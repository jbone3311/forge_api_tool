import json
import os
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import threading
import uuid


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    """Represents a single job in the queue."""
    
    def __init__(self, config_name: str, batch_size: int = None, num_batches: int = None):
        self.id = self._generate_id()
        self.config_name = config_name
        self.batch_size = batch_size
        self.num_batches = num_batches
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
        
    def _generate_id(self) -> str:
        """Generate a unique job ID."""
        return str(uuid.uuid4())
    
    def start(self):
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now().isoformat()
    
    def complete(self):
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
    
    def fail(self, error: str):
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now().isoformat()
        self.errors.append(error)
    
    def cancel(self):
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now().isoformat()
    
    def update_progress(self, current_batch: int, current_image: int, total_images: int):
        """Update job progress."""
        self.current_batch = current_batch
        self.current_image = current_image
        self.total_images = total_images
        self.completed_images = current_image
        
        if self.progress_callback:
            self.progress_callback(self)
    
    def add_output_file(self, file_path: str):
        """Add an output file to the job."""
        self.output_files.append(file_path)
    
    def add_error(self, error: str):
        """Add an error to the job."""
        self.errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        return {
            'id': self.id,
            'config_name': self.config_name,
            'batch_size': self.batch_size,
            'num_batches': self.num_batches,
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
            'prompts': self.prompts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create job from dictionary."""
        job = cls(data['config_name'], data.get('batch_size'), data.get('num_batches'))
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
        return job


class JobQueue:
    """Manages a queue of jobs with persistence."""
    
    def __init__(self, queue_file: str = "queue.json"):
        self.queue_file = queue_file
        self.jobs: List[Job] = []
        self.current_job: Optional[Job] = None
        self.running = False
        self.lock = threading.Lock()
        self.load_queue()
    
    def add_job(self, config_name: str, batch_size: int = None, num_batches: int = None) -> Job:
        """Add a new job to the queue."""
        with self.lock:
            job = Job(config_name, batch_size, num_batches)
            self.jobs.append(job)
            self.save_queue()
            return job
    
    def add_job_with_prompts(self, config: Dict[str, Any], prompts: List[str]) -> Job:
        """Add a new job to the queue with pre-generated prompts."""
        with self.lock:
            config_name = config.get('name', 'unknown')
            batch_size = len(prompts)
            num_batches = 1
            
            job = Job(config_name, batch_size, num_batches)
            job.prompts = prompts  # Store the pre-generated prompts
            job.total_images = len(prompts)
            self.jobs.append(job)
            self.save_queue()
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
            return self.current_job
    
    def complete_current_job(self):
        """Mark the current job as completed."""
        with self.lock:
            if self.current_job:
                self.current_job.complete()
                self.current_job = None
                self.save_queue()
    
    def fail_current_job(self, error: str):
        """Mark the current job as failed."""
        with self.lock:
            if self.current_job:
                self.current_job.fail(error)
                self.current_job = None
                self.save_queue()
    
    def cancel_current_job(self):
        """Cancel the current job."""
        with self.lock:
            if self.current_job:
                self.current_job.cancel()
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
            self.jobs = [job for job in self.jobs if job.status == JobStatus.PENDING or job.status == JobStatus.RUNNING]
            self.save_queue()
    
    def clear_all_jobs(self):
        """Clear all jobs from the queue."""
        with self.lock:
            if self.current_job:
                self.current_job.cancel()
            self.jobs = []
            self.current_job = None
            self.save_queue()
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the queue."""
        total_jobs = len(self.jobs)
        pending_jobs = len([j for j in self.jobs if j.status == JobStatus.PENDING])
        running_jobs = len([j for j in self.jobs if j.status == JobStatus.RUNNING])
        completed_jobs = len([j for j in self.jobs if j.status == JobStatus.COMPLETED])
        failed_jobs = len([j for j in self.jobs if j.status == JobStatus.FAILED])
        cancelled_jobs = len([j for j in self.jobs if j.status == JobStatus.CANCELLED])
        
        total_images = sum(j.total_images for j in self.jobs if j.total_images > 0)
        completed_images = sum(j.completed_images for j in self.jobs)
        failed_images = sum(j.failed_images for j in self.jobs)
        
        return {
            'total_jobs': total_jobs,
            'pending_jobs': pending_jobs,
            'running_jobs': running_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'cancelled_jobs': cancelled_jobs,
            'total_images': total_images,
            'completed_images': completed_images,
            'failed_images': failed_images,
            'current_job': self.current_job.to_dict() if self.current_job else None
        }
    
    def save_queue(self):
        """Save queue to file."""
        try:
            data = {
                'jobs': [job.to_dict() for job in self.jobs],
                'current_job_id': self.current_job.id if self.current_job else None,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving queue: {e}")
    
    def load_queue(self):
        """Load queue from file."""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.jobs = [Job.from_dict(job_data) for job_data in data.get('jobs', [])]
                
                current_job_id = data.get('current_job_id')
                if current_job_id:
                    self.current_job = self.get_job(current_job_id)
        except Exception as e:
            print(f"Error loading queue: {e}")
            self.jobs = []
            self.current_job = None
    
    def set_progress_callback(self, job_id: str, callback: Callable[[Job], None]):
        """Set a progress callback for a specific job."""
        job = self.get_job(job_id)
        if job:
            job.progress_callback = callback


# Create a global instance for easy importing
job_queue = JobQueue() 