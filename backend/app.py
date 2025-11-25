import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from video_generator import VideoGenerator
import threading

# Load environment variables
load_dotenv()
print("=" * 60)
print("AI VIDEO GENERATOR - INITIALIZING")
print("=" * 60)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
print("[✓] Flask app initialized with CORS enabled")

# Configuration
VIDEO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)
print(f"[✓] Video output directory: {VIDEO_DIR}")

# In-memory storage for job status (in production, use Redis or a database)
jobs = {}
print("[✓] In-memory job storage initialized")

# Initialize video generator
try:
    video_generator = VideoGenerator()
    print("[✓] Video generator initialized successfully")
except Exception as e:
    print(f"[✗] Failed to initialize video generator: {e}")
    video_generator = None

@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """
    Generate a video from a text prompt
    Expected JSON: {
        "prompt": "description of video",
        "model": "stable-video-diffusion" (optional),
        "duration": 3 (optional, seconds),
        "fps": 24 (optional)
    }
    """
    print("\n" + "=" * 60)
    print("NEW VIDEO GENERATION REQUEST")
    print("=" * 60)

    try:
        data = request.get_json()
        print(f"[DEBUG] Request data: {json.dumps(data, indent=2)}")

        if not data or 'prompt' not in data:
            print("[✗] ERROR: Prompt is required")
            return jsonify({'error': 'Prompt is required'}), 400

        prompt = data['prompt']
        model = data.get('model', 'stable-video-diffusion')
        duration = int(data.get('duration', 3))
        fps = int(data.get('fps', 24))

        print(f"[✓] Prompt: {prompt[:100]}...")
        print(f"[✓] Model: {model}")
        print(f"[✓] Duration: {duration}s | FPS: {fps}")

        # Create a unique job ID
        job_id = str(uuid.uuid4())
        print(f"[✓] Generated Job ID: {job_id}")

        # Initialize job status
        jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'prompt': prompt,
            'model': model,
            'created_at': datetime.now().isoformat(),
            'progress': 0,
            'video_url': None,
            'error': None
        }

        # Start video generation in background thread
        print(f"[✓] Starting background thread for job {job_id}")
        thread = threading.Thread(
            target=generate_video_async,
            args=(job_id, prompt, model, duration, fps)
        )
        thread.daemon = True
        thread.start()
        print(f"[✓] Background thread started successfully")

        print("=" * 60)
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Video generation started'
        }), 202

    except Exception as e:
        print(f"[✗] ERROR in /api/generate: {str(e)}")
        print("=" * 60)
        return jsonify({'error': str(e)}), 500

def generate_video_async(job_id, prompt, model, duration, fps):
    """Background task to generate video"""
    print(f"\n[THREAD {job_id}] Starting video generation")
    print(f"[THREAD {job_id}] Prompt: {prompt[:80]}...")
    print(f"[THREAD {job_id}] Model: {model}")

    try:
        # Update status to processing
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 10
        print(f"[THREAD {job_id}] Status: PROCESSING (10%)")

        # Generate video
        def progress_callback(progress):
            jobs[job_id]['progress'] = progress
            print(f"[THREAD {job_id}] Progress: {progress}%")

        print(f"[THREAD {job_id}] Calling video generator...")
        video_path = video_generator.generate(
            prompt=prompt,
            model=model,
            duration=duration,
            fps=fps,
            output_dir=VIDEO_DIR,
            job_id=job_id,
            progress_callback=progress_callback
        )
        print(f"[THREAD {job_id}] Video generated at: {video_path}")

        # Update job status
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['video_url'] = f'/api/video/{job_id}'
        jobs[job_id]['video_path'] = video_path
        jobs[job_id]['completed_at'] = datetime.now().isoformat()

        print(f"[THREAD {job_id}] ✓ COMPLETED SUCCESSFULLY")
        print(f"[THREAD {job_id}] Video URL: {jobs[job_id]['video_url']}")

    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)
        print(f"[THREAD {job_id}] ✗ FAILED")
        print(f"[THREAD {job_id}] Error: {str(e)}")
        import traceback
        print(f"[THREAD {job_id}] Traceback:")
        traceback.print_exc()

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get the status of a video generation job"""
    print(f"[API] Status check for job: {job_id}")

    if job_id not in jobs:
        print(f"[API] Job not found: {job_id}")
        return jsonify({'error': 'Job not found'}), 404

    job = jobs[job_id].copy()
    print(f"[API] Job status: {job['status']} ({job.get('progress', 0)}%)")

    # Don't expose internal file paths
    if 'video_path' in job:
        del job['video_path']

    return jsonify(job)

@app.route('/api/video/<job_id>', methods=['GET'])
def get_video(job_id):
    """Download or stream a generated video"""
    print(f"[API] Video download requested for job: {job_id}")

    if job_id not in jobs:
        print(f"[API] Job not found: {job_id}")
        return jsonify({'error': 'Job not found'}), 404

    job = jobs[job_id]

    if job['status'] != 'completed':
        print(f"[API] Video not ready, status: {job['status']}")
        return jsonify({'error': 'Video not ready yet'}), 404

    if 'video_path' not in job or not os.path.exists(job['video_path']):
        print(f"[API] Video file not found at path: {job.get('video_path', 'N/A')}")
        return jsonify({'error': 'Video file not found'}), 404

    print(f"[API] Sending video file: {job['video_path']}")
    return send_file(
        job['video_path'],
        mimetype='video/mp4',
        as_attachment=True,
        download_name=f'ai_video_{job_id}.mp4'
    )

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all video generation jobs"""
    jobs_list = []
    for job in jobs.values():
        job_copy = job.copy()
        if 'video_path' in job_copy:
            del job_copy['video_path']
        jobs_list.append(job_copy)

    # Sort by creation time, most recent first
    jobs_list.sort(key=lambda x: x['created_at'], reverse=True)

    return jsonify({'jobs': jobs_list})

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available video generation models"""
    return jsonify({
        'models': video_generator.get_available_models()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print("\n" + "=" * 60)
    print("STARTING SERVER")
    print("=" * 60)
    print(f"[✓] Host: {host}")
    print(f"[✓] Port: {port}")
    print(f"[✓] Debug mode: {debug}")
    print(f"[✓] Video output directory: {VIDEO_DIR}")
    print(f"[✓] Available models: {len(video_generator.get_available_models() if video_generator else [])}")
    print("=" * 60)
    print(f"\n🌐 Open your browser to: http://localhost:{port}")
    print("=" * 60 + "\n")

    app.run(host=host, port=port, debug=debug, threaded=True)
