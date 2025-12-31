# SNELLIRE

**Your Agentic AI-powered career growth companion.**

Snellire is a Streamlit web app that helps you bridge the gap between where you are and where you want to be in your career. 
Upload your resume, tell it your dream job, and it'll figure out exactly what you need to learn—then guide you through it, step by step.

---

**What It Does**

1. Resume Analysis – You upload your resume (PDF) and describe your target role. The AI evaluates your current skills against what's needed for that job.

2. Personalized Learning Path – Based on your match percentage, Snellire routes you through one of three paths:
   - Foundation (< 40% match): Start from scratch with beginner-friendly fundamentals
   - Skill Up (40-79% match): Level up specific skills you're missing
   - Job Search (80%+ match): You're ready-- get tailored job hunting strategies

3. Progress Tracking – Your journey is saved to a database, so you can pick up exactly where you left off. Complete steps at your own pace.

4. Job Search Guidance – When you're ready, get platform recommendations, search keywords, and resume tips specific to your target role.

---

**Tech Stack**

- Frontend: Streamlit
- AI: Google Gemma 3 (27B) via OpenRouter API
- Database: Supabase (PostgreSQL)
- PDF Parsing: pypdf

---

**Prerequisites**

- Python 3.8+
- A Supabase project (free tier)
- An OpenRouter API key

**Installation**

```
#Clone the repo
git clone https://github.com/VibilanM/agentic-ai-project.git
cd agentic-ai-project

#Install dependencies
pip install -r requirements.txt
```

**Configuration**

Create a `.streamlit/secrets.toml` file with your API keys:

```
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
OPENROUTER_KEY = "your-openrouter-api-key"
```

**Database Setup**

Create a table called `user_progress` in your Supabase project with these columns:

| Column             | Type               |
|--------------------|--------------------|
| username           | text (primary key) |
| password           | text               |
| current_mode       | text               |
| chances_percentage | integer            |
| current_skills     | jsonb              |
| missing_skills     | jsonb              |
| foundation_steps   | jsonb              |
| foundation_index   | integer            |
| skill_up_steps     | jsonb              |
| skill_up_index     | integer            |
| resume_text        | text               |
| expectation_text   | text               |

**Run It**

```
python -m streamlit run main.py
```

---

**How It Works Internally**

Snellire uses a multi-agent approach internally:

1. Evaluation Agent – Analyzes resume vs. job requirements, outputs match percentage and skill gaps
2. Foundation Agent – Generates beginner learning paths for low-match users
3. Skill-Up Agent – Creates intermediate learning plans for users with existing foundations
4. Job Search Agent – Provides market-aware job hunting strategies for job-ready users

Each agent is a carefully crafted prompt that talks to the same LLM, but with different system instructions. 
The JSON responses are parsed and displayed as interactive step-by-step plans.

---

**Notes**

- Passwords are stored in plain text (since this is a demo project and is not production-ready at the moment)
- The AI model might occasionally return malformed JSON-- there's retry logic to handle that
- Rate limiting is handled with exponential backoff

---
