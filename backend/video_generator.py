import os
import time
import replicate
from dotenv import load_dotenv
import requests
from PIL import Image
import io

load_dotenv()


class VideoGenerator:
    """Handles AI video generation using various models"""

    def __init__(self):
        print("[VideoGenerator] Initializing...")
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        if self.api_token:
            os.environ['REPLICATE_API_TOKEN'] = self.api_token
            print("[VideoGenerator] ✓ API token loaded")
        else:
            print("[VideoGenerator] ⚠ WARNING: No API token found")

        self.models = {
            'stable-video-diffusion': {
                'name': 'Stable Video Diffusion',
                'model_id': 'stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438',
                'description': 'Generate videos from images using Stable Video Diffusion',
                'requires_image': True
            },
            'animate-diff': {
                'name': 'AnimateDiff',
                'model_id': 'lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f',
                'description': 'Text-to-video animation generation',
                'requires_image': False
            },
            'text2video-zero': {
                'name': 'Text2Video-Zero',
                'model_id': 'cjwbw/text2video-zero:2198e556fa42e9eef07fdc461d18498eb8a21d2d7e48e7dbb5f90c2aa0e65e50',
                'description': 'Zero-shot text-to-video generation',
                'requires_image': False
            }
        }

    def get_available_models(self):
        """Return list of available models"""
        return [
            {
                'id': key,
                'name': model['name'],
                'description': model['description'],
                'requires_image': model['requires_image']
            }
            for key, model in self.models.items()
        ]

    def generate(self, prompt, model='animate-diff', duration=3, fps=24,
                 output_dir='videos', job_id=None, progress_callback=None):
        """
        Generate a video from a text prompt

        Args:
            prompt: Text description of the video
            model: Model identifier to use
            duration: Video duration in seconds
            fps: Frames per second
            output_dir: Directory to save the video
            job_id: Unique job identifier
            progress_callback: Function to call with progress updates

        Returns:
            Path to the generated video file
        """
        print(f"\n[VideoGenerator] Starting generation")
        print(f"[VideoGenerator] Model: {model}")
        print(f"[VideoGenerator] Prompt: {prompt[:80]}...")

        if not self.api_token:
            print("[VideoGenerator] ✗ ERROR: No API token")
            raise ValueError("REPLICATE_API_TOKEN not set. Please configure your API key.")

        if model not in self.models:
            print(f"[VideoGenerator] ✗ ERROR: Unknown model: {model}")
            raise ValueError(f"Unknown model: {model}. Available models: {list(self.models.keys())}")

        model_info = self.models[model]
        print(f"[VideoGenerator] Using {model_info['name']}")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        print(f"[VideoGenerator] Output directory: {output_dir}")

        if progress_callback:
            progress_callback(20)

        try:
            # Generate video based on model type
            print(f"[VideoGenerator] Calling model-specific generator...")
            if model == 'animate-diff':
                output = self._generate_animate_diff(prompt, progress_callback)
            elif model == 'text2video-zero':
                output = self._generate_text2video_zero(prompt, progress_callback)
            elif model == 'stable-video-diffusion':
                output = self._generate_stable_video_diffusion(prompt, progress_callback)
            else:
                raise ValueError(f"Model {model} not implemented yet")

            print(f"[VideoGenerator] Model returned output: {type(output)}")

            if progress_callback:
                progress_callback(90)

            # Download the video
            video_path = os.path.join(output_dir, f'{job_id or "video"}.mp4')
            print(f"[VideoGenerator] Downloading video to: {video_path}")
            self._download_video(output, video_path)

            if progress_callback:
                progress_callback(100)

            print(f"[VideoGenerator] ✓ Generation complete: {video_path}")
            return video_path

        except Exception as e:
            print(f"[VideoGenerator] ✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Video generation failed: {str(e)}")

    def _generate_animate_diff(self, prompt, progress_callback=None):
        """Generate video using AnimateDiff"""
        print(f"[VideoGenerator] AnimateDiff: Starting generation")

        if progress_callback:
            progress_callback(30)

        print(f"[VideoGenerator] AnimateDiff: Calling Replicate API...")
        output = replicate.run(
            self.models['animate-diff']['model_id'],
            input={
                "prompt": prompt,
                "guidance_scale": 7.5,
                "num_inference_steps": 25,
            }
        )

        print(f"[VideoGenerator] AnimateDiff: API call completed")
        if progress_callback:
            progress_callback(80)

        return output

    def _generate_text2video_zero(self, prompt, progress_callback=None):
        """Generate video using Text2Video-Zero"""
        if progress_callback:
            progress_callback(30)

        output = replicate.run(
            self.models['text2video-zero']['model_id'],
            input={
                "prompt": prompt,
                "video_length": 8,
            }
        )

        if progress_callback:
            progress_callback(80)

        return output

    def _generate_stable_video_diffusion(self, prompt, progress_callback=None):
        """
        Generate video using Stable Video Diffusion
        Note: This model requires an input image, so we'll need to generate one first
        """
        if progress_callback:
            progress_callback(30)

        # First, generate an image from the prompt using Stable Diffusion
        image_output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={"prompt": prompt}
        )

        if progress_callback:
            progress_callback(50)

        # Get the first image URL
        if isinstance(image_output, list):
            image_url = image_output[0]
        else:
            image_url = image_output

        # Now generate video from the image
        output = replicate.run(
            self.models['stable-video-diffusion']['model_id'],
            input={
                "input_image": image_url,
                "cond_aug": 0.02,
                "decoding_t": 14,
                "video_length": "14_frames_with_svd",
                "sizing_strategy": "maintain_aspect_ratio",
                "motion_bucket_id": 127,
                "frames_per_second": 6
            }
        )

        if progress_callback:
            progress_callback(80)

        return output

    def _download_video(self, output, output_path):
        """Download video from URL to local file"""
        print(f"[VideoGenerator] Downloading video...")

        # Handle different output formats
        if isinstance(output, str):
            video_url = output
        elif isinstance(output, list) and len(output) > 0:
            video_url = output[0]
        else:
            print(f"[VideoGenerator] ✗ ERROR: Unexpected output format: {type(output)}")
            raise ValueError(f"Unexpected output format: {type(output)}")

        print(f"[VideoGenerator] Video URL: {video_url}")
        print(f"[VideoGenerator] Downloading...")

        # Download the video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    if percent % 10 < 1:  # Print every ~10%
                        print(f"[VideoGenerator] Download progress: {percent:.1f}%")

        file_size = os.path.getsize(output_path)
        print(f"[VideoGenerator] ✓ Download complete: {file_size / 1024:.1f} KB")

        return output_path


# Demo/test function
if __name__ == '__main__':
    generator = VideoGenerator()

    print("Available models:")
    for model in generator.get_available_models():
        print(f"  - {model['id']}: {model['name']}")

    print("\nGenerating test video...")
    try:
        video_path = generator.generate(
            prompt="A serene sunset over the ocean with gentle waves",
            model='animate-diff',
            job_id='test'
        )
        print(f"Video generated: {video_path}")
    except Exception as e:
        print(f"Error: {e}")
