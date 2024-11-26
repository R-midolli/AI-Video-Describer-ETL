# AI Video Describer

## Overview

AI Video Describer is a tool that automates the process of extracting video content from YouTube, generating AI-powered descriptions, and logging the video details to a Notion database.

## Features

- 🎥 Download YouTube videos using `yt-dlp`
- 🤖 AI-powered video description generation with Google Gemini
- 📝 Automatic title extraction
- 🗂️ Video details exported to Notion database

## Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`
- API Keys:
  - Google Gemini API
  - Notion API

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/ai-video-describer.git
   cd ai-video-describer
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure Environment Variables
   Create a `.env` file in the project root with the following:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   NOTION_API_KEY=your_notion_api_key
   NOTION_DATABASE_ID=your_notion_database_id
   ```

## Usage

Run the script and input a YouTube video URL:

```bash
python main.py
```

### Workflow

1. Enter a YouTube video URL
2. Video is downloaded
3. AI generates a description and extracts the title
4. Prompt to keep or delete the video
5. Video details (title, publication date, description) exported to Notion

## Configuration

- Adjust `generation_config` in the script to modify AI behavior
- Customize Notion database properties as needed

## Dependencies

- `yt-dlp`: YouTube video downloading
- `google-generativeai`: AI content generation
- `python-dotenv`: Environment variable management
- `requests`: Notion API interactions

## Security

- Never commit API keys to version control
- Use environment variables or secure secret management

## Limitations

- Requires active internet connection
- Depends on YouTube video accessibility
- AI description quality varies by content

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Rafael Midolli - rbmidolli@gmail.com

Project Link: [https://github.com/R-midolli/AI-Video-Describer-ETL](https://github.com/R-midolli/AI-Video-Describer-ETL)
