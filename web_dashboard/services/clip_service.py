#!/usr/bin/env python3
"""
CLIP Service

Service layer for CLIP Processor in the web dashboard.
Handles job queuing, progress tracking, and UI integration.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from core.clip_processor import CLIPProcessor
from core.centralized_logger import logger


class CLIPService:
    """Service for handling CLIP processing in the web dashboard."""
    
    def __init__(self, app_context):
        """
        Initialize CLIP service.
        
        Args:
            app_context: Application context containing dependencies
        """
        self.context = app_context
        self.processor = None
        self._initialize_processor()
        
        logger.log_app_event("clip_service_initialized", {
            "service": "CLIPService"
        })
    
    def _initialize_processor(self):
        """Initialize the CLIP processor."""
        try:
            # Get API URL from context or config
            api_url = "http://127.0.0.1:7860"  # Default A1111 URL
            output_dir = "wildcards/clip_generated"
            
            self.processor = CLIPProcessor(
                api_url=api_url,
                output_dir=output_dir
            )
        except Exception as e:
            logger.error(f"Error initializing CLIP processor: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to CLIP API.
        
        Returns:
            Dictionary with connection status
        """
        if not self.processor:
            return {
                'connected': False,
                'error': 'CLIP processor not initialized'
            }
        
        try:
            connected = self.processor.test_connection()
            
            if connected:
                installed, msg = self.processor.check_clip_interrogator_installed()
                return {
                    'connected': True,
                    'extension_installed': installed,
                    'message': msg
                }
            else:
                return {
                    'connected': False,
                    'error': 'Cannot connect to Automatic1111 API'
                }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    def process_directory(self,
                         input_dir: str,
                         modes: Optional[List[str]] = None,
                         theme_name: Optional[str] = None,
                         recursive: bool = True) -> Dict[str, Any]:
        """
        Process images in a directory.
        
        Args:
            input_dir: Directory containing images
            modes: List of CLIP modes to use
            theme_name: Override theme name
            recursive: Process subdirectories as themes
            
        Returns:
            Processing results dictionary
        """
        if not self.processor:
            return {
                'success': False,
                'error': 'CLIP processor not initialized'
            }
        
        try:
            # Add to job queue for async processing
            job_data = {
                'type': 'clip_process',
                'input_dir': input_dir,
                'modes': modes or CLIPProcessor.MODES,
                'theme_name': theme_name,
                'recursive': recursive,
                'status': 'pending'
            }
            
            # Add job to context
            job_id = self.context.add_job(job_data)
            
            # Process synchronously for now (can be moved to background worker)
            def progress_callback(current, total, status):
                # Update job progress
                job_data['status'] = status
                job_data['progress'] = {
                    'current': current,
                    'total': total,
                    'percentage': int((current / total) * 100) if total > 0 else 0
                }
                self.context.update_job(job_id, job_data)
            
            results = self.processor.process_directory(
                input_dir=input_dir,
                modes=modes,
                theme_name=theme_name,
                recursive=recursive,
                progress_callback=progress_callback
            )
            
            # Update job with final results
            job_data['status'] = 'completed' if results['success'] else 'failed'
            job_data['results'] = results
            self.context.update_job(job_id, job_data)
            
            results['job_id'] = job_id
            return results
            
        except Exception as e:
            logger.error(f"Error processing directory: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about generated wildcards."""
        if not self.processor:
            return {}
        
        try:
            return self.processor.get_processing_stats()
        except Exception as e:
            logger.error(f"Error getting CLIP stats: {e}")
            return {}
    
    def get_available_modes(self) -> List[str]:
        """Get list of available CLIP modes."""
        return CLIPProcessor.MODES
    
    def get_generated_wildcards(self) -> List[Dict[str, Any]]:
        """
        Get list of generated wildcard files.
        
        Returns:
            List of wildcard file info dictionaries
        """
        if not self.processor:
            return []
        
        wildcards = []
        output_dir = Path(self.processor.output_dir)
        
        if not output_dir.exists():
            return []
        
        for wildcard_file in sorted(output_dir.glob('*.txt')):
            try:
                # Parse filename
                name_parts = wildcard_file.stem.rsplit('_', 1)
                if len(name_parts) == 2:
                    theme, mode = name_parts
                else:
                    theme = wildcard_file.stem
                    mode = 'unknown'
                
                # Count tags
                with open(wildcard_file, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                
                wildcards.append({
                    'filename': wildcard_file.name,
                    'theme': theme,
                    'mode': mode,
                    'tag_count': len(lines),
                    'file_path': str(wildcard_file),
                    'preview': lines[:10] if lines else []
                })
            except Exception as e:
                logger.error(f"Error reading wildcard {wildcard_file}: {e}")
        
        return wildcards
