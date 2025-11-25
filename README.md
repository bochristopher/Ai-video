# AI Video Generator

A web application that generates AI videos based on text prompts using various AI video generation models.

## Features

- 🎬 Generate videos from text prompts
- 🎨 Support for multiple AI video generation models
- 💾 Download generated videos
- 🌐 Simple web interface
- 📊 Real-time generation status

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI Models**: Replicate API (Stable Video Diffusion, AnimateDiff, etc.)

## Setup

### Prerequisites

- Python 3.8+
- Replicate API key (or other video generation service API key)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Ai-video
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Add your API keys to `.env`:
```
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

### Running the Application

1. Start the backend server:
```bash
python backend/app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter a text prompt describing the video you want to generate
2. (Optional) Adjust generation parameters
3. Click "Generate Video"
4. Wait for the video to be generated
5. Preview and download your video

## Supported Video Models

- Stable Video Diffusion
- AnimateDiff
- Text-to-Video models via Replicate

## API Endpoints

- `POST /api/generate` - Generate a video from a prompt
- `GET /api/status/<job_id>` - Check generation status
- `GET /api/video/<video_id>` - Retrieve generated video
- `GET /api/jobs` - List all jobs
- `GET /api/models` - List available models
- `GET /health` - Health check

## Testing

The project includes comprehensive tests:

### Unit Tests
- Backend API endpoint tests
- Video generator logic tests
- Mock external dependencies

### Integration Tests
- End-to-end workflow tests
- Multi-job handling
- Error scenarios

### UI Tests
- Selenium-based browser tests
- Playwright tests (alternative)
- Form interactions
- Responsive design
- Accessibility checks

### Running Tests

**All tests:**
```bash
./run_tests.sh
```

**Specific test suite:**
```bash
python tests/test_app.py          # API tests
python tests/test_video_generator.py  # Generator tests
python tests/test_integration.py  # Integration tests
python tests/test_ui.py           # UI tests (Selenium)
python tests/test_ui_playwright.py  # UI tests (Playwright)
```

**Install UI test dependencies:**
```bash
# For Selenium
pip install selenium
# Install ChromeDriver or Firefox GeckoDriver

# For Playwright
pip install playwright
playwright install chromium
```

## Logging and Debugging

The application includes comprehensive logging:

- **Backend**: Initialization, requests, progress, errors with tracebacks
- **Frontend**: API calls, status updates, user actions in browser console
- **Format**: `[Component] Message` with ✓ and ✗ indicators

View logs in terminal (backend) or browser console (frontend).

## Configuration

Edit `.env` to configure:
- API keys (REPLICATE_API_TOKEN)
- Server settings (PORT, HOST)
- Video parameters (resolution, duration, fps)
- Storage settings

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design, data flow, and implementation details.

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
