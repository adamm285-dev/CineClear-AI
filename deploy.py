#!/usr/bin/env python3
"""
========================================================================
   CINECLEAR AI // 1-CLICK AUTO-DEPLOY & JUDGE EVALUATOR SCRIPT
========================================================================
This script provides a 1-click automated environment setup, dependency
verification, configuration initialization, and server launcher with
automatic browser launch for hackathon judges and evaluators.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def print_banner():
    print("""
========================================================================
       🎬 CINECLEAR AI // AGENTIC CINEMA LEGAL CLEARANCE
           Zero-Downtime Autonomous E&O Insurance Auditor
========================================================================
    """)

def check_python():
    print("[*] Checking Python runtime version...")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print(f"[!] Error: Python 3.10+ is required. Found: Python {v.major}.{v.minor}.{v.micro}")
        sys.exit(1)
    print(f"    [+] Python {v.major}.{v.minor}.{v.micro} detected. (OK)")

def setup_directories():
    print("[*] Verifying workspace directories...")
    for d in ["uploads", "reports", "sample_media", "docs/images"]:
        p = ROOT_DIR / d
        p.mkdir(parents=True, exist_ok=True)
    print("    [+] Directories initialized. (OK)")

def setup_env():
    print("[*] Checking environment configuration (.env)...")
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("    [!] .env not found. Auto-generating from .env.example...")
            env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
            print("    [+] .env created. (Using verified local offline fallback engine)")
        else:
            print("    [!] Warning: .env.example not found. Creating default .env...")
            default_env = (
                "# Google Gemini API\n"
                "GEMINI_API_KEY=your_gemini_api_key_here\n"
                "GEMINI_MODEL=gemini-3.5-flash-lite\n\n"
                "# Parallel Search API\n"
                "PARALLEL_API_KEY=your_parallel_api_key_here\n"
                "PARALLEL_BASE_URL=https://api.parallel.ai/v1\n\n"
                "# Server Settings\n"
                "HOST=0.0.0.0\n"
                "PORT=8085\n"
                "ENVIRONMENT=development\n"
            )
            env_file.write_text(default_env, encoding="utf-8")
    else:
        print("    [+] .env detected. (OK)")

def install_dependencies():
    req_file = ROOT_DIR / "requirements.txt"
    if not req_file.exists():
        print("[!] Warning: requirements.txt not found. Skipping auto-install.")
        return

    print("[*] Verifying & installing Python dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
            cwd=str(ROOT_DIR)
        )
        print("    [+] All dependencies verified and ready. (OK)")
    except Exception as e:
        print(f"    [!] Pip check failed ({e}). Continuing with existing environment...")

def run_doctor_if_requested():
    if "--doctor" in sys.argv or "--health" in sys.argv:
        from doctor import run_doctor
        run_doctor()
        sys.exit(0)

def run_tests_if_requested():
    if "--test" in sys.argv or "--pytest" in sys.argv:
        print("\n[*] Running CineClear AI 33-test validation suite...")
        res = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=str(ROOT_DIR))
        sys.exit(res.returncode)

def run_demo_if_requested():
    if "--demo" in sys.argv:
        print("\n[*] Running CineClear AI CLI Instant Demo...")
        res = subprocess.run([sys.executable, "main.py", "--demo"], cwd=str(ROOT_DIR))
        sys.exit(res.returncode)

def launch_server():
    port = int(os.environ.get("PORT", 8085))
    host = os.environ.get("HOST", "127.0.0.1")
    url = f"http://localhost:{port}"

    print(f"\n[*] Starting CineClear AI Studio Web Server on {url} ...")
    print(f"[*] Opening browser automatically at {url} ...\n")

    def open_browser():
        time.sleep(1.8)
        webbrowser.open(url)

    import threading
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    import uvicorn
    uvicorn.run("server:app", host=host, port=port, reload=False)

def main():
    print_banner()
    check_python()
    setup_directories()
    setup_env()
    install_dependencies()
    run_doctor_if_requested()
    run_tests_if_requested()
    run_demo_if_requested()
    launch_server()

if __name__ == "__main__":
    main()
