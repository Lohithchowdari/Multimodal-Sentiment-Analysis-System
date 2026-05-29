# Software and Technologies Used

This project is a **Flask-based web application** for multimodal sentiment analysis (text, image, and audio).

## Core Language

- Python

## Backend Framework

- Flask

## Authentication and Session

- Flask-Login

## Database

- SQLite (default via SQLAlchemy URI)
- Flask-SQLAlchemy (ORM layer)

## AI / NLP

- Groq API (model used in code: `llama-3.1-8b-instant`)

## Image Processing / OCR

- Pillow (PIL)
- pytesseract
- Tesseract OCR engine (system software)

## Audio Processing / Speech-to-Text

- SpeechRecognition
- pydub
- FFmpeg (system software used by pydub)

## Email Notifications

- Flask-Mail
- SMTP (configured for Gmail in settings)

## Configuration / Environment

- python-dotenv (`.env` loading)
- pytz (timezone handling)

## Frontend (Template Layer)

- Jinja2 templates (via Flask `render_template`)
- HTML/CSS/JavaScript (in template/static files)
