# PDF Password Remover

A batch PDF password removal tool with both a modern web interface and CLI support. Built with FastAPI for easy cloud deployment.

## Features

- 🔓 Remove passwords from multiple PDFs at once
- 🌐 Beautiful drag-and-drop web interface
- 💻 Command-line interface for automation
- 📦 Download all processed files as ZIP
- ⚡ Fast processing with pikepdf
- ☁️ Ready to deploy on Render (free tier)

## Live Demo

Deploy your own instance on Render with one click:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Local Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Web Interface (Local)

```bash
python app.py
```

Then open http://localhost:8000 in your browser.

### Command Line

```bash
# Single file
python cli.py --password "yourpassword" input.pdf

# Multiple files with same password
python cli.py --password "yourpassword" file1.pdf file2.pdf file3.pdf

# Entire folder
python cli.py --password "yourpassword" --input-dir ./encrypted_pdfs

# Custom output directory
python cli.py --password "yourpassword" --output-dir ./unlocked input.pdf
```

## Deploy to Render (Free Tier)

### Option 1: One-Click Deploy

1. Push this repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **New** → **Web Service**
4. Connect your GitHub repo
5. Render will auto-detect settings from `render.yaml`
6. Click **Create Web Service**

### Option 2: Manual Setup

1. Create a new **Web Service** on Render
2. Connect your GitHub repository
3. Configure:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Select the **Free** plan
5. Deploy!

### Environment

The app uses these defaults on Render:
- Python 3.11
- Health check endpoint: `/health`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/unlock` | POST | Process PDFs (multipart form) |
| `/download/{session_id}` | GET | Download processed files |
| `/health` | GET | Health check |

## Notes

- You must know the password to remove it (this tool doesn't crack passwords)
- Original files are never modified
- Processed files are saved with `_unlocked` suffix
- Files are processed in memory and not stored permanently

## License

MIT
