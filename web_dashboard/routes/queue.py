"""
Queue routes for the Flask web dashboard.

This module contains route handlers for job queue operations,
using the Queue Service for business logic.
"""

from flask import Blueprint, request, jsonify
from services.queue_service import QueueService
from core.exceptions import (
    JobQueueError, ValidationError
)
from utils.response_helpers import error_response, success_response
from utils.decorators import handle_errors

# Create blueprint
queue_bp = Blueprint('queue', __name__)

# Service instance (will be initialized in app.py)
queue_service = None


def init_queue_service(service_instance):
    """Initialize the queue service instance."""
    global queue_service
    queue_service = service_instance


@queue_bp.route('/api/queue/status')
@handle_errors
def get_queue_status():
    """Get detailed queue status with enhanced statistics."""
    try:
        stats = queue_service.get_queue_status()
        return success_response(stats)
    except JobQueueError as e:
        return error_response(str(e), 500)


@queue_bp.route('/api/queue/jobs')
@handle_errors
def get_queue_jobs():
    """Get all jobs in the queue with detailed information."""
    try:
        result = queue_service.get_all_jobs()
        return success_response(result)
    except JobQueueError as e:
        return error_response(str(e), 500)


@queue_bp.route('/api/queue/jobs/<job_id>')
@handle_errors
def get_job_details(job_id):
    """Get detailed information about a specific job."""
    try:
        job_data = queue_service.get_job_details(job_id)
        return success_response(job_data)
    except ValidationError as e:
        return error_response(str(e), 400)
    except JobQueueError as e:
        return error_response(str(e), 404)


@queue_bp.route('/api/queue/jobs/<job_id>/retry', methods=['POST'])
@handle_errors
def retry_job(job_id):
    """Retry a failed job."""
    try:
        result = queue_service.retry_job(job_id)
        return success_response(result)
    except ValidationError as e:
        return error_response(str(e), 400)
    except JobQueueError as e:
        return error_response(str(e), 400)


@queue_bp.route('/api/queue/jobs/<job_id>/cancel', methods=['POST'])
@handle_errors
def cancel_job(job_id):
    """Cancel a specific job."""
    try:
        result = queue_service.cancel_job(job_id)
        return success_response(result)
    except ValidationError as e:
        return error_response(str(e), 400)
    except JobQueueError as e:
        return error_response(str(e), 404)


@queue_bp.route('/api/queue/clear', methods=['POST'])
@handle_errors
def clear_queue():
    """Clear all jobs from the queue."""
    try:
        result = queue_service.clear_all_jobs()
        return success_response(result)
    except JobQueueError as e:
        return error_response(str(e), 500)


@queue_bp.route('/api/queue/clear-completed', methods=['POST'])
@handle_errors
def clear_completed_jobs():
    """Clear only completed and failed jobs from the queue."""
    try:
        result = queue_service.clear_completed_jobs()
        return success_response(result)
    except JobQueueError as e:
        return error_response(str(e), 500)


@queue_bp.route('/api/queue/priority-stats')
@handle_errors
def get_priority_stats():
    """Get queue statistics broken down by priority."""
    try:
        stats = queue_service.get_priority_stats()
        return success_response(stats)
    except JobQueueError as e:
        return error_response(str(e), 500)


@queue_bp.route('/api/queue/summary')
@handle_errors
def get_queue_summary():
    """Get a summary of queue statistics."""
    try:
        summary = queue_service.get_queue_summary()
        return success_response(summary)
    except JobQueueError as e:
        return error_response(str(e), 500) 