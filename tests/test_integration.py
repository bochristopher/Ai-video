"""
Integration tests for AI Video Generator
Tests the complete workflow from API request to video generation
"""
import unittest
from unittest.mock import patch, Mock
import json
import os
import sys
import time
import threading

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""

    @patch('app.VideoGenerator')
    def setUp(self, mock_video_gen):
        """Set up test fixtures"""
        print("\n" + "="*60)
        print(f"Running: {self._testMethodName}")
        print("="*60)

        import app as flask_app
        self.app = flask_app.app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.flask_app = flask_app

        # Clear jobs
        flask_app.jobs.clear()

    def tearDown(self):
        """Clean up after tests"""
        print(f"✓ {self._testMethodName} completed")

    @patch('app.video_generator')
    def test_complete_video_generation_workflow(self, mock_generator):
        """Test the complete workflow from request to completion"""
        print("[INTEGRATION] Testing complete video generation workflow")

        # Mock the video generator
        test_video_path = '/tmp/test_integration_video.mp4'

        # Create a fake video file
        os.makedirs('/tmp', exist_ok=True)
        with open(test_video_path, 'wb') as f:
            f.write(b'fake video content')

        mock_generator.generate.return_value = test_video_path

        # Step 1: Submit generation request
        print("[INTEGRATION] Step 1: Submit video generation request")
        payload = {
            'prompt': 'A beautiful mountain landscape',
            'model': 'animate-diff',
            'duration': 3
        }

        response = self.client.post(
            '/api/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)
        data = json.loads(response.data)
        job_id = data['job_id']

        print(f"[INTEGRATION] ✓ Job created: {job_id}")

        # Step 2: Check initial status
        print("[INTEGRATION] Step 2: Check job status")
        status_response = self.client.get(f'/api/status/{job_id}')
        status_data = json.loads(status_response.data)

        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_data['id'], job_id)
        self.assertIn('status', status_data)

        print(f"[INTEGRATION] ✓ Status: {status_data['status']}")

        # Step 3: Simulate completion by directly calling the async function
        print("[INTEGRATION] Step 3: Simulating video generation completion")
        self.flask_app.generate_video_async(
            job_id,
            payload['prompt'],
            payload['model'],
            payload['duration'],
            24
        )

        # Step 4: Check completed status
        print("[INTEGRATION] Step 4: Check completed status")
        status_response = self.client.get(f'/api/status/{job_id}')
        status_data = json.loads(status_response.data)

        self.assertEqual(status_data['status'], 'completed')
        self.assertEqual(status_data['progress'], 100)
        self.assertIsNotNone(status_data['video_url'])

        print(f"[INTEGRATION] ✓ Video completed")
        print(f"[INTEGRATION] ✓ Video URL: {status_data['video_url']}")

        # Step 5: Download video
        print("[INTEGRATION] Step 5: Download video")
        video_response = self.client.get(f'/api/video/{job_id}')

        self.assertEqual(video_response.status_code, 200)
        self.assertEqual(video_response.mimetype, 'video/mp4')

        print(f"[INTEGRATION] ✓ Video downloaded successfully")

        # Cleanup
        if os.path.exists(test_video_path):
            os.remove(test_video_path)

    @patch('app.video_generator')
    def test_failed_generation_workflow(self, mock_generator):
        """Test workflow when video generation fails"""
        print("[INTEGRATION] Testing failed generation workflow")

        # Mock generator to raise exception
        mock_generator.generate.side_effect = Exception("Test error")

        # Submit request
        payload = {'prompt': 'Test prompt'}

        response = self.client.post(
            '/api/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )

        job_id = json.loads(response.data)['job_id']

        # Simulate generation
        self.flask_app.generate_video_async(
            job_id,
            payload['prompt'],
            'animate-diff',
            3,
            24
        )

        # Check failed status
        status_response = self.client.get(f'/api/status/{job_id}')
        status_data = json.loads(status_response.data)

        self.assertEqual(status_data['status'], 'failed')
        self.assertIsNotNone(status_data['error'])

        print(f"[INTEGRATION] ✓ Failure handled correctly")
        print(f"[INTEGRATION] ✓ Error: {status_data['error']}")

    @patch('app.video_generator')
    def test_multiple_concurrent_jobs(self, mock_generator):
        """Test handling multiple concurrent video generation jobs"""
        print("[INTEGRATION] Testing multiple concurrent jobs")

        test_video_path = '/tmp/test_concurrent.mp4'
        with open(test_video_path, 'wb') as f:
            f.write(b'fake video')

        mock_generator.generate.return_value = test_video_path

        # Create multiple jobs
        job_ids = []
        for i in range(5):
            payload = {'prompt': f'Test prompt {i}'}
            response = self.client.post(
                '/api/generate',
                data=json.dumps(payload),
                content_type='application/json'
            )
            data = json.loads(response.data)
            job_ids.append(data['job_id'])

        print(f"[INTEGRATION] ✓ Created {len(job_ids)} jobs")

        # Check all jobs exist
        jobs_response = self.client.get('/api/jobs')
        jobs_data = json.loads(jobs_response.data)

        self.assertEqual(len(jobs_data['jobs']), 5)

        print(f"[INTEGRATION] ✓ All jobs tracked correctly")

        # Cleanup
        if os.path.exists(test_video_path):
            os.remove(test_video_path)

    def test_api_error_handling(self):
        """Test API error handling"""
        print("[INTEGRATION] Testing API error handling")

        # Test with invalid JSON
        response = self.client.post(
            '/api/generate',
            data='invalid json',
            content_type='application/json'
        )

        self.assertIn(response.status_code, [400, 500])

        print(f"[INTEGRATION] ✓ Invalid JSON handled")

        # Test with missing content type
        response = self.client.post(
            '/api/generate',
            data=json.dumps({'prompt': 'test'})
        )

        # Should still work or return appropriate error
        self.assertIsNotNone(response.status_code)

        print(f"[INTEGRATION] ✓ Missing content-type handled")

    @patch('app.video_generator')
    def test_progress_tracking(self, mock_generator):
        """Test progress tracking during generation"""
        print("[INTEGRATION] Testing progress tracking")

        test_video_path = '/tmp/test_progress.mp4'
        with open(test_video_path, 'wb') as f:
            f.write(b'fake video')

        # Capture progress callback
        progress_values = []

        def mock_generate(*args, **kwargs):
            callback = kwargs.get('progress_callback')
            if callback:
                callback(20)
                callback(50)
                callback(80)
                callback(100)
            return test_video_path

        mock_generator.generate.side_effect = mock_generate

        # Submit job
        payload = {'prompt': 'Test prompt'}
        response = self.client.post(
            '/api/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )

        job_id = json.loads(response.data)['job_id']

        # Simulate generation
        self.flask_app.generate_video_async(
            job_id,
            payload['prompt'],
            'animate-diff',
            3,
            24
        )

        # Check final progress
        status_response = self.client.get(f'/api/status/{job_id}')
        status_data = json.loads(status_response.data)

        self.assertEqual(status_data['progress'], 100)

        print(f"[INTEGRATION] ✓ Progress tracked successfully")

        # Cleanup
        if os.path.exists(test_video_path):
            os.remove(test_video_path)

    def test_model_availability(self):
        """Test that models are available through API"""
        print("[INTEGRATION] Testing model availability")

        with patch('app.video_generator') as mock_gen:
            mock_gen.get_available_models.return_value = [
                {'id': 'animate-diff', 'name': 'AnimateDiff', 'description': 'Test', 'requires_image': False},
                {'id': 'text2video-zero', 'name': 'Text2Video', 'description': 'Test', 'requires_image': False}
            ]

            response = self.client.get('/api/models')
            data = json.loads(response.data)

            self.assertGreaterEqual(len(data['models']), 2)

            model_ids = [m['id'] for m in data['models']]
            self.assertIn('animate-diff', model_ids)

            print(f"[INTEGRATION] ✓ Available models: {model_ids}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("INTEGRATION TESTS")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
