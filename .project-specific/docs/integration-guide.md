# Integration Guide - Forge-API-Tool

## 🎯 Overview
This guide provides comprehensive instructions for integrating the Forge-API-Tool with other systems, applications, and services, including API integrations, webhook setups, and custom extensions.

## 🔌 API Integration

### REST API Endpoints

#### Base URL
```
http://localhost:5000/api/v1
```

#### Authentication
```bash
# API Key Authentication
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:5000/api/v1/health

# Session Authentication (for web dashboard)
curl -H "Cookie: session=YOUR_SESSION_ID" \
     http://localhost:5000/api/v1/status
```

#### Core Endpoints

##### Health Check
```bash
GET /api/v1/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-12T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "forge_api": "connected",
    "database": "connected",
    "cache": "connected"
  }
}
```

##### Image Generation
```bash
POST /api/v1/generate
```
**Request Body:**
```json
{
  "prompt": "a beautiful landscape",
  "negative_prompt": "blurry, low quality",
  "width": 1024,
  "height": 1024,
  "steps": 20,
  "cfg_scale": 7.5,
  "seed": 42,
  "wildcards": {
    "enabled": true,
    "max_depth": 2
  }
}
```
**Response:**
```json
{
  "job_id": "job_12345",
  "status": "queued",
  "estimated_time": 30,
  "webhook_url": "https://your-domain.com/webhooks/generation"
}
```

##### Job Status
```bash
GET /api/v1/jobs/{job_id}
```
**Response:**
```json
{
  "job_id": "job_12345",
  "status": "completed",
  "progress": 100,
  "result": {
    "image_url": "/outputs/generated_image_12345.png",
    "metadata": {
      "prompt": "a beautiful landscape",
      "parameters": {
        "width": 1024,
        "height": 1024,
        "steps": 20
      }
    }
  }
}
```

##### Batch Generation
```bash
POST /api/v1/generate/batch
```
**Request Body:**
```json
{
  "prompts": [
    "a beautiful landscape",
    "a futuristic city",
    "a peaceful forest"
  ],
  "parameters": {
    "width": 1024,
    "height": 1024,
    "steps": 20
  },
  "wildcards": {
    "enabled": true
  }
}
```

##### Configuration Management
```bash
GET /api/v1/config
PUT /api/v1/config
GET /api/v1/config/{section}
PUT /api/v1/config/{section}
```

##### Wildcard Management
```bash
GET /api/v1/wildcards
GET /api/v1/wildcards/{category}
POST /api/v1/wildcards/{category}
DELETE /api/v1/wildcards/{category}/{item}
```

