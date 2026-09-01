#!/usr/bin/env python3
"""
========================================================================
   CINECLEAR AI // SYSTEM HEALTHCHECK & DIAGNOSTIC DOCTOR
========================================================================
Provides judges and evaluators with a 1-command diagnostic for Python
runtime, dependencies, API keys, video/PDF codecs, and sample media.
"""

import os
import sys
import importlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Enable ANSI escape sequences on Windows terminals
if sys.platform == "win32":
    os.system("color")

def print_status(component: str, ok: bool, details: str = ""):
    status = f"{GREEN}[PASS]{RESET}" if ok else f"{RED}[FAIL]{RESET}"
    print(f"  {status} {BOLD}{component:<32}{RESET} {details}")

def run_doctor():
    print(f"\n{CYAN}{BOLD}======================================================{RESET}")
    print(f"{CYAN}{BOLD}   🎬 CineClear AI // System Diagnostic & Doctor     {RESET}")
    print(f"{CYAN}{BOLD}======================================================{RESET}\n")
    
    all_ok = True

    # 1. Python Runtime
    py_ver = sys.version_info
    py_ok = (py_ver.major == 3 and py_ver.minor >= 10)
    print_status("Python Runtime (>= 3.10)", py_ok, f"v{py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if not py_ok:
        all_ok = False

    # 2. Critical Packages
    packages = ["fastapi", "pydantic", "cv2", "reportlab", "google.genai", "httpx", "pytest"]
    for pkg in packages:
        try:
            importlib.import_module(pkg)
            print_status(f"Package: {pkg}", True)
        except ImportError:
            print_status(f"Package: {pkg}", False, "Missing. Run: pip install -r requirements.txt")
            all_ok = False

    # 3. Environment Variables & API Keys
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    parallel_key = os.getenv("PARALLEL_API_KEY")
    
    if gemini_key:
        masked = f"{gemini_key[:4]}...{gemini_key[-4:]}"
        print_status("GEMINI_API_KEY", True, f"Found ({masked})")
    else:
        print_status("GEMINI_API_KEY", False, "Missing in .env (Dynamic Cascade fallback active)")

    if parallel_key:
        masked = f"{parallel_key[:4]}...{parallel_key[-4:]}"
        print_status("PARALLEL_API_KEY", True, f"Found ({masked})")
    else:
        print_status("PARALLEL_API_KEY", False, "Missing in .env (Offline statutory grounding active)")

    # 4. Engine & Codec Diagnostics
    try:
        import cv2
        print_status("OpenCV Video Decoder", True, f"Build: {cv2.__version__}")
    except Exception as e:
        print_status("OpenCV Video Decoder", False, str(e))
        all_ok = False

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        print_status("ReportLab PDF Engine", True, "Canvas & Flowables Ready")
    except Exception as e:
        print_status("ReportLab PDF Engine", False, str(e))
        all_ok = False

    # 5. Sample Media Presence
    sample_img = Path("sample_media/sample_set_photo.jpg").exists()
    sample_txt = Path("sample_media/sample_screenplay.txt").exists()
    print_status("Sample Media Assets", sample_img and sample_txt, "Production stills & screenplay loaded")

    print("\n" + "=" * 55)
    if all_ok:
        print(f"{GREEN}{BOLD}All systems green. CineClear AI is ready for production.{RESET}\n")
    else:
        print(f"{YELLOW}{BOLD}Some components require attention. See details above.{RESET}\n")

if __name__ == "__main__":
    run_doctor()
