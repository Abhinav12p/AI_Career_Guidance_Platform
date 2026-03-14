# AI-Powered Career Guidance Platform, Streamlit Version

This project is a Streamlit based career guidance platform with six tabs:
- Discover Careers
- Market Analysis
- Learning Roadmap
- Career Insights
- Chat Assistant
- History

## Features
- Works on `localhost:8501`
- Streamlit UI similar to modern dashboard apps
- Discover Careers works without any external API key
- Market Analysis uses SerpAPI for live Google Jobs research
- Learning Roadmap uses Gemini
- Career Insights uses Gemini
- Chat Assistant uses Gemini
- History saves actions locally in `data/history.json`

## Setup
```bash
python -m venv .venv
```

Windows PowerShell:
```bash
.venv\Scripts\Activate.ps1
```

Windows CMD:
```bash
.venv\Scripts\activate.bat
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run:
```bash
streamlit run app.py
```

Or use:
```bash
run.bat
```

## Open in browser
`http://localhost:8501`

## API keys
- Gemini API key for Roadmap, Insights, Chat Assistant
- SerpAPI key for Market Analysis

## Notes
- API keys are entered in the sidebar for the current session.
- If API keys are missing, only Discover Careers and History will work.