### WebSocket API

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onopen = function() {
  console.log('Connected to Forge-API-Tool WebSocket');
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

#### Real-time Updates
```javascript
// Subscribe to job updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'jobs',
  job_id: 'job_12345'
}));

// Receive job updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'job_update') {
    updateJobProgress(data.job_id, data.progress);
  }
};
```

## 🔗 Webhook Integration

### Webhook Setup

#### Configure Webhooks
```bash
# Set webhook URL
python cli.py config set webhooks.generation_url "https://your-domain.com/webhooks/generation"
python cli.py config set webhooks.error_url "https://your-domain.com/webhooks/errors"

# Enable webhooks
python cli.py config set webhooks.enabled true
```

#### Webhook Payload Format
```json
{
  "event": "generation.completed",
  "timestamp": "2024-06-12T10:30:00Z",
  "job_id": "job_12345",
  "data": {
    "status": "completed",
    "image_url": "/outputs/generated_image_12345.png",
    "metadata": {
      "prompt": "a beautiful landscape",
      "parameters": {
        "width": 1024,
        "height": 1024,
        "steps": 20
      }
    }
  },
  "signature": "sha256=abc123..."
}
```

#### Webhook Verification
```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

### Webhook Endpoints

#### Generation Webhook Handler
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/generation', methods=['POST'])
def generation_webhook():
    # Verify signature
    signature = request.headers.get('X-Webhook-Signature')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    data = request.json
    
    # Process the webhook
    if data['event'] == 'generation.completed':
        process_completed_generation(data)
    elif data['event'] == 'generation.failed':
        process_failed_generation(data)
    
    return jsonify({'status': 'received'}), 200

def process_completed_generation(data):
    job_id = data['job_id']
    image_url = data['data']['image_url']
    # Process the completed generation
    print(f"Generation completed for job {job_id}: {image_url}")
```

## 🔧 Custom Extensions

### Plugin System

#### Plugin Structure
```
plugins/
├── my_custom_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   ├── config.json
│   └── requirements.txt
```

#### Plugin Implementation
```python
# plugins/my_custom_plugin/plugin.py
from core.plugin_base import PluginBase

class MyCustomPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "My Custom Plugin"
        self.version = "1.0.0"
    
    def on_generation_start(self, job_data):
        """Called when image generation starts"""
        print(f"Generation starting for job: {job_data['job_id']}")
        return job_data
    
    def on_generation_complete(self, job_data, result):
        """Called when image generation completes"""
        print(f"Generation completed for job: {job_data['job_id']}")
        # Process the result
        return result
    
    def on_error(self, job_data, error):
        """Called when an error occurs"""
        print(f"Error in job {job_data['job_id']}: {error}")
        return error
```

#### Plugin Configuration
```json
{
  "name": "my_custom_plugin",
  "version": "1.0.0",
  "description": "A custom plugin for Forge-API-Tool",
  "author": "Your Name",
  "hooks": [
    "on_generation_start",
    "on_generation_complete",
    "on_error"
  ],
  "settings": {
    "enabled": true,
    "custom_setting": "value"
  }
}
```

#### Load Plugin
```bash
# Install plugin
python cli.py plugins install plugins/my_custom_plugin

# Enable plugin
python cli.py plugins enable my_custom_plugin

# List plugins
python cli.py plugins list

# Disable plugin
python cli.py plugins disable my_custom_plugin
```

### Custom API Extensions

#### Custom Endpoint
```python
# extensions/custom_api.py
from flask import Blueprint, request, jsonify
from core.api_auth import require_api_key

custom_api = Blueprint('custom_api', __name__)

@custom_api.route('/custom/process', methods=['POST'])
@require_api_key
def custom_process():
    data = request.json
    
    # Custom processing logic
    result = process_custom_data(data)
    
    return jsonify({
        'status': 'success',
        'result': result
    })

def process_custom_data(data):
    # Implement your custom logic here
    return {'processed': True, 'data': data}
```

#### Register Extension
```python
# In your main application
from extensions.custom_api import custom_api

app.register_blueprint(custom_api, url_prefix='/api/v1')
```

## 🔄 External Service Integration

### Database Integration

#### PostgreSQL Integration
```python
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    def connect(self):
        return psycopg2.connect(self.connection_string)
    
    def save_generation_result(self, job_id, result):
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO generation_results (job_id, prompt, image_url, metadata)
                    VALUES (%s, %s, %s, %s)
                """, (job_id, result['prompt'], result['image_url'], result['metadata']))
                conn.commit()
```

#### Redis Integration
```python
import redis
import json

class CacheManager:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    def cache_generation_result(self, job_id, result):
        self.redis.setex(
            f"generation:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(result)
        )
    
    def get_generation_result(self, job_id):
        data = self.redis.get(f"generation:{job_id}")
        return json.loads(data) if data else None
```

### Cloud Storage Integration

#### AWS S3 Integration
```python
import boto3
from botocore.exceptions import ClientError

class S3Storage:
    def __init__(self, bucket_name, aws_access_key_id, aws_secret_access_key):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bucket_name = bucket_name
    
    def upload_image(self, local_path, s3_key):
        try:
            self.s3.upload_file(local_path, self.bucket_name, s3_key)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return None
    
    def download_image(self, s3_key, local_path):
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_path)
            return True
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            return False
```

#### Google Cloud Storage Integration
```python
from google.cloud import storage

class GCSStorage:
    def __init__(self, bucket_name, credentials_path=None):
        if credentials_path:
            self.client = storage.Client.from_service_account_json(credentials_path)
        else:
            self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    def upload_image(self, local_path, gcs_key):
        blob = self.bucket.blob(gcs_key)
        blob.upload_from_filename(local_path)
        return blob.public_url
    
    def download_image(self, gcs_key, local_path):
        blob = self.bucket.blob(gcs_key)
        blob.download_to_filename(local_path)
        return True
```

### Message Queue Integration

#### RabbitMQ Integration
```python
import pika
import json

class RabbitMQManager:
    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.connection = None
        self.channel = None
    
    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(**self.connection_params)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='generation_jobs')
    
    def publish_job(self, job_data):
        self.channel.basic_publish(
            exchange='',
            routing_key='generation_jobs',
            body=json.dumps(job_data)
        )
    
    def consume_jobs(self, callback):
        self.channel.basic_consume(
            queue='generation_jobs',
            on_message_callback=callback,
            auto_ack=True
        )
        self.channel.start_consuming()
```

#### Redis Queue Integration
```python
from rq import Queue
from redis import Redis

class RedisQueueManager:
    def __init__(self, redis_url):
        self.redis = Redis.from_url(redis_url)
        self.queue = Queue(connection=self.redis)
    
    def enqueue_generation(self, generation_function, *args, **kwargs):
        job = self.queue.enqueue(generation_function, *args, **kwargs)
        return job.id
    
    def get_job_status(self, job_id):
        job = self.queue.fetch_job(job_id)
        if job:
            return {
                'status': job.get_status(),
                'result': job.result,
                'error': job.exc_info
            }
        return None
```

## 🔐 Authentication and Security

### API Key Management
```python
from core.auth import APIKeyManager

class CustomAuthManager(APIKeyManager):
    def validate_api_key(self, api_key):
        # Custom validation logic
        return self.check_key_in_database(api_key)
    
    def generate_api_key(self, user_id):
        # Custom key generation
        return self.create_key_for_user(user_id)
    
    def revoke_api_key(self, api_key):
        # Custom key revocation
        return self.remove_key_from_database(api_key)
```

### OAuth Integration
```python
from flask_oauthlib.provider import OAuth2Provider

oauth = OAuth2Provider()

@oauth.clientgetter
def load_client(client_id):
    # Load OAuth client from database
    return get_client_from_database(client_id)

@oauth.tokengetter
def load_token(access_token=None):
    # Load OAuth token from database
    return get_token_from_database(access_token)

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    # Save OAuth token to database
    save_token_to_database(token, request.user)
```

## 📊 Monitoring and Analytics

### Custom Metrics
```python
from core.metrics import MetricsCollector

class CustomMetrics(MetricsCollector):
    def __init__(self):
        super().__init__()
    
    def record_generation_request(self, user_id, prompt_length):
        self.increment_counter('generation_requests_total')
        self.record_histogram('prompt_length', prompt_length)
        self.record_gauge('active_users', user_id)
    
    def record_generation_success(self, job_id, generation_time):
        self.increment_counter('generation_success_total')
        self.record_histogram('generation_time', generation_time)
    
    def record_generation_error(self, error_type):
        self.increment_counter('generation_errors_total', {'error_type': error_type})
```

### Integration with Monitoring Services

#### Prometheus Integration
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
generation_requests = Counter('generation_requests_total', 'Total generation requests')
generation_time = Histogram('generation_time_seconds', 'Time spent generating images')
active_users = Gauge('active_users', 'Number of active users')

# Record metrics
def record_generation_metrics(job_id, generation_time_seconds):
    generation_requests.inc()
    generation_time.observe(generation_time_seconds)
```

#### DataDog Integration
```python
from datadog import initialize, statsd

# Initialize DataDog
initialize(api_key='your_api_key', app_key='your_app_key')

# Send metrics
def send_datadog_metrics(job_id, generation_time):
    statsd.increment('forge_api.generation.requests')
    statsd.histogram('forge_api.generation.time', generation_time)
    statsd.gauge('forge_api.active_jobs', get_active_job_count())
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
name: Forge-API-Tool Integration

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        python cli.py tests run all
    
    - name: Run integration tests
      run: |
        python cli.py tests run integration
    
    - name: Deploy to staging
      if: github.ref == 'refs/heads/main'
      run: |
        python cli.py deploy staging
```

### Docker Integration
```dockerfile
# Dockerfile for integration
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose API port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/v1/health || exit 1

CMD ["python", "cli.py", "web", "start", "production"]
```

## 📝 Integration Examples

### Python Client Library
```python
import requests
import json

class ForgeAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def generate_image(self, prompt, **kwargs):
        data = {
            'prompt': prompt,
            **kwargs
        }
        response = requests.post(
            f'{self.base_url}/api/v1/generate',
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def get_job_status(self, job_id):
        response = requests.get(
            f'{self.base_url}/api/v1/jobs/{job_id}',
            headers=self.headers
        )
        return response.json()

# Usage
client = ForgeAPIClient('http://localhost:5000', 'your_api_key')
result = client.generate_image('a beautiful landscape')
print(f"Job ID: {result['job_id']}")
```

### JavaScript/Node.js Client
```javascript
class ForgeAPIClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async generateImage(prompt, options = {}) {
        const data = {
            prompt,
            ...options
        };
        
        const response = await fetch(`${this.baseUrl}/api/v1/generate`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    async getJobStatus(jobId) {
        const response = await fetch(`${this.baseUrl}/api/v1/jobs/${jobId}`, {
            headers: this.headers
        });
        
        return await response.json();
    }
}

// Usage
const client = new ForgeAPIClient('http://localhost:5000', 'your_api_key');
client.generateImage('a beautiful landscape')
    .then(result => console.log('Job ID:', result.job_id))
    .catch(error => console.error('Error:', error));
```

This integration guide provides comprehensive instructions for integrating the Forge-API-Tool with various systems and services. Customize the examples and configurations based on your specific integration requirements. 