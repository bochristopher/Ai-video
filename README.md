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

## Configuration

Edit `.env` to configure:
- API keys
- Model selection
- Video parameters (resolution, duration, fps)

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
