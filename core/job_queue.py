import json
import os
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import uuid
import logging


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class Job:
    """Represents a single job in the queue with enhanced features."""
    
    def __init__(self, config_name: str, batch_size: int = None, num_batches: int = None, priority: JobPriority = JobPriority.NORMAL):
        self.id = self._generate_id()
        self.config_name = config_name
        self.batch_size = batch_size
        self.num_batches = num_batches
        self.priority = priority
        self.status = JobStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.current_batch = 0
        self.current_image = 0
        self.total_images = 0
        self.completed_images = 0
        self.failed_images = 0
        self.errors = []
        self.output_files = []
        self.progress_callback = None
        self.prompts = []  # Store pre-generated prompts
        self.retry_count = 0
        self.max_retries = 3
        self.last_error = None
        self.estimated_duration = None
        self.actual_duration = None
        
    def _generate_id(self) -> str:
        """Generate a unique job ID."""
        return str(uuid.uuid4())
    
    def start(self):
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now().isoformat()
        self.last_error = None
    
    def complete(self):
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        if self.started_at:
            start_time = datetime.fromisoformat(self.started_at)
            end_time = datetime.fromisoformat(self.completed_at)
            self.actual_duration = (end_time - start_time).total_seconds()
    
    def fail(self, error: str):
        """Mark job as failed."""
        self.last_error = error
        self.errors.append(error)
        
        if self.retry_count < self.max_retries:
            self.status = JobStatus.RETRYING
            self.retry_count += 1
            logging.warning(f"Job {self.id} failed, retrying ({self.retry_count}/{self.max_retries}): {error}")
        else:
            self.status = JobStatus.FAILED
            self.completed_at = datetime.now().isoformat()
            logging.error(f"Job {self.id} failed permanently after {self.max_retries} retries: {error}")
    
    def cancel(self):
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now().isoformat()
    
    def retry(self):
        """Retry a failed job."""
        if self.status == JobStatus.FAILED and self.retry_count < self.max_retries:
            self.status = JobStatus.PENDING
            self.retry_count += 1
            self.errors = self.errors[:-1] if self.errors else []  # Remove last error
            self.last_error = None
            return True
        return False
    
    def update_progress(self, current_batch: int, current_image: int, total_images: int):
        """Update job progress."""
        self.current_batch = current_batch
        self.current_image = current_image
        self.total_images = total_images
        self.completed_images = current_image
        
        # Estimate remaining time
        if self.started_at and self.completed_images > 0:
            elapsed = (datetime.now() - datetime.fromisoformat(self.started_at)).total_seconds()
            if self.completed_images > 0:
                rate = self.completed_images / elapsed
                remaining = (self.total_images - self.completed_images) / rate if rate > 0 else 0
                self.estimated_duration = elapsed + remaining
        
        if self.progress_callback:
            self.progress_callback(self)
    
    def add_output_file(self, file_path: str):
        """Add an output file to the job."""
        self.output_files.append(file_path)
    
    def add_error(self, error: str):
        """Add an error to the job."""
        self.errors.append(error)
        self.last_error = error
    
    def get_progress_percentage(self) -> float:
        """Get progress as a percentage."""
        if self.total_images == 0:
            return 0.0
        return (self.completed_images / self.total_images) * 100
    
    def get_elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds."""
        if not self.started_at:
            return None
        return (datetime.now() - datetime.fromisoformat(self.started_at)).total_seconds()
    
    def get_estimated_remaining_time(self) -> Optional[float]:
        """Get estimated remaining time in seconds."""
        if self.estimated_duration and self.started_at:
            elapsed = self.get_elapsed_time()
            if elapsed:
                return max(0, self.estimated_duration - elapsed)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        return {
            'id': self.id,
            'config_name': self.config_name,
            'batch_size': self.batch_size,
            'num_batches': self.num_batches,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'current_batch': self.current_batch,
            'current_image': self.current_image,
            'total_images': self.total_images,
            'completed_images': self.completed_images,
            'failed_images': self.failed_images,
            'errors': self.errors,
            'output_files': self.output_files,
            'prompts': self.prompts,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'last_error': self.last_error,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create job from dictionary."""
        priority = JobPriority(data.get('priority', JobPriority.NORMAL.value))
        job = cls(data['config_name'], data.get('batch_size'), data.get('num_batches'), priority)
        job.id = data['id']
        job.status = JobStatus(data['status'])
        job.created_at = data['created_at']
        job.started_at = data.get('started_at')
        job.completed_at = data.get('completed_at')
        job.current_batch = data.get('current_batch', 0)
        job.current_image = data.get('current_image', 0)
        job.total_images = data.get('total_images', 0)
        job.completed_images = data.get('completed_images', 0)
        job.failed_images = data.get('failed_images', 0)
        job.errors = data.get('errors', [])
        job.output_files = data.get('output_files', [])
        job.prompts = data.get('prompts', [])
        job.retry_count = data.get('retry_count', 0)
        job.max_retries = data.get('max_retries', 3)
        job.last_error = data.get('last_error')
        job.estimated_duration = data.get('estimated_duration')
        job.actual_duration = data.get('actual_duration')
        return job


