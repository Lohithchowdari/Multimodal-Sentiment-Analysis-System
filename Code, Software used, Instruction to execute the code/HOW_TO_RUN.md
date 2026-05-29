# How to Run This Project

## 1) Prerequisites

- Python 3.10 or newer
- `pip` (Python package manager)
- Tesseract OCR installed and added to PATH
- FFmpeg installed and added to PATH (needed by `pydub`)

## 2) Create and activate virtual environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3) Install required packages

If you already have a requirements file, install with:

```powershell
pip install -r requirements.txt
```

If not, install the core dependencies manually:

```powershell
pip install flask flask-login flask-sqlalchemy flask-mail python-dotenv groq pytz pillow pytesseract speechrecognition pydub
```

## 4) Configure environment variables

Create a `.env` file in the project root and add:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///multimodal_sentiment.db
GROQ_API_KEY=your_groq_api_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password_or_app_password
ADMIN_USERNAME=lohith
ADMIN_PASSWORD=8978188900
APP_NAME=MindSync AI
```

## 5) Run the application

```powershell
python app.py
```

The app will start on:

- `http://127.0.0.1:5000`
- `http://localhost:5000`

## 6) Notes

- Database tables are created automatically at startup.
- For OCR to work, Tesseract must be installed correctly.
- For audio transcription to work well, FFmpeg should be available in system PATH.
