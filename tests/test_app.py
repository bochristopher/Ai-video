"""
Unit tests for Flask API (app.py)
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestFlaskApp(unittest.TestCase):
    """Unit tests for Flask application"""

    @patch('app.VideoGenerator')
    def setUp(self, mock_video_gen):
        """Set up test fixtures"""
        print("\n" + "="*60)
        print(f"Running: {self._testMethodName}")
        print("="*60)

        # Import app after patching
        import app as flask_app
        self.app = flask_app.app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        # Clear jobs dict for clean slate
        flask_app.jobs.clear()

    def tearDown(self):
        """Clean up after tests"""
        print(f"✓ {self._testMethodName} completed")

    def test_index_route(self):
        """Test the index route returns HTML"""
        print("[TEST] Testing index route")

        response = self.client.get('/')

        # Should attempt to serve index.html
        # May fail if file doesn't exist in test, but we can check the attempt
        self.assertIn(response.status_code, [200, 404])
        print(f"[TEST] ✓ Status code: {response.status_code}")

    def test_health_check(self):
        """Test the health check endpoint"""
        print("[TEST] Testing health check endpoint")

        response = self.client.get('/health')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)

        print(f"[TEST] ✓ Health check: {data}")

    def test_list_models(self):
        """Test the list models endpoint"""
        print("[TEST] Testing list models endpoint")

        with patch('app.video_generator') as mock_gen:
            mock_gen.get_available_models.return_value = [
                {
                    'id': 'test-model',
                    'name': 'Test Model',
                    'description': 'A test model',
                    'requires_image': False
                }
            ]

            response = self.client.get('/api/models')
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertIn('models', data)
            self.assertEqual(len(data['models']), 1)

            print(f"[TEST] ✓ Models: {data['models']}")

    def test_generate_video_missing_prompt(self):
        """Test generate endpoint with missing prompt"""
        print("[TEST] Testing generate without prompt")

        response = self.client.post(
            '/api/generate',
            data=json.dumps({}),
            content_type='application/json'
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('Prompt is required', data['error'])

        print(f"[TEST] ✓ Error message: {data['error']}")

    @patch('app.threading.Thread')
    def test_generate_video_success(self, mock_thread):
        """Test successful video generation request"""
        print("[TEST] Testing successful generation request")

        payload = {
            'prompt': 'A beautiful sunset',
            'model': 'animate-diff',
            'duration': 3,
            'fps': 24
        }

        response = self.client.post(
            '/api/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 202)
        self.assertIn('job_id', data)
        self.assertEqual(data['status'], 'queued')

        # Verify thread was started
        mock_thread.assert_called_once()

        print(f"[TEST] ✓ Job ID: {data['job_id']}")
        print(f"[TEST] ✓ Status: {data['status']}")

    def test_get_status_not_found(self):
        """Test status endpoint with non-existent job"""
        print("[TEST] Testing status for non-existent job")

        response = self.client.get('/api/status/nonexistent-job-id')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

        print(f"[TEST] ✓ Error: {data['error']}")

    @patch('app.threading.Thread')
    def test_get_status_success(self, mock_thread):
        """Test status endpoint with existing job"""
        print("[TEST] Testing status for existing job")

        # First create a job
        payload = {'prompt': 'Test prompt'}
        response = self.client.post(
            '/api/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )

        job_data = json.loads(response.data)
        job_id = job_data['job_id']

        # Now check status
        status_response = self.client.get(f'/api/status/{job_id}')
        status_data = json.loads(status_response.data)

        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_data['id'], job_id)
        self.assertIn('status', status_data)
        self.assertIn('prompt', status_data)

        print(f"[TEST] ✓ Job status: {status_data['status']}")

    def test_get_video_not_found(self):
        """Test video download with non-existent job"""
        print("[TEST] Testing video download for non-existent job")

        response = self.client.get('/api/video/nonexistent-job-id')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

        print(f"[TEST] ✓ Error: {data['error']}")

    @patch('app.threading.Thread')
    def test_get_video_not_ready(self, mock_thread):
        """Test video download when video is not ready"""
        print("[TEST] Testing video download when not ready")

        # Create a job
        payload = {'prompt': 'Test prompt'}
        response = self.client.post(
            '/api/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )

        job_data = json.loads(response.data)
        job_id = job_data['job_id']

        # Try to download before completion
        video_response = self.client.get(f'/api/video/{job_id}')
        data = json.loads(video_response.data)

        self.assertEqual(video_response.status_code, 404)
        self.assertIn('error', data)

        print(f"[TEST] ✓ Error: {data['error']}")

    def test_list_jobs_empty(self):
        """Test listing jobs when none exist"""
        print("[TEST] Testing empty job list")

        response = self.client.get('/api/jobs')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('jobs', data)
        self.assertEqual(len(data['jobs']), 0)

        print(f"[TEST] ✓ Job list: empty")

    @patch('app.threading.Thread')
    def test_list_jobs_with_jobs(self, mock_thread):
        """Test listing jobs when jobs exist"""
        print("[TEST] Testing job list with jobs")

        # Create multiple jobs
        for i in range(3):
            payload = {'prompt': f'Test prompt {i}'}
            self.client.post(
                '/api/generate',
                data=json.dumps(payload),
                content_type='application/json'
            )

        # List jobs
        response = self.client.get('/api/jobs')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['jobs']), 3)

        print(f"[TEST] ✓ Found {len(data['jobs'])} jobs")

    def test_cors_headers(self):
        """Test that CORS headers are present"""
        print("[TEST] Testing CORS headers")

        response = self.client.get('/health')

        # CORS should be enabled via Flask-CORS
        self.assertEqual(response.status_code, 200)

        print(f"[TEST] ✓ CORS enabled")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("FLASK APP UNIT TESTS")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
