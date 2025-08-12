---
title: Darzi FastAPI Backend
emoji: 📃
colorFrom: green
colorTo: yellow
sdk: docker
---


# Backend API
This directory contains the source code for the backend API, built using FastAPI.

## Features
- **Resume Parsing**: Extract structured data from PDF resumes and plain text
- **Hybrid Parsing**: Uses both local spaCy-based parser and MCP server for enhanced results
- **Multiple Input Formats**: Supports both PDF file uploads and raw text input

### Important Links
- HuggingFace Repo: [https://huggingface.co/spaces/VIT-Bhopal-AI-Innovators-Hub/darzi-api-server](https://huggingface.co/spaces/VIT-Bhopal-AI-Innovators-Hub/darzi-api-server)
- Deployment Link: [https://vit-bhopal-ai-innovators-hub-darzi-api-server.hf.space](https://vit-bhopal-ai-innovators-hub-darzi-api-server.hf.space)

## API Endpoints

### `/parse` (POST)
Parse plain text resume data.
- **Input**: Raw text (Content-Type: text/plain)
- **Output**: Hybrid parsing results from both local parser and MCP server

### `/parse-pdf` (POST) 
Parse PDF resume file.
- **Input**: PDF file upload (multipart/form-data)
- **Output**: Structured resume data extracted from PDF

## Setup

### Local Development

1. Install dependencies:
```bash
# Using uv (recommended)
uv sync
uv run python -m spacy download en_core_web_sm

# Or using pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. Run the server:
```bash
python main.py
# Server will be available at http://localhost:7860
```

### Testing the API

#### Test Text Parsing:
```bash
curl -X POST http://localhost:7860/parse \
  -H "Content-Type: text/plain" \
  -d "John Doe. Email: john.doe@example.com. Phone: 1234567890. Python developer with 5 years experience at Google."
```

#### Test PDF Parsing:
```bash
# Replace 'path/to/your/resume.pdf' with your actual PDF file path
curl -X POST http://localhost:7860/parse-pdf \
  -F 'file=@path/to/your/resume.pdf'

# Example paths:
curl -X POST http://localhost:7860/parse-pdf -F 'file=@~/Downloads/resume.pdf'
curl -X POST http://localhost:7860/parse-pdf -F 'file=@~/Desktop/my_resume.pdf'
```

#### Expected Response Format:
```json
{
  "filename": "resume.pdf",
  "parsing_result": {
    "name": "John Doe",
    "email": ["john.doe@example.com"],
    "mobile_number": ["1234567890"],
    "skills": ["Python", "JavaScript", "React"],
    "education": ["Bachelor of Science", "University Name"],
    "experience": [{"title": "Software Engineer", "company": "Google"}],
    "raw_text": "First 500 characters of extracted text..."
  },
  "source": "local_parser"
}
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t darzi-backend-api .
```

2. Run the Docker container:
```bash
docker run -p 7860:7860 darzi-backend-api
```

3. Access the API at `http://localhost:7860/`.