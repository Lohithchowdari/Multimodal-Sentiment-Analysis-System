# AI Project Guide - MindSync AI

## Purpose

MindSync AI is a Flask web app for **multimodal sentiment analysis** focused on emotional wellbeing support.
Users can submit:

- text input
- image input (OCR -> text)
- audio input (speech-to-text -> text)

The system classifies sentiment as `positive`, `neutral`, or `negative`, stores results, and can send support emails for negative outcomes.

---

## Scope of This Guide

This guide is based on reading the project source files in the workspace root:

- `app.py`
- `config.py`
- `models.py`
- `services.py`
- `templates/*`
- `static/js/main.js`
- `static/css/style.css`
- `HOW_TO_RUN.md`
- `SOFTWARE_USED.md`

It intentionally excludes virtual environment internals (`.venv`) and binary assets (`.jpg`, `.png`) because they do not define application logic.

---

## Tech Stack

- **Backend:** Flask
- **Auth/session:** Flask-Login + Flask session
- **ORM/database:** Flask-SQLAlchemy (default SQLite)
- **AI model API:** Groq (`llama-3.1-8b-instant`)
- **OCR:** Pillow + pytesseract (+ system Tesseract)
- **Speech-to-text:** SpeechRecognition + pydub (+ system FFmpeg)
- **Mail:** Flask-Mail with SMTP
- **Frontend:** Jinja templates, custom CSS, vanilla JS, Chart.js
- **Timezone:** pytz (`Asia/Kolkata`)

---

## High-Level Architecture

### 1) Entry and app bootstrapping (`app.py`)

- Creates Flask app and loads `Config`.
- Initializes DB (`db.init_app`) and mail (`mail.init_app`).
- Initializes Flask-Login manager.
- Creates uploads directory (`uploads/`) on startup.
- Conditionally creates `groq_service` only when `GROQ_API_KEY` is set.
- Creates tables at startup with `db.create_all()` inside app context.

### 2) Data layer (`models.py`)

- `User` model: login identity and account creation timestamp.
- `Prediction` model: records analysis metadata + content + sentiment + suggestion + email status + timestamp.
- `User` -> `Prediction`: one-to-many relationship with cascade delete.

### 3) Service layer (`services.py`)

- `GroqService`: sentiment analysis + supportive email text generation.
- `OCRService`: image-to-text extraction via Tesseract.
- `AudioService`: audio conversion/transcription pipeline.
- `EmailService`: sends formatted HTML support email for negative sentiment.

### 4) Presentation layer

- Templates for landing/auth/user/admin pages under `templates/`.
- UI behavior and API interaction under `static/js/main.js`.
- Design system and responsive styling under `static/css/style.css`.

---

## Data Model Details

## `User`

- `id` (PK, int)
- `email` (unique, required)
- `password` (hashed password string)
- `created_at` (timezone-aware `Asia/Kolkata`)

## `Prediction`

- `id` (PK, int)
- `user_id` (FK -> `users.id`, required)
- `analysis_type` (`text` / `image` / `audio`)
- `input_data` (original analyzed text or extracted/transcribed text)
- `sentiment` (`positive` / `neutral` / `negative`)
- `suggestion` (AI-generated support text)
- `email_sent` (bool, default false)
- `timestamp` (timezone-aware `Asia/Kolkata`)

---

## Request/Response Flows

## Authentication

- `/register`:
  - validates email/password/confirm match
  - checks duplicate email
  - hashes password with `pbkdf2:sha256`
  - creates user
- `/login`:
  - fetches user by email
  - verifies hash
  - creates login session
- `/logout`:
  - clears Flask-Login session

## Text sentiment flow (`/text-analysis`)

1. User submits textarea content.
2. Server checks non-empty text and configured AI service.
3. Calls `GroqService.analyze_sentiment(text, "text")`.
4. Saves `Prediction`.
5. If negative:
   - sends support email via `EmailService.send_alert_email(...)`
   - sets `prediction.email_sent`.
6. Renders `text_result.html`.

## Image sentiment flow (`/image-analysis`)

1. User uploads image file.
2. Server validates uploaded file presence.
3. OCR via `OCRService.extract_text_from_image(file)`.
4. Runs sentiment analysis on extracted text.
5. Saves `Prediction` and conditionally sends support email.
6. Renders `image_result.html`.

## Audio sentiment flow (`/api/audio-analyze`)

1. Frontend records audio with `MediaRecorder` and uploads blob as `recording.wav`.
2. Backend stores temp file at `uploads/temp_audio.wav`.
3. `AudioService.transcribe_audio`:
   - attempts parse as webm/generic/wav
   - normalizes to mono 16k WAV
   - transcribes with Google recognizer
4. Backend analyzes sentiment on transcribed text.
5. Saves `Prediction`, optionally sends support email.
6. Returns JSON with success/sentiment/suggestion.
7. Deletes temp file in `finally`.

