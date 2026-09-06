# 🔎 FindIt AI

**AI-powered Lost & Found platform for campuses, hostels and communities.**

## Problem
Lost and found information is fragmented across chats, notice boards and forms. Users need a better way to report items and discover possible matches.

## Solution
FindIt AI converts natural-language reports into structured data, uses AI-assisted categorization, ranks textually similar opposite-type reports, explains possible matches, and supports a claim/resolution workflow.

## Core features
- Lost / found reporting
- User registration and login
- AI category + summary (Gemini optional)
- Text similarity matching
- Match score + explanation
- Image upload as supporting evidence
- Claim workflow
- Active/resolved status
- Dashboard statistics
- FastAPI backend + Swagger
- Streamlit frontend
- Automated matching test

## Architecture
```text
Streamlit UI
    ↓
FastAPI REST API
    ↓
SQLite/PostgreSQL
    ↓
AI analysis + matching engine
    ↓
Possible match + explanation + claim
```

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Add a Gemini API key if you want Gemini-powered categorization/explanations. The app still runs with a local fallback without the key.

Terminal 1:
```bash
python -m uvicorn backend.main:app --reload
```

Terminal 2:
```bash
streamlit run frontend/app.py
```

Open:
- Frontend: http://localhost:8501
- API docs: http://127.0.0.1:8000/docs

## Testing
```bash
pytest
```

## Production roadmap
- Replace demo token flow with JWT/OAuth
- PostgreSQL
- pgvector/FAISS embeddings
- Multimodal image analysis
- Email/push notifications
- Admin moderation and claim verification
- Rate limiting and audit logs
- CI/CD
- Evaluation dataset and precision/recall tracking

## Responsible use
A match score is only a recommendation. It must not be treated as proof of ownership. Claims should be verified by a human/admin, especially for valuable items.
