# Next Steps - Immediate Action Plan

## 🎯 **Current Status**
✅ **Phase 1 Complete:** Foundation utilities and config service created
🔄 **Ready for Phase 2:** Core services extraction

## 🚀 **Immediate Next Steps (This Week)**

### **Step 1: Create Generation Service** (Priority: HIGH)
**File:** `services/generation_service.py`
**Lines to extract:** 535-622, 623-706, 707-774 from app.py

```python
# Extract these functions from app.py:
# - generate_image() (lines 535-622)
# - start_batch() (lines 623-706) 
# - preview_batch() (lines 707-774)
# - update_generation_progress() (lines 422-446)
# - stop_generation() (lines 1200-1237)
```

**Key functions to create:**
- `generate_single_image(config_name, prompt, seed)`
- `start_batch_generation(config_name, batch_size, num_batches, prompts, user_prompt)`
- `preview_batch_prompts(config_name, batch_size, num_batches, user_prompt)`
- `stop_generation()`
- `update_generation_progress(current, total, config_name)`

### **Step 2: Create Queue Service** (Priority: HIGH)
**File:** `services/queue_service.py`
**Lines to extract:** 775-887 from app.py

```python
# Extract these functions from app.py:
# - get_queue_status() (lines 775-784)
# - get_queue_jobs() (lines 785-797)
# - get_job_details() (lines 798-810)
# - retry_job() (lines 811-823)
# - cancel_job() (lines 824-836)
# - clear_queue() (lines 837-849)
# - clear_completed_jobs() (lines 850-862)
# - get_priority_stats() (lines 863-887)
```

### **Step 3: Create Output Service** (Priority: HIGH)
**File:** `services/output_service.py`
**Lines to extract:** 888-1036, 1238-1308 from app.py

```python
# Extract these functions from app.py:
# - get_outputs() (lines 888-940)
# - get_output_statistics() (lines 941-957)
# - get_output_dates() (lines 958-977)
# - serve_output_image() (lines 978-1002)
# - get_output_metadata() (lines 1003-1036)
# - get_output_directory() (lines 1238-1251)
# - get_latest_output_directory() (lines 1252-1265)
# - open_output_folder() (lines 1266-1308)
```

## 📋 **Week 1 Checklist**

### **Day 1-2: Generation Service**
- [ ] Create `services/generation_service.py`
- [ ] Extract generation-related business logic
- [ ] Add proper error handling and validation
- [ ] Create unit tests for generation service
- [ ] Update imports in existing code

### **Day 3-4: Queue Service**
- [ ] Create `services/queue_service.py`
- [ ] Extract queue-related business logic
- [ ] Add proper error handling and validation
- [ ] Create unit tests for queue service
- [ ] Update imports in existing code

### **Day 5: Output Service**
- [ ] Create `services/output_service.py`
- [ ] Extract output-related business logic
- [ ] Add proper error handling and validation
- [ ] Create unit tests for output service
- [ ] Update imports in existing code

## 🔧 **Implementation Template**

### **Service Class Template:**
```python
"""
[Service Name] service for the Flask web dashboard.

This module provides business logic for [service domain],
separating it from the HTTP route handlers.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from core.centralized_logger import logger
from core.exceptions import [RelevantExceptions]
from utils.validators import [RelevantValidators]
from utils.response_helpers import [RelevantHelpers]


class [ServiceName]Service:
    """
    Service class for [service domain] operations.
    """
    
    def __init__(self, [dependencies]):
        """
        Initialize the [service name] service.
        
        Args:
            [dependencies]: Service dependencies
        """
        self.[dependencies] = [dependencies]
    
    def [method_name](self, [parameters]) -> [return_type]:
        """
        [Method description].
        
        Args:
            [parameters]: Method parameters
            
        Returns:
            [return description]
            
        Raises:
            [RelevantException]: If operation fails
        """
        try:
            # Business logic here
            pass
        except [SpecificException] as e:
            logger.log_error(f"[Error context]: {e}")
            raise [RelevantException](f"[Error message]: {e}")
        except Exception as e:
            logger.log_error(f"Unexpected error in [method_name]: {e}")
            raise [RelevantException](f"Unexpected error: {e}")
```

### **Route Template:**
```python
"""
[Route Domain] API routes for the Flask web dashboard.

This module contains all [domain]-related API endpoints,
using the service layer for business logic and utilities for
error handling and response formatting.
"""

from flask import Blueprint, request
from utils.decorators import handle_errors, validate_input, require_json
from utils.response_helpers import (
    success_response, error_response, [specific_helpers]
)
from services.[service_name]_service import [ServiceName]Service
from core.centralized_logger import logger

# Create blueprint
[domain]_bp = Blueprint('[domain]', __name__)

# Initialize service
[service_name]_service = [ServiceName]Service([dependencies])


@[domain]_bp.route('/api/[domain]', methods=['GET'])
@handle_errors
def get_[domain]():
    """
    Get [domain] data.
    
    Returns:
        JSON response with [domain] data
    """
    [data] = [service_name]_service.get_[domain]()
    return success_response({'[domain]': [data]})
```

## 🧪 **Testing Strategy**

### **Unit Test Template:**
```python
"""
Unit tests for [ServiceName]Service.
"""

import unittest
from unittest.mock import Mock, patch
from services.[service_name]_service import [ServiceName]Service
from core.exceptions import [RelevantExceptions]


class Test[ServiceName]Service(unittest.TestCase):
    """Test cases for [ServiceName]Service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.[dependency] = Mock()
        self.service = [ServiceName]Service(self.[dependency])
    
    def test_[method_name]_success(self):
        """Test successful [method_name] operation."""
        # Arrange
        [test_data] = [expected_data]
        self.[dependency].[method].return_value = [expected_result]
        
        # Act
        result = self.service.[method_name]([test_data])
        
        # Assert
        self.assertEqual(result, [expected_result])
        self.[dependency].[method].assert_called_once_with([expected_args])
    
    def test_[method_name]_failure(self):
        """Test [method_name] operation failure."""
        # Arrange
        self.[dependency].[method].side_effect = [RelevantException]("Test error")
        
        # Act & Assert
        with self.assertRaises([RelevantException]):
            self.service.[method_name]([test_data])
```

## 📊 **Progress Tracking**

### **Week 1 Goals:**
- [ ] **Generation Service:** Complete with tests
- [ ] **Queue Service:** Complete with tests  
- [ ] **Output Service:** Complete with tests
- [ ] **Code Coverage:** >80% for new services
- [ ] **Documentation:** Update service documentation

### **Success Metrics:**
- **Lines of Code:** Reduce app.py by ~500 lines
- **Test Coverage:** >80% for new services
- **Error Handling:** 100% standardized across new services
- **Response Format:** 100% consistent across new endpoints

## 🚨 **Risk Mitigation**

### **Backward Compatibility:**
- Keep all existing route handlers in app.py during transition
- Use feature flags to switch between old and new implementations
- Maintain identical API responses

### **Testing:**
- Run existing tests to ensure no regressions
- Add new tests for each service
- Integration tests for complete workflows

### **Rollback Plan:**
- Keep original app.py intact until all tests pass
- Use git branches for each service extraction
- Easy rollback by reverting to original app.py

## 🎯 **Next Week Preview**

### **Week 2 Goals:**
- [ ] Log Service
- [ ] Settings Service  
- [ ] Status Service
- [ ] RunDiffusion Service

### **Week 3 Goals:**
- [ ] Route extraction for completed services
- [ ] Dashboard routes
- [ ] Generation routes
- [ ] Queue routes
- [ ] Output routes

---

**Ready to start with Generation Service! 🚀** 