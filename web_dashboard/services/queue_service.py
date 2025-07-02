"""
Queue service for the Flask web dashboard.

This module provides business logic for job queue operations,
separating it from the HTTP route handlers.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, List, Optional, Any
from core.exceptions import (
    JobQueueError, ValidationError, ConfigurationError
)
from web_dashboard.utils.validators import validate_job_id


class QueueService:
    """
    Service class for job queue operations.
    """
    
    def __init__(self, 
                 job_queue_instance,
                 logger_instance):
        """
        Initialize the queue service.
        
        Args:
            job_queue_instance: Instance of job queue
            logger_instance: Instance of logger
        """
        self.job_queue = job_queue_instance
        self.logger = logger_instance
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get detailed queue status with enhanced statistics.
        
        Returns:
            Dictionary with queue status information
            
        Raises:
            JobQueueError: If queue operation fails
        """
        try:
            stats = self.job_queue.get_queue_stats()
            return stats
        except Exception as e:
            self.logger.log_error(f"Error getting queue status: {e}")
            raise JobQueueError(f"Failed to get queue status: {e}")
    
    def get_all_jobs(self) -> Dict[str, Any]:
        """
        Get all jobs in the queue with detailed information.
        
        Returns:
            Dictionary with jobs and total count
            
        Raises:
            JobQueueError: If queue operation fails
        """
        try:
            jobs = self.job_queue.get_all_jobs()
            return {
                'jobs': [job.to_dict() for job in jobs],
                'total': len(jobs)
            }
        except Exception as e:
            self.logger.log_error(f"Error getting queue jobs: {e}")
            raise JobQueueError(f"Failed to get queue jobs: {e}")
    
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific job.
        
        Args:
            job_id: ID of the job to retrieve
            
        Returns:
            Dictionary with job details
            
        Raises:
            ValidationError: If job_id is invalid
            JobQueueError: If job not found or operation fails
        """
        try:
            # Validate job_id
            validate_job_id(job_id)
            
            job = self.job_queue.get_job(job_id)
            if job:
                return job.to_dict()
            else:
                raise JobQueueError(f"Job '{job_id}' not found")
        except ValidationError:
            # Re-raise validation errors
            raise
        except JobQueueError:
            # Re-raise job queue errors
            raise
        except Exception as e:
            self.logger.log_error(f"Error getting job details: {e}")
            raise JobQueueError(f"Failed to get job details: {e}")
    
    def retry_job(self, job_id: str) -> Dict[str, Any]:
        """
        Retry a failed job.
        
        Args:
            job_id: ID of the job to retry
            
        Returns:
            Dictionary with retry result
            
        Raises:
            ValidationError: If job_id is invalid
            JobQueueError: If job cannot be retried or operation fails
        """
        try:
            # Validate job_id
            validate_job_id(job_id)
            
            success = self.job_queue.retry_job(job_id)
            if success:
                return {'message': 'Job queued for retry'}
            else:
                raise JobQueueError(f"Job '{job_id}' cannot be retried")
        except ValidationError:
            # Re-raise validation errors
            raise
        except JobQueueError:
            # Re-raise job queue errors
            raise
        except Exception as e:
            self.logger.log_error(f"Error retrying job: {e}")
            raise JobQueueError(f"Failed to retry job: {e}")
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a specific job.
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            Dictionary with cancellation result
            
        Raises:
            ValidationError: If job_id is invalid
            JobQueueError: If job not found or cannot be cancelled
        """
        try:
            # Validate job_id
            validate_job_id(job_id)
            
            success = self.job_queue.remove_job(job_id)
            if success:
                return {'message': 'Job cancelled'}
            else:
                raise JobQueueError(f"Job '{job_id}' not found or cannot be cancelled")
        except ValidationError:
            # Re-raise validation errors
            raise
        except JobQueueError:
            # Re-raise job queue errors
            raise
        except Exception as e:
            self.logger.log_error(f"Error cancelling job: {e}")
            raise JobQueueError(f"Failed to cancel job: {e}")
    
    def clear_all_jobs(self) -> Dict[str, Any]:
        """
        Clear all jobs from the queue.
        
        Returns:
            Dictionary with clear result
            
        Raises:
            JobQueueError: If queue operation fails
        """
        try:
            cleared_count = self.job_queue.clear_all_jobs()
            return {
                'message': f'Cleared {cleared_count} jobs from queue',
                'cleared_count': cleared_count
            }
        except Exception as e:
            self.logger.log_error(f"Error clearing queue: {e}")
            raise JobQueueError(f"Failed to clear queue: {e}")
    
    def clear_completed_jobs(self) -> Dict[str, Any]:
        """
        Clear only completed and failed jobs from the queue.
        
        Returns:
            Dictionary with clear result
            
        Raises:
            JobQueueError: If queue operation fails
        """
        try:
            cleared_count = self.job_queue.clear_completed_jobs()
            return {
                'message': f'Cleared {cleared_count} completed/failed jobs',
                'cleared_count': cleared_count
            }
        except Exception as e:
            self.logger.log_error(f"Error clearing completed jobs: {e}")
            raise JobQueueError(f"Failed to clear completed jobs: {e}")
    
    def get_priority_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics broken down by priority.
        
        Returns:
            Dictionary with priority statistics
            
        Raises:
            JobQueueError: If queue operation fails
        """
        try:
            stats = self.job_queue.get_queue_stats()
            priority_stats = stats.get('priority_stats', {})
            
            # Add detailed priority breakdown
            detailed_stats = {}
            for priority_name, count in priority_stats.items():
                jobs = self.job_queue.get_jobs_by_priority(
                    getattr(self.job_queue.JobPriority, priority_name)
                )
                detailed_stats[priority_name] = {
                    'count': count,
                    'pending': len([j for j in jobs if j.status == self.job_queue.JobStatus.PENDING]),
                    'running': len([j for j in jobs if j.status == self.job_queue.JobStatus.RUNNING]),
                    'completed': len([j for j in jobs if j.status == self.job_queue.JobStatus.COMPLETED]),
                    'failed': len([j for j in jobs if j.status == self.job_queue.JobStatus.FAILED]),
                    'retrying': len([j for j in jobs if j.status == self.job_queue.JobStatus.RETRYING])
                }
            
            return detailed_stats
        except Exception as e:
            self.logger.log_error(f"Error getting priority stats: {e}")
            raise JobQueueError(f"Failed to get priority stats: {e}")
    
    def get_job_by_id(self, job_id: str):
        """
        Get a job object by ID.
        
        Args:
            job_id: ID of the job to retrieve
            
        Returns:
            Job object or None if not found
            
        Raises:
            ValidationError: If job_id is invalid
        """
        try:
            # Validate job_id
            validate_job_id(job_id)
            
            return self.job_queue.get_job(job_id)
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            self.logger.log_error(f"Error getting job by ID: {e}")
            raise JobQueueError(f"Failed to get job by ID: {e}")
    
    def get_jobs_by_status(self, status):
        """
        Get all jobs with a specific status.
        
        Args:
            status: Job status to filter by
            
        Returns:
            List of jobs with the specified status
        """
        try:
            all_jobs = self.job_queue.get_all_jobs()
            return [job for job in all_jobs if job.status == status]
        except Exception as e:
            self.logger.log_error(f"Error getting jobs by status: {e}")
            raise JobQueueError(f"Failed to get jobs by status: {e}")
    
    def get_jobs_by_priority(self, priority):
        """
        Get all jobs with a specific priority.
        
        Args:
            priority: Job priority to filter by
            
        Returns:
            List of jobs with the specified priority
        """
        try:
            return self.job_queue.get_jobs_by_priority(priority)
        except Exception as e:
            self.logger.log_error(f"Error getting jobs by priority: {e}")
            raise JobQueueError(f"Failed to get jobs by priority: {e}")
    
    def get_queue_summary(self) -> Dict[str, Any]:
        """
        Get a summary of queue statistics.
        
        Returns:
            Dictionary with queue summary
            
        Raises:
            JobQueueError: If queue operation fails
        """
        try:
            stats = self.job_queue.get_queue_stats()
            
            # Create a simplified summary
            summary = {
                'total_jobs': stats.get('total_jobs', 0),
                'pending_jobs': stats.get('pending_jobs', 0),
                'running_jobs': stats.get('running_jobs', 0),
                'completed_jobs': stats.get('completed_jobs', 0),
                'failed_jobs': stats.get('failed_jobs', 0),
                'total_images': stats.get('total_images', 0),
                'completed_images': stats.get('completed_images', 0),
                'failed_images': stats.get('failed_images', 0),
                'current_job': stats.get('current_job'),
                'queue_empty': stats.get('total_jobs', 0) == 0,
                'has_failed_jobs': stats.get('failed_jobs', 0) > 0
            }
            
            return summary
        except Exception as e:
            self.logger.log_error(f"Error getting queue summary: {e}")
            raise JobQueueError(f"Failed to get queue summary: {e}") 