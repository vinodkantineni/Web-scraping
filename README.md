# AI-Powered Personalized News Digest & Bias Detection SaaS

A production-grade, end-to-end media analysis web application designed to help users combat information overload, isolate media slants, and generate objective coverage. Built using a modern React frontend and a FastAPI Python backend, complete with secure JWT user authentication, persistent database history, and single-container Docker deployment support.

---

## Key Features
1. **Interactive Dashboard**: Submit article URLs or paste raw text for analysis.
2. **Political Bias Spectrum**: DisplaysLeft, Center, and Right leanings of articles using a side-by-side comparison chart.
3. **Objective Summarization**: Condenses long articles into factual, bias-free summaries (approx. 100-150 words).
4. **Neutral Debiasing**: Automatically rewrites the news content in a purely neutral tone.
5. **Secure Authentication**: Register and log in securely to access personalized research dashboards.
6. **Search & Analysis History**: Every processed article is automatically logged to a local SQLite database for future reference.

---

## Tech Stack
- **Frontend**: React (Vite), React Router, Lucide Icons, Chart.js, Vanilla CSS Glassmorphic theme.
- **Backend**: FastAPI, SQLAlchemy (SQLite database), JWT (JSON Web Tokens), `newspaper3k` web scraper.
- **AI Models**: Gemini API (`gemini-1.5-flash` model for 1-2s analysis) with an optional fallback to local Hugging Face BART models.
- **Deployment**: Docker (Multi-stage build), Docker Compose.

---

## Setup & Local Development

> [!IMPORTANT]
> **Run commands from the project root directory** (i.e. `C:\projects\Web scraping`). Do not run virtual environment commands inside the `/backend` or `/frontend` subdirectories.

### Prerequisites
- Python 3.11 or 3.12 (highly recommended; avoid pre-release Python 3.14 to prevent dependency conflicts)
- Node.js 18+

### Step 1: Environment Configuration
Create a `.env` file inside the `backend/` directory:
- Path: [backend/.env](file:///c:/projects/Web%20scraping/backend/.env)
```env
# Required for fast 1-2s Gemini Analysis (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here

# JWT authentication configurations
JWT_SECRET_KEY=generate_a_secure_random_string_here
JWT_EXPIRE_MINUTES=1440

# Database URL
DATABASE_URL=sqlite:///./news_bias.db
```

### Step 2: Install Dependencies
Open your shell (e.g. PowerShell on Windows) in the project root folder and execute:

1. **Backend Environment Setup**:
   ```bash
   # Create the virtual environment using Python 3.12
   py -3.12 -m venv .venv

   # Windows (PowerShell requires leading `.\` to run local scripts):
   .\.venv\Scripts\pip install -r backend/requirements.txt

   # macOS/Linux:
   .venv/bin/pip install -r backend/requirements.txt
   ```
2. **Frontend Packages Setup**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Step 3: Run the Application
Start both the FastAPI backend and Vite frontend concurrently by running the root launcher:
```bash
# Windows:
.\.venv\Scripts\python run.py

# macOS/Linux:
.venv/bin/python run.py
```
This script runs:
- **Frontend Web UI**: [http://localhost:5173](http://localhost:5173) (or 5174 if port 5173 is occupied)
- **FastAPI Backend (Swagger API Docs)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Deployment & Dockerization
The project is containerized for production deployments. Please refer to [DEPLOY.md](file:///c:/projects/Web%20scraping/DEPLOY.md) for full step-by-step instructions on local Docker running, Render setup, and GCP Cloud Run setup.

---

## Pushing to GitHub

To push this project to your GitHub account, run the following commands in the root directory:
```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit of end-to-end news bias digest SaaS"

# Set branch name to main
git branch -M main

# Add your remote GitHub URL
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git

# Push to GitHub
git push -u origin main
```
