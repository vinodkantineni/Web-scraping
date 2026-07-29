import subprocess
import sys
import os
import signal
import time

processes = []

def signal_handler(sig, frame):
    print("\nStopping local servers...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            pass
    print("Servers stopped. Goodbye!")
    sys.exit(0)

# Register the signal handler for clean Ctrl+C exits
signal.signal(signal.SIGINT, signal_handler)

def run_servers():
    # Make sure we are in the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    print("==================================================")
    print("Starting AI News Bias Digest Local Dev Stack")
    print("==================================================")
    
    # 1. Start backend FastAPI server
    # Run with -m uvicorn so it resolves paths correctly
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.app.main:app", 
        "--host", "127.0.0.1", "--port", "8000", "--reload"
    ]
    
    print("Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=project_root,
        stdout=None,
        stderr=None
    )
    processes.append(backend_proc)

    # Give backend a moment to boot
    time.sleep(2)

    # 2. Start frontend dev server
    # Detect shell type for running npm correctly on Windows or Unix
    use_shell = os.name == 'nt'
    frontend_cmd = ["npm", "run", "dev"]
    
    print("Starting Vite Frontend on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=os.path.join(project_root, "frontend"),
        shell=use_shell,
        stdout=None,
        stderr=None
    )
    processes.append(frontend_proc)

    print("\n==================================================")
    print("Both servers are running!")
    print("Local Frontend: http://localhost:5173")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to terminate both servers.")
    print("==================================================\n")

    # Keep script alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run_servers()
