from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database import engine, Base
from .routes import auth, analysis

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI News Bias Detection & Debiasing API",
    description="Production-grade API for news extraction, bias analysis, and objective re-writing.",
    version="1.0.0"
)

# CORS configuration
# Allow local development frontend (usually port 5173 for Vite) and any production hosts
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(analysis.router)

# Root status endpoint
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "mode": "Local BART models (HuggingFace)"}

# Serve frontend static files in production
# The React build output directory (frontend/dist) is copied/built under a path served by FastAPI
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

if os.path.exists(static_dir):
    print(f"Serving compiled static frontend from: {static_dir}")
    # Mount assets folder
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="static")
    
    # Catch-all route to serve index.html for client-side routing (React Router)
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        # Allow API routes to pass through (handled by routers above)
        if catchall.startswith("api"):
            return None
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    print(f"Static frontend directory not found at: {static_dir}. Running API-only mode.")
    @app.get("/")
    def read_root():
        return {"message": "AI News Bias API is running. Point your React frontend to this address."}
