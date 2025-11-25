# AI Video Generator - Architecture

## Overview

This application generates AI videos from text prompts using various video generation models through the Replicate API.

## Project Structure

```
Ai-video/
├── backend/
│   ├── app.py              # Flask API server
│   └── video_generator.py  # Video generation logic
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── tests/
│   ├── __init__.py
│   ├── test_app.py         # Flask API unit tests
│   ├── test_video_generator.py  # Generator unit tests
│   ├── test_integration.py # Integration tests
│   └── run_tests.py        # Test runner
├── videos/                 # Generated videos storage
├── .env                    # Environment variables (not in git)
├── .env.example            # Environment template
├── .gitignore
├── requirements.txt        # Python dependencies
├── setup.sh                # Setup script
├── run.sh                  # Run server script
├── run_tests.sh            # Test runner script
├── README.md               # Documentation
└── ARCHITECTURE.md         # This file
```

## Components

### Backend (Python + Flask)

#### app.py
- **REST API Server**: Flask application serving both API and frontend
- **Job Management**: Tracks video generation jobs with status and progress
- **Background Processing**: Async video generation using threads
- **Endpoints**:
  - `GET /` - Serve frontend
  - `POST /api/generate` - Start video generation
  - `GET /api/status/<job_id>` - Check generation status
  - `GET /api/video/<job_id>` - Download video
  - `GET /api/jobs` - List all jobs
  - `GET /api/models` - List available models
  - `GET /health` - Health check

#### video_generator.py
- **VideoGenerator Class**: Handles AI video generation
- **Multi-Model Support**: AnimateDiff, Stable Video Diffusion, Text2Video-Zero
- **Replicate Integration**: Interfaces with Replicate API
- **Progress Tracking**: Callback system for progress updates
- **Video Download**: Fetches and saves generated videos

### Frontend (HTML + CSS + JavaScript)

#### index.html
- Modern, responsive UI
- Form for prompt input and configuration
- Real-time status updates
- Video preview and download
- Recent jobs list
- Example prompts

#### style.css
- Modern gradient background
- Card-based layout
- Responsive design
- Status badges and progress bars
- Mobile-friendly

#### script.js
- API communication
- Status polling
- Progress updates
- Video preview
- Error handling
- Console logging for debugging

## Data Flow

1. **User Input**: User enters prompt and parameters in frontend
2. **API Request**: POST to `/api/generate` with prompt data
3. **Job Creation**: Server creates job with unique ID, returns 202 Accepted
4. **Background Processing**: Thread spawned to generate video
5. **Progress Updates**: Frontend polls `/api/status/<job_id>` every 2 seconds
6. **Video Generation**:
   - Call Replicate API with model and prompt
   - Track progress via callbacks
   - Download generated video
7. **Completion**: Job status updated to 'completed' with video URL
8. **Video Delivery**: Frontend displays video, user can download

## State Management

### Job States
- `queued`: Job created, waiting to start
- `processing`: Video generation in progress
- `completed`: Video ready, available for download
- `failed`: Error occurred during generation

### Job Data Structure
```python
{
    'id': str,              # Unique job ID
    'status': str,          # Current status
    'prompt': str,          # User's prompt
    'model': str,           # Model used
    'created_at': str,      # ISO timestamp
    'completed_at': str,    # ISO timestamp (if completed)
    'progress': int,        # 0-100
    'video_url': str,       # API endpoint for video
    'video_path': str,      # Server file path (internal)
    'error': str            # Error message (if failed)
}
```

## API Models

### Supported Models

1. **AnimateDiff** (Recommended)
   - Text-to-video animation
   - No input image required
   - Fast generation

2. **Stable Video Diffusion**
   - High-quality videos from images
   - Requires image generation first
   - Slower but higher quality

3. **Text2Video-Zero**
   - Zero-shot text-to-video
   - Experimental

## Logging

### Backend Logging
- Initialization messages with checkmarks
- Request/response logging
- Thread-based job tracking
- Progress updates
- Error messages with tracebacks
- Download progress

### Frontend Logging
- API calls and responses
- Job status changes
- Progress updates
- Error messages
- User actions

### Log Format
```
[Component] Message
[✓] Success message
[✗] Error message
[DEBUG] Debug information
[THREAD job_id] Thread-specific messages
```

## Testing

### Unit Tests
- **test_app.py**: Flask API endpoint tests
- **test_video_generator.py**: Video generator logic tests
- Mock external dependencies (Replicate API, file operations)
- Test error handling and edge cases

### Integration Tests
- **test_integration.py**: End-to-end workflow tests
- Complete video generation workflow
- Multi-job handling
- Error scenarios
- Progress tracking

### Running Tests
```bash
./run_tests.sh
# or
python tests/run_tests.py
```

## Configuration

### Environment Variables (.env)
```bash
# Required
REPLICATE_API_TOKEN=your_token_here

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
MAX_VIDEO_DURATION=10
DEFAULT_FPS=24
DEFAULT_WIDTH=512
DEFAULT_HEIGHT=512
```

## Security Considerations

1. **API Keys**: Stored in .env, never committed to git
2. **CORS**: Enabled for frontend access
3. **Input Validation**: Prompt and parameters validated
4. **File Storage**: Videos stored in dedicated directory
5. **Job Isolation**: Each job has unique ID

## Performance

- **Async Processing**: Background threads for video generation
- **Polling**: 2-second intervals for status checks
- **Streaming**: Large video files streamed, not loaded into memory
- **Caching**: Replicate API handles model caching

## Error Handling

- API errors return JSON with error message
- Frontend displays user-friendly error messages
- Backend logs full tracebacks
- Failed jobs marked with error details
- Retry capability for failed generations

## Future Enhancements

1. **Database**: Replace in-memory job storage with Redis/PostgreSQL
2. **WebSockets**: Real-time progress updates instead of polling
3. **Queue System**: Celery for better job management
4. **Authentication**: User accounts and API keys
5. **Storage**: Cloud storage (S3) for videos
6. **Caching**: Cache popular prompts/videos
7. **Rate Limiting**: Prevent API abuse
8. **Analytics**: Track usage and performance metrics
