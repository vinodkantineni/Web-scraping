# Walkthrough: Complete End-to-End BiasDigest SaaS Project

The prototype single-file Gradio application has been successfully transformed into a full production-ready, industry-grade media intelligence SaaS. Below is a comprehensive overview of the components, database structure, and execution steps.

---

## 📂 Project Directory Structure
All project assets are organized in the project folder [news-bias-digest](file:///c:/projects/news-bias-digest):

```
news-bias-digest/
├── Dockerfile                  # Multi-stage production container build
├── docker-compose.yml          # Container orchestration script
├── run.py                      # Concurrency runner script for dev server
├── README.md                   # Operational guide & git setup steps
├── .gitignore                  # Git track ignore configurations
├── backend/
│   ├── requirements.txt        # Backend python dependencies
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI entrypoint & static mounting
│       ├── database.py         # SQLAlchemy engine & session getter
│       ├── models.py           # DB Schemas (User & Analysis tables)
│       ├── schemas.py          # Pydantic schema request/response types
│       ├── auth.py             # JWT & password hashing cryptography
│       ├── ml/
│       │   └── analyzer.py     # AI Pipeline (Gemini HTTP API & BART fallback)
│       └── routes/
│           ├── auth.py         # Auth API routes (/register, /login, /me)
│           └── analysis.py     # Analysis routes (/analyze, /history)
└── frontend/
    ├── package.json
    ├── vite.config.js          # Vite config with API dev server proxy
    ├── index.html              # HTML shell with custom page title
    └── src/
        ├── index.css           # Vanilla CSS custom glassmorphic dark theme
        ├── main.jsx
        ├── App.jsx             # React App router & login session check
        ├── components/
        │   ├── Navbar.jsx      # Navigation bar with Lucide icons
        │   └── BiasChart.jsx   # Comparison bar chart using Chart.js
        └── pages/
            ├── LandingPage.jsx # Product intro landing page
            ├── AuthPage.jsx    # User login & registration panels
            ├── DashboardPage.jsx # Main analyzer input/result workspace
            └── HistoryPage.jsx # User-specific past search dashboard
```

---

## 🛢️ Database Schema
We created two interrelated SQL tables using SQLAlchemy inside [models.py](file:///c:/projects/news-bias-digest/backend/app/models.py):

1. **`users` Table**:
   - `id` (Primary Key, Autoincrement)
   - `username` (String, Unique, Indexed)
   - `password_hash` (String, Bcrypt hashed)
   - `created_at` (DateTime, Defaults to UTC)

2. **`analyses` Table**:
   - `id` (Primary Key, Autoincrement)
   - `user_id` (Foreign Key -> `users.id`)
   - `title` (String)
   - `url` (String, Optional)
   - `text` (String, Original raw content)
   - `summary` (String, AI objective factual summary)
   - `original_left` / `original_center` / `original_right` (Float bias scores)
   - `debiased_text` (String, Objective rewritten content)
   - `debiased_left` / `debiased_center` / `debiased_right` (Float debiased bias scores)
   - `bias_reduction` (Float, Calculated drop in maximum political spectrum score)
   - `created_at` (DateTime, Defaults to UTC)

---

## 🎯 Verification Results
1. **Compilation Check**: Successfully validated that all Python modules compile without syntax errors:
   - [main.py](file:///c:/projects/news-bias-digest/backend/app/main.py)
   - [models.py](file:///c:/projects/news-bias-digest/backend/app/models.py)
   - [analyzer.py](file:///c:/projects/news-bias-digest/backend/app/ml/analyzer.py)
   - [auth.py](file:///c:/projects/news-bias-digest/backend/app/auth.py)
2. **Frontend Build Check**: Verified that the React Vite application compiles to optimized production assets:
   - `npm run build` output successfully compiled in 862ms.
   - Resulting bundles generated under `frontend/dist/`.

---

## 🚀 How to Run & Push to GitHub
Please refer to the detailed instructions in the project [README.md](file:///c:/projects/news-bias-digest/README.md) to set up environment variables (including your `GEMINI_API_KEY`), install dependencies, boot both servers concurrently with `python run.py`, or deploy the Docker image.