class JobQueue:
    """Manages a queue of jobs with enhanced features including prioritization and persistence."""
    
    def __init__(self, queue_file: str = "queue.json"):
        self.queue_file = queue_file
        self.jobs: List[Job] = []
        self.current_job: Optional[Job] = None
        self.running = False
        self.lock = threading.Lock()
        self.processing_callbacks: List[Callable[[Job], None]] = []
        self.load_queue()
        self._sort_jobs_by_priority()
    
    def add_job(self, config_name: str, batch_size: int = None, num_batches: int = None, priority: JobPriority = JobPriority.NORMAL) -> Job:
        """Add a new job to the queue with priority."""
        with self.lock:
            job = Job(config_name, batch_size, num_batches, priority)
            self.jobs.append(job)
            self._sort_jobs_by_priority()
            self.save_queue()
            self._notify_processing_callbacks(job)
            return job
    
    def add_job_with_prompts(self, config: Dict[str, Any], prompts: List[str], priority: JobPriority = JobPriority.NORMAL) -> Job:
        """Add a new job to the queue with pre-generated prompts."""
        with self.lock:
            config_name = config.get('name', 'unknown')
            batch_size = len(prompts)
            num_batches = 1
            
            job = Job(config_name, batch_size, num_batches, priority)
            job.prompts = prompts  # Store the pre-generated prompts
            job.total_images = len(prompts)
            self.jobs.append(job)
            self._sort_jobs_by_priority()
            self.save_queue()
            self._notify_processing_callbacks(job)
            return job
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a job from the queue."""
        with self.lock:
            for i, job in enumerate(self.jobs):
                if job.id == job_id:
                    if job.status == JobStatus.RUNNING:
                        job.cancel()
                    else:
                        self.jobs.pop(i)
                    self.save_queue()
                    return True
            return False
    
    def retry_job(self, job_id: str) -> bool:
        """Retry a failed job."""
        with self.lock:
            job = self.get_job(job_id)
            if job and job.retry():
                self._sort_jobs_by_priority()
                self.save_queue()
                self._notify_processing_callbacks(job)
                return True
            return False
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        for job in self.jobs:
            if job.id == job_id:
                return job
        return None
    
    def get_pending_jobs(self) -> List[Job]:
        """Get all pending jobs."""
        return [job for job in self.jobs if job.status == JobStatus.PENDING]
    
    def get_running_job(self) -> Optional[Job]:
        """Get the currently running job."""
        return self.current_job
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs."""
        return self.jobs.copy()
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get jobs by status."""
        return [job for job in self.jobs if job.status == status]
    
    def get_jobs_by_priority(self, priority: JobPriority) -> List[Job]:
        """Get jobs by priority."""
        return [job for job in self.jobs if job.priority == priority]
    
    def _sort_jobs_by_priority(self):
        """Sort jobs by priority (highest first) and creation time."""
        self.jobs.sort(key=lambda job: (-job.priority.value, job.created_at))
    
    def _notify_processing_callbacks(self, job: Job):
        """Notify all processing callbacks about a job change."""
        for callback in self.processing_callbacks:
            try:
                callback(job)
            except Exception as e:
                logging.error(f"Error in processing callback: {e}")
    
    def add_processing_callback(self, callback: Callable[[Job], None]):
        """Add a callback to be notified when jobs are processed."""
        self.processing_callbacks.append(callback)
    
    def remove_processing_callback(self, callback: Callable[[Job], None]):
        """Remove a processing callback."""
        if callback in self.processing_callbacks:
            self.processing_callbacks.remove(callback)
    
    def start_next_job(self) -> Optional[Job]:
        """Start the next pending job."""
        with self.lock:
            if self.current_job and self.current_job.status == JobStatus.RUNNING:
                return None  # Already running a job
            
            pending_jobs = self.get_pending_jobs()
            if not pending_jobs:
                return None
            
            self.current_job = pending_jobs[0]
            self.current_job.start()
            self.save_queue()
            self._notify_processing_callbacks(self.current_job)
            return self.current_job
    
    def complete_current_job(self):
        """Mark the current job as completed."""
        with self.lock:
            if self.current_job:
                self.current_job.complete()
                self._notify_processing_callbacks(self.current_job)
                self.current_job = None
                self.save_queue()
    
    def fail_current_job(self, error: str):
        """Mark the current job as failed."""
        with self.lock:
            if self.current_job:
                self.current_job.fail(error)
                self._notify_processing_callbacks(self.current_job)
                if self.current_job.status == JobStatus.FAILED:
                    self.current_job = None
                self.save_queue()
    
    def cancel_current_job(self):
        """Cancel the current job."""
        with self.lock:
            if self.current_job:
                self.current_job.cancel()
                self._notify_processing_callbacks(self.current_job)
                self.current_job = None
                self.save_queue()
    
    def update_current_job_progress(self, current_batch: int, current_image: int, total_images: int):
        """Update progress of the current job."""
        if self.current_job:
            self.current_job.update_progress(current_batch, current_image, total_images)
            self.save_queue()
    
    def add_current_job_output(self, file_path: str):
        """Add output file to current job."""
        if self.current_job:
            self.current_job.add_output_file(file_path)
            self.save_queue()
    
    def add_current_job_error(self, error: str):
        """Add error to current job."""
        if self.current_job:
            self.current_job.add_error(error)
            self.save_queue()
    
    def clear_completed_jobs(self):
        """Remove completed and failed jobs from the queue."""
        with self.lock:
            initial_count = len(self.jobs)
            self.jobs = [job for job in self.jobs if job.status == JobStatus.PENDING or job.status == JobStatus.RUNNING or job.status == JobStatus.RETRYING]
            cleared_count = initial_count - len(self.jobs)
            self.save_queue()
            return cleared_count
    
    def clear_all_jobs(self):
        """Clear all jobs from the queue."""
        with self.lock:
            if self.current_job:
                self.current_job.cancel()
            cleared_count = len(self.jobs)
            self.jobs = []
            self.current_job = None
            self.save_queue()
            return cleared_count
    
    def clear_queue(self):
        """Clear all jobs from the queue (alias for clear_all_jobs)."""
        return self.clear_all_jobs()
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the queue."""
        total_jobs = len(self.jobs)
        pending_jobs = len([j for j in self.jobs if j.status == JobStatus.PENDING])
        running_jobs = len([j for j in self.jobs if j.status == JobStatus.RUNNING])
        retrying_jobs = len([j for j in self.jobs if j.status == JobStatus.RETRYING])
        completed_jobs = len([j for j in self.jobs if j.status == JobStatus.COMPLETED])
        failed_jobs = len([j for j in self.jobs if j.status == JobStatus.FAILED])
        cancelled_jobs = len([j for j in self.jobs if j.status == JobStatus.CANCELLED])
        
        total_images = sum(j.total_images for j in self.jobs if j.total_images > 0)
        completed_images = sum(j.completed_images for j in self.jobs)
        failed_images = sum(j.failed_images for j in self.jobs)
        
        # Priority breakdown
        priority_stats = {}
        for priority in JobPriority:
            priority_stats[priority.name] = len([j for j in self.jobs if j.priority == priority])
        
        # Average processing time
        completed_jobs_with_duration = [j for j in self.jobs if j.actual_duration is not None]
        avg_duration = sum(j.actual_duration for j in completed_jobs_with_duration) / len(completed_jobs_with_duration) if completed_jobs_with_duration else 0
        
        return {
            'total_jobs': total_jobs,
            'pending_jobs': pending_jobs,
            'running_jobs': running_jobs,
            'retrying_jobs': retrying_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'cancelled_jobs': cancelled_jobs,
            'total_images': total_images,
            'completed_images': completed_images,
            'failed_images': failed_images,
            'priority_stats': priority_stats,
            'average_duration': avg_duration,
            'current_job': self.current_job.to_dict() if self.current_job else None
        }
    
    def save_queue(self):
        """Save queue to file with error handling."""
        try:
            data = {
                'jobs': [job.to_dict() for job in self.jobs],
                'current_job_id': self.current_job.id if self.current_job else None,
                'last_updated': datetime.now().isoformat(),
                'version': '2.0'  # Version for future compatibility
            }
            
            # Create backup of existing file
            if os.path.exists(self.queue_file):
                backup_file = f"{self.queue_file}.backup"
                try:
                    import shutil
                    shutil.copy2(self.queue_file, backup_file)
                except Exception as e:
                    logging.warning(f"Failed to create backup of queue file: {e}")
            
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving queue: {e}")
            raise
    
    def load_queue(self):
        """Load queue from file with error handling and migration."""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle version migration
                version = data.get('version', '1.0')
                if version == '1.0':
                    # Migrate old format to new format
                    self._migrate_v1_to_v2(data)
                else:
                    self.jobs = [Job.from_dict(job_data) for job_data in data.get('jobs', [])]
                
                current_job_id = data.get('current_job_id')
                if current_job_id:
                    self.current_job = self.get_job(current_job_id)
                    
        except Exception as e:
            logging.error(f"Error loading queue: {e}")
            self.jobs = []
            self.current_job = None
    
    def _migrate_v1_to_v2(self, data: Dict[str, Any]):
        """Migrate queue data from version 1.0 to 2.0."""
        try:
            self.jobs = []
            for job_data in data.get('jobs', []):
                # Add missing fields for v2.0
                job_data.setdefault('priority', JobPriority.NORMAL.value)
                job_data.setdefault('retry_count', 0)
                job_data.setdefault('max_retries', 3)
                job_data.setdefault('last_error', None)
                job_data.setdefault('estimated_duration', None)
                job_data.setdefault('actual_duration', None)
                
                self.jobs.append(Job.from_dict(job_data))
            
            logging.info("Successfully migrated queue from v1.0 to v2.0")
        except Exception as e:
            logging.error(f"Error during queue migration: {e}")
            self.jobs = []
    
    def set_progress_callback(self, job_id: str, callback: Callable[[Job], None]):
        """Set a progress callback for a specific job."""
        job = self.get_job(job_id)
        if job:
            job.progress_callback = callback
    
    def process_next_job(self) -> Optional[Job]:
        """Process the next job in the queue (alias for start_next_job for compatibility)."""
        return self.start_next_job()
    
    def get_status(self) -> Dict[str, Any]:
        """Get queue status (alias for get_queue_stats for compatibility)."""
        return self.get_queue_stats()


# Create a global instance for easy importing
job_queue = JobQueue() 