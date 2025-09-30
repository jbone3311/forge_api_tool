#!/usr/bin/env python3
"""
Batch Operations Manager

Handles batch operations for configurations, wildcards, and image generation.
"""

import json
import os
import tempfile
import zipfile
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class BatchOperation:
    """Represents a single batch operation."""
    
    def __init__(self, operation_id: str, operation_type: str, items: List[str], 
                 callback: Optional[Callable] = None):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.items = items
        self.callback = callback
        self.status = "pending"
        self.progress = 0
        self.total_items = len(items)
        self.completed_items = 0
        self.failed_items = 0
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        self.created_at = time.time()
    
    def update_progress(self, completed: int, failed: int = 0):
        """Update operation progress."""
        self.completed_items = completed
        self.failed_items = failed
        self.progress = (completed + failed) / self.total_items * 100 if self.total_items > 0 else 0
        
        if completed + failed >= self.total_items:
            self.status = "completed" if failed == 0 else "completed_with_errors"
            self.end_time = time.time()
    
    def add_result(self, item: str, success: bool, result: Any = None, error: str = None):
        """Add a result for an item."""
        self.results.append({
            'item': item,
            'success': success,
            'result': result,
            'error': error,
            'timestamp': time.time()
        })
        
        if not success:
            self.errors.append({
                'item': item,
                'error': error,
                'timestamp': time.time()
            })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operation summary."""
        duration = None
        if self.start_time:
            end_time = self.end_time or time.time()
            duration = end_time - self.start_time
        
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type,
            'status': self.status,
            'progress': self.progress,
            'total_items': self.total_items,
            'completed_items': self.completed_items,
            'failed_items': self.failed_items,
            'duration': duration,
            'created_at': self.created_at,
            'start_time': self.start_time,
            'end_time': self.end_time
        }


class BatchManager:
    """Manages batch operations for the application."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize batch manager.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.operations: Dict[str, BatchOperation] = {}
        self._lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def create_operation(self, operation_type: str, items: List[str], 
                        callback: Optional[Callable] = None) -> str:
        """Create a new batch operation."""
        operation_id = f"{operation_type}_{int(time.time())}_{len(items)}"
        
        with self._lock:
            operation = BatchOperation(operation_id, operation_type, items, callback)
            self.operations[operation_id] = operation
        
        return operation_id
    
    def start_operation(self, operation_id: str, process_func: Callable):
        """Start a batch operation."""
        with self._lock:
            if operation_id not in self.operations:
                raise ValueError(f"Operation {operation_id} not found")
            
            operation = self.operations[operation_id]
            if operation.status != "pending":
                raise ValueError(f"Operation {operation_id} is not pending")
            
            operation.status = "running"
            operation.start_time = time.time()
        
        # Submit to executor
        self.executor.submit(self._run_operation, operation_id, process_func)
    
    def _run_operation(self, operation_id: str, process_func: Callable):
        """Run a batch operation."""
        with self._lock:
            operation = self.operations[operation_id]
        
        completed = 0
        failed = 0
        
        try:
            # Process items in parallel
            with ThreadPoolExecutor(max_workers=min(self.max_workers, operation.total_items)) as executor:
                future_to_item = {
                    executor.submit(process_func, item): item 
                    for item in operation.items
                }
                
                for future in as_completed(future_to_item):
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        operation.add_result(item, True, result)
                        completed += 1
                    except Exception as e:
                        operation.add_result(item, False, error=str(e))
                        failed += 1
                    
                    operation.update_progress(completed, failed)
                    
                    # Call callback if provided
                    if operation.callback:
                        try:
                            operation.callback(operation)
                        except Exception as e:
                            print(f"Callback error for operation {operation_id}: {e}")
        
        except Exception as e:
            with self._lock:
                operation.status = "failed"
                operation.errors.append({
                    'error': f"Operation failed: {str(e)}",
                    'timestamp': time.time()
                })
    
    def get_operation(self, operation_id: str) -> Optional[BatchOperation]:
        """Get an operation by ID."""
        with self._lock:
            return self.operations.get(operation_id)
    
    def get_all_operations(self) -> List[Dict[str, Any]]:
        """Get all operations with their summaries."""
        with self._lock:
            return [op.get_summary() for op in self.operations.values()]
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a running operation."""
        with self._lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            if operation.status == "running":
                operation.status = "cancelled"
                operation.end_time = time.time()
                return True
            
            return False
    
    def delete_operation(self, operation_id: str) -> bool:
        """Delete an operation."""
        with self._lock:
            if operation_id in self.operations:
                del self.operations[operation_id]
                return True
            return False
    
    def cleanup_completed_operations(self, older_than_hours: int = 24) -> int:
        """Clean up completed operations older than specified hours."""
        cutoff_time = time.time() - (older_than_hours * 3600)
        deleted_count = 0
        
        with self._lock:
            to_delete = [
                op_id for op_id, op in self.operations.items()
                if op.status in ["completed", "completed_with_errors", "failed", "cancelled"]
                and op.end_time and op.end_time < cutoff_time
            ]
            
            for op_id in to_delete:
                del self.operations[op_id]
                deleted_count += 1
        
        return deleted_count
    
    def shutdown(self):
        """Shutdown the batch manager."""
        self.executor.shutdown(wait=True)


# Global batch manager instance
_batch_manager = None


def get_batch_manager() -> BatchManager:
    """Get the global batch manager instance."""
    global _batch_manager
    if _batch_manager is None:
        _batch_manager = BatchManager()
    return _batch_manager


class BatchOperations:
    """High-level batch operations for the application."""
    
    def __init__(self):
        self.batch_manager = get_batch_manager()
    
    def batch_export_configs(self, config_names: List[str], output_path: str) -> str:
        """Export multiple configurations to a zip file."""
        def export_config(config_name):
            # This would integrate with your config service
            # For now, return a placeholder
            return {"config_name": config_name, "exported": True}
        
        operation_id = self.batch_manager.create_operation("export_configs", config_names)
        self.batch_manager.start_operation(operation_id, export_config)
        return operation_id
    
    def batch_import_configs(self, file_paths: List[str]) -> str:
        """Import multiple configuration files."""
        def import_config(file_path):
            # This would integrate with your config service
            # For now, return a placeholder
            return {"file_path": file_path, "imported": True}
        
        operation_id = self.batch_manager.create_operation("import_configs", file_paths)
        self.batch_manager.start_operation(operation_id, import_config)
        return operation_id
    
    def batch_process_wildcards(self, wildcard_files: List[str]) -> str:
        """Process multiple wildcard files."""
        def process_wildcard_file(file_path):
            # This would integrate with your wildcard manager
            # For now, return a placeholder
            return {"file_path": file_path, "processed": True}
        
        operation_id = self.batch_manager.create_operation("process_wildcards", wildcard_files)
        self.batch_manager.start_operation(operation_id, process_wildcard_file)
        return operation_id
    
    def batch_generate_images(self, prompts: List[str], config_name: str) -> str:
        """Generate multiple images from prompts."""
        def generate_image(prompt):
            # This would integrate with your generation service
            # For now, return a placeholder
            return {"prompt": prompt, "generated": True}
        
        operation_id = self.batch_manager.create_operation("generate_images", prompts)
        self.batch_manager.start_operation(operation_id, generate_image)
        return operation_id


# Global batch operations instance
_batch_operations = None


def get_batch_operations() -> BatchOperations:
    """Get the global batch operations instance."""
    global _batch_operations
    if _batch_operations is None:
        _batch_operations = BatchOperations()
    return _batch_operations