---

## Route Map

## Public routes

- `GET /` -> landing page
- `GET|POST /register` -> user registration
- `GET|POST /login` -> user login

## User-authenticated routes

- `GET /logout`
- `GET /dashboard`
- `GET|POST /text-analysis`
- `GET|POST /image-analysis`
- `GET /audio-analysis`
- `POST /api/audio-analyze` (JSON API)
- `GET /history` (paginated)
- `GET /analytics`
- `GET /api/analytics-data` (JSON API)

## Admin routes (session-based, separate from Flask-Login)

- `GET|POST /admin/login`
- `GET /admin/logout`
- `GET /admin/dashboard`
- `GET /admin/user/<int:user_id>`
- `GET /admin/api/user-analytics/<int:user_id>`

---

## Frontend Behavior

## `main.js`

- Audio recording UX:
  - 3-second countdown
  - max 30-second recording
  - upload and result rendering
- Analytics:
  - loads user timeline + distribution charts from `/api/analytics-data`
  - loads admin per-user timeline chart from `/admin/api/user-analytics/<id>`
- Image upload preview before submit.
- Auto-hide alert banners after 5 seconds.

## `style.css`

- Dark-themed design system with CSS variables.
- Reusable utility classes and card/button systems.
- Responsive grid behavior.
- Specialized styles for sentiment states, result cards, audio controls, tables, pagination.

---

## Configuration and Environment

Defined in `config.py` and `.env`:

- `SECRET_KEY`
- `DATABASE_URL` (default: `sqlite:///multimodal_sentiment.db`)
- `GROQ_API_KEY`
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`
- `APP_NAME`
- `UPLOAD_FOLDER` (default `uploads`)
- `MAX_CONTENT_LENGTH` = 16MB

---

## Key Couplings and Dependencies

- `app.py` depends on service contracts in `services.py`:
  - `analyze_sentiment(...)` returns `(sentiment, suggestion)`.
- Email alerts depend on a valid `GROQ_API_KEY` because `EmailService` creates `GroqService` again to generate email body.
- Audio processing requires both Python libs and system-level tools:
  - pydub + FFmpeg
  - SpeechRecognition network access for Google recognizer
- Image OCR requires Tesseract installed in system PATH.

---

## Current Risks / Gaps (Important for AI maintainers)

1. **Hardcoded default admin credentials in config fallback**
   - `ADMIN_USERNAME` and `ADMIN_PASSWORD` have insecure defaults.

2. **Admin auth is separate from Flask-Login and only checks `session['admin']`**
   - no role-based user model
   - no CSRF/session hardening layer visible in code

3. **Sensitive mental health data stored as plain text in `Prediction.input_data`**
   - no encryption-at-rest strategy shown

4. **Potential bug in flash category class expression in `base.html`**
   - category mapping expression is logically awkward and may not behave as intended.

5. **No explicit test suite in repo**
   - regression risk is higher for route/service changes.

6. **Broad exception handling in services**
   - useful for uptime but can hide root causes; mostly logs with `print`.

---

## How to Extend Safely (For AI Agents)

When implementing features:

1. Preserve output contract of `GroqService.analyze_sentiment` (`sentiment` lowercase + suggestion text).
2. Keep `Prediction` writes consistent across all modalities.
3. Ensure new endpoints respect auth boundaries:
   - user routes -> `@login_required`
   - admin routes -> `session['admin']` check (or migrate consistently).
4. For any UI change involving charts/audio:
   - update both templates and `static/js/main.js`.
5. For new settings:
   - add to `config.py`
   - document in setup docs.

---

## Typical End-to-End User Journey

1. User registers and logs in.
2. Lands on dashboard with summary stats + recent activity.
3. Chooses text/image/audio analysis.
4. Receives sentiment + suggestion result.
5. If negative, receives support email.
6. Can review history and analytics timeline.
7. Admin can inspect all users and per-user analytics.

---

## Quick File Responsibilities

- `app.py`: all routes and orchestration
- `models.py`: DB schema
- `services.py`: external/service logic (AI, OCR, audio, email)
- `config.py`: environment-backed settings
- `templates/*.html`: server-rendered pages
- `static/js/main.js`: interaction logic + charts + API calls
- `static/css/style.css`: visual system
- `HOW_TO_RUN.md`: local setup instructions
- `SOFTWARE_USED.md`: technology list

---

## Suggested Next Improvements

- Move admin auth to role-based model with Flask-Login.
- Add CSRF protection and stronger session security.
- Add tests for:
  - auth flow
  - sentiment endpoints
  - analytics API output shape
- Replace print logging with structured logging.
- Introduce secure secret management and remove insecure fallback credentials.
- Consider async/background job for email sending to improve response latency.

