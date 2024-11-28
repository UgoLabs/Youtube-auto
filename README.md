# AI YouTube Video Generator

An automated YouTube video generator that creates, edits, and uploads videos using AI. The application uses GPT-4 for script generation, Stability AI for image generation, and various APIs for text-to-speech and video composition.

## Features

- 🤖 **AI-powered script generation** using GPT-4
- 🎨 **Image generation** using Stability AI
- 🎤 **Text-to-speech conversion**
- 🎬 **Automatic video composition**
- 📈 **Google Trends integration** for topic selection
- 📤 **Direct YouTube upload capability**
- 🖥️ **User-friendly GUI interface**

## Prerequisites

- Python 3.8+
- OpenAI API key
- Stability AI API key
- YouTube API credentials
- Required Python packages (see `requirements.txt`)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/Youtube_auto.git
   cd Youtube_auto
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the root directory with your API keys:**

   ```env
   OPENAI_API_KEY=your_openai_key_here
   IMAGE_API_KEY=your_stability_ai_key_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   YOUTUBE_CLIENT_ID=your_youtube_client_id_here
   YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
   ```

## Usage

1. **Run the application:**

   ```bash
   python main.py
   ```

2. **Enter a topic or click "Get Trending Topics."
3. **Click "Generate Video" to start the process.**
4. **Once complete, you can save locally or upload to YouTube.**

## Project Structure

```text
Youtube_auto/
├── main.py                # Main application file
├── requirements.txt       # Python dependencies
├── .env                   # API keys and configuration
├── utils/
│   ├── __init__.py
│   ├── logging_utils.py
│   └── youtube_utils.py
├── scripts/
│   ├── __init__.py
│   └── gui.py
└── output/                # Generated files directory
    ├── audio/
    ├── images/
    └── videos/
```

## Configuration

### Required API Keys

- OpenAI API key for GPT-4
- Stability AI API key for image generation
- YouTube API credentials for uploading

### YouTube API Setup

1. Create a project in Google Cloud Console.
2. Enable the YouTube Data API v3.
3. Create OAuth 2.0 credentials.
4. Download the client secrets file.
5. Place it in the project root as `client_secrets.json`.

## Contributing

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. Commit your changes:

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

4. Push to the branch:

   ```bash
   git push origin feature/AmazingFeature
   ```

5. Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- OpenAI GPT-4 for script generation
- Stability AI for image generation
- Google Text-to-Speech for audio conversion
- MoviePy for video editing
