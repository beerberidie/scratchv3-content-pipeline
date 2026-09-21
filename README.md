# ScratchV3: scheduled AI content pipeline with WordPress publishing

A FastAPI service that generates articles and social posts from rules and reference material, schedules them, and publishes them to WordPress **as drafts** for a human to review.

## Pipeline
1. **Rules and references:** free-form content rules are parsed into structured prompts; past chat conversations can be ingested as reference material.
2. **Generation:** OpenAI or OpenRouter, selected per user; user-supplied text passes through an input sanitizer (`app/services/input_sanitizer.py`).
3. **Images:** optional stock images via the Pexels API.
4. **QA filter:** formatting and quality checks before publishing.
5. **Publish:** creates the post through the WordPress REST API (`/wp-json/wp/v2`) with `status: draft`, so nothing goes live unreviewed.

## The parts worth a look
- **Scheduler with Redis locks** (`app/services/scheduler.py`): each scheduled task takes a Redis lock before it runs, so the same task can't run twice at once.
- **Encrypted API keys** (`app/services/encryption.py`): third-party keys are stored with Fernet encryption, never in plain text.
- **Auth:** JWT sessions with bcrypt-hashed passwords.

## Numbers
77 API endpoints · 89 test functions · FastAPI · Redis · Python 3.8+

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # AI provider key, Redis URL, encryption key, WordPress URL + application password
python run.py
```

## Tests
```bash
pytest -q
```
