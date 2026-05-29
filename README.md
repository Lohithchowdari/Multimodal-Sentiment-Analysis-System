# 🧠 MindSync AI

## AI-Powered Multimodal Sentiment Analysis & Mental Wellbeing Support System

MindSync AI is a Flask-based web application that performs **multimodal sentiment analysis** using Artificial Intelligence. The platform analyzes **Text, Images, and Audio** inputs to determine emotional sentiment and provides supportive recommendations for users.

The system integrates **Groq LLM, OCR, Speech Recognition, and Email Notification Services** to create a comprehensive mental wellbeing support platform.

---

## 🚀 Features

### 📝 Text Sentiment Analysis
- Analyze user-entered text
- Detect Positive, Neutral, or Negative sentiment
- Generate AI-powered suggestions

### 🖼️ Image Sentiment Analysis
- Extract text from images using OCR
- Analyze extracted text sentiment
- Support various image formats

### 🎤 Audio Sentiment Analysis
- Convert speech to text
- Analyze emotional tone from voice transcripts
- Provide sentiment insights

### 👤 User Authentication
- User Registration
- Secure Login
- Session Management
- Password Hashing

### 📊 Analytics Dashboard
- Sentiment Statistics
- Historical Analysis
- Trend Visualization
- User Activity Monitoring

### 📧 Email Notification System
- Automated support emails
- Triggered for negative sentiment detections
- Mental wellbeing guidance

### 🔐 Admin Dashboard
- User Management
- Analytics Monitoring
- Prediction History Tracking

---

# 🏗️ System Architecture

```text
                ┌───────────────┐
                │    User       │
                └───────┬───────┘
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼

   Text Input      Image Input      Audio Input
       │                │                │
       ▼                ▼                ▼
   Groq LLM       Tesseract OCR    Speech Recognition
       │                │                │
       └──────────┬─────┴─────┬──────────┘
                  │
                  ▼
       Sentiment Classification
                  │
                  ▼
       Positive / Neutral / Negative
                  │
                  ▼
          Database Storage
                  │
                  ▼
         Analytics Dashboard
```

---

# 🛠️ Tech Stack

## Backend
- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Mail

## Database
- SQLite

## Artificial Intelligence
- Groq API
- Llama 3.1 8B Instant

## OCR
- Tesseract OCR
- pytesseract
- Pillow

## Speech Recognition
- SpeechRecognition
- pydub
- FFmpeg

## Frontend
- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

## Utilities
- python-dotenv
- pytz

---

# 📂 Project Structure

```text
MindSync-AI/
│
├── app.py
├── config.py
├── models.py
├── services.py
├── requirements.txt
├── .env
│
├── uploads/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── analytics.html
│   └── ...
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/MindSync-AI.git

cd MindSync-AI
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a file named:

```text
.env
```

Add:

```env
SECRET_KEY=your_secret_key

DATABASE_URL=sqlite:///multimodal_sentiment.db

GROQ_API_KEY=your_groq_api_key

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin_password
```

---

## Run Application

```bash
python app.py
```

Open browser:

```text
http://localhost:5000
```

---

# 📈 Sentiment Categories

| Sentiment | Description |
|------------|-------------|
| Positive | Happy, Motivated, Optimistic |
| Neutral | Informational, Balanced |
| Negative | Stress, Anxiety, Sadness |

---

# 🔄 Workflow

### Text Analysis

```text
User Text
    ↓
Groq AI
    ↓
Sentiment Prediction
    ↓
Store Result
    ↓
Show Recommendation
```

### Image Analysis

```text
Image Upload
     ↓
OCR Extraction
     ↓
Text Content
     ↓
Groq AI
     ↓
Sentiment Prediction
```

### Audio Analysis

```text
Audio Recording
       ↓
Speech-to-Text
       ↓
Text Content
       ↓
Groq AI
       ↓
Sentiment Prediction
```

---

# 🔒 Security Features

- Password Hashing
- Session Authentication
- Secure Login Management
- Environment Variable Configuration
- Role-Based Admin Access

---

# 🎯 Future Enhancements

- Deep Learning Models
- Real-Time Emotion Detection
- Face Emotion Recognition
- Multi-Language Support
- Cloud Deployment
- Mobile Application

---

# 💡 Real-World Applications

- Mental Health Monitoring
- Student Wellbeing Systems
- Employee Sentiment Tracking
- Customer Feedback Analysis
- Social Media Monitoring
- AI Wellness Assistants

---

# 👨‍💻 Author

### DUPATI LOHITH CHOWDARI

B.Tech Computer Science Engineering

SRM Institute of Science and Technology

GitHub: https://github.com/Lohithchowdari

LinkedIn: www.linkedin.com/in/lohithchowdari

---

# ⭐ If you found this project useful, please give it a star.
