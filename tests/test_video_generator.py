"""
Unit tests for video_generator.py
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from video_generator import VideoGenerator


class TestVideoGenerator(unittest.TestCase):
    """Unit tests for VideoGenerator class"""

    def setUp(self):
        """Set up test fixtures"""
        print("\n" + "="*60)
        print(f"Running: {self._testMethodName}")
        print("="*60)

    def tearDown(self):
        """Clean up after tests"""
        print(f"✓ {self._testMethodName} completed")

    @patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'})
    def test_init_with_api_token(self):
        """Test VideoGenerator initialization with API token"""
        print("[TEST] Testing initialization with API token")

        generator = VideoGenerator()

        self.assertIsNotNone(generator.api_token)
        self.assertEqual(generator.api_token, 'test_token')
        self.assertIsInstance(generator.models, dict)
        self.assertGreater(len(generator.models), 0)

        print(f"[TEST] ✓ API token loaded: {generator.api_token}")
        print(f"[TEST] ✓ Models loaded: {len(generator.models)}")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_token(self):
        """Test VideoGenerator initialization without API token"""
        print("[TEST] Testing initialization without API token")

        generator = VideoGenerator()

        self.assertIsNone(generator.api_token)
        print("[TEST] ✓ No API token (expected)")

    def test_get_available_models(self):
        """Test getting available models"""
        print("[TEST] Testing get_available_models")

        with patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'}):
            generator = VideoGenerator()
            models = generator.get_available_models()

            self.assertIsInstance(models, list)
            self.assertGreater(len(models), 0)

            # Check first model structure
            first_model = models[0]
            self.assertIn('id', first_model)
            self.assertIn('name', first_model)
            self.assertIn('description', first_model)
            self.assertIn('requires_image', first_model)

            print(f"[TEST] ✓ Found {len(models)} models")
            for model in models:
                print(f"[TEST]   - {model['id']}: {model['name']}")

    @patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'})
    def test_generate_without_api_token(self):
        """Test generate method fails without API token"""
        print("[TEST] Testing generate without API token")

        with patch.dict(os.environ, {}, clear=True):
            generator = VideoGenerator()
            generator.api_token = None

            with self.assertRaises(ValueError) as context:
                generator.generate("test prompt")

            self.assertIn("REPLICATE_API_TOKEN", str(context.exception))
            print(f"[TEST] ✓ Raised ValueError: {context.exception}")

    @patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'})
    def test_generate_with_invalid_model(self):
        """Test generate method with invalid model"""
        print("[TEST] Testing generate with invalid model")

        generator = VideoGenerator()

        with self.assertRaises(ValueError) as context:
            generator.generate("test prompt", model="invalid-model")

        self.assertIn("Unknown model", str(context.exception))
        print(f"[TEST] ✓ Raised ValueError: {context.exception}")

    @patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'})
    @patch('video_generator.replicate.run')
    @patch('video_generator.requests.get')
    def test_generate_animate_diff_success(self, mock_get, mock_replicate):
        """Test successful video generation with AnimateDiff"""
        print("[TEST] Testing AnimateDiff generation")

        # Mock replicate.run to return a video URL
        mock_replicate.return_value = "https://example.com/video.mp4"

        # Mock requests.get for video download
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b'fake video content'])
        mock_response.headers = {'content-length': '1000'}
        mock_get.return_value = mock_response

        generator = VideoGenerator()

        # Create temporary output directory
        output_dir = '/tmp/test_videos'
        os.makedirs(output_dir, exist_ok=True)

        video_path = generator.generate(
            prompt="A beautiful sunset",
            model="animate-diff",
            output_dir=output_dir,
            job_id="test_123"
        )

        self.assertTrue(os.path.exists(video_path))
        self.assertTrue(video_path.endswith('.mp4'))

        print(f"[TEST] ✓ Video generated at: {video_path}")

        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)

    @patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'})
    def test_download_video_string_url(self):
        """Test _download_video with string URL"""
        print("[TEST] Testing download with string URL")

        with patch('video_generator.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.iter_content = Mock(return_value=[b'test content'])
            mock_response.headers = {'content-length': '100'}
            mock_get.return_value = mock_response

            generator = VideoGenerator()
            output_path = '/tmp/test_video.mp4'

            result = generator._download_video(
                "https://example.com/video.mp4",
                output_path
            )

            self.assertEqual(result, output_path)
            self.assertTrue(os.path.exists(output_path))

            print(f"[TEST] ✓ Video downloaded to: {output_path}")

            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)

    @patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'})
    def test_download_video_list_url(self):
        """Test _download_video with list of URLs"""
        print("[TEST] Testing download with URL list")

        with patch('video_generator.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.iter_content = Mock(return_value=[b'test content'])
            mock_response.headers = {'content-length': '100'}
            mock_get.return_value = mock_response

            generator = VideoGenerator()
            output_path = '/tmp/test_video_list.mp4'

            result = generator._download_video(
                ["https://example.com/video.mp4", "https://example.com/video2.mp4"],
                output_path
            )

            self.assertEqual(result, output_path)
            print(f"[TEST] ✓ Video downloaded from list")

            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)

    @patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'})
    def test_download_video_invalid_format(self):
        """Test _download_video with invalid format"""
        print("[TEST] Testing download with invalid format")

        generator = VideoGenerator()

        with self.assertRaises(ValueError) as context:
            generator._download_video(
                {'invalid': 'format'},
                '/tmp/test.mp4'
            )

        self.assertIn("Unexpected output format", str(context.exception))
        print(f"[TEST] ✓ Raised ValueError: {context.exception}")

    def test_progress_callback(self):
        """Test progress callback functionality"""
        print("[TEST] Testing progress callback")

        progress_values = []

        def callback(progress):
            progress_values.append(progress)
            print(f"[TEST] Progress: {progress}%")

        with patch.dict(os.environ, {'REPLICATE_API_TOKEN': 'test_token'}):
            with patch('video_generator.replicate.run') as mock_replicate:
                with patch('video_generator.requests.get') as mock_get:
                    mock_replicate.return_value = "https://example.com/video.mp4"

                    mock_response = Mock()
                    mock_response.iter_content = Mock(return_value=[b'content'])
                    mock_response.headers = {'content-length': '100'}
                    mock_get.return_value = mock_response

                    generator = VideoGenerator()

                    output_dir = '/tmp/test_progress'
                    os.makedirs(output_dir, exist_ok=True)

                    generator.generate(
                        prompt="test",
                        model="animate-diff",
                        output_dir=output_dir,
                        job_id="progress_test",
                        progress_callback=callback
                    )

                    # Check that progress was reported
                    self.assertGreater(len(progress_values), 0)
                    print(f"[TEST] ✓ Progress callbacks: {progress_values}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("VIDEO GENERATOR UNIT TESTS")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
