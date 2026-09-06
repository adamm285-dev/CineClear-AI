import argparse
import asyncio
import sys
import json
from pathlib import Path

from app.config import settings
from app.auditor import CineClearAuditor
from app.models import RiskLevel


def print_banner():
    print("""
========================================================================
   CINECLEAR AI // AGENTIC CINEMA LEGAL & E&O CLEARANCE SYSTEM       
========================================================================
    """)


async def run_cli():
    parser = argparse.ArgumentParser(
        description="CineClear AI - Agentic Legal & E&O Clearance Scanner for Film, TV, and Commercials"
    )
    parser.add_argument("--file", type=str, help="Path to video clip, set photo, or screenplay PDF/TXT")
    parser.add_argument("--title", type=str, default="Feature Production", help="Project / Film Title")
    parser.add_argument("--media-type", type=str, default="auto", choices=["auto", "video", "image", "script"], help="Media asset type")
    parser.add_argument("--output-json", type=str, help="Save report to specified JSON file path")
    parser.add_argument("--output-pdf", type=str, help="Save PDF clearance binder to specified path")
    parser.add_argument("--demo", action="store_true", help="Run instant demo audit using bundled sample set photo")
    parser.add_argument("--batch-dir", type=str, help="Directory of media files to batch audit")

    args = parser.parse_args()
    print_banner()

    target_file = args.file
    if args.demo:
        target_file = str(settings.SAMPLE_MEDIA_DIR / "sample_set_photo.jpg")
        print(f"[*] Running demo clearance audit on bundled sample: {target_file}")
    elif not target_file and not args.batch_dir:
        print("[!] No file specified. Defaulting to --demo mode.")
        target_file = str(settings.SAMPLE_MEDIA_DIR / "sample_set_photo.jpg")

    auditor = CineClearAuditor()

    if target_file:
        path = Path(target_file)
        if not path.exists():
            print(f"[!] Error: File '{target_file}' does not exist.")
            sys.exit(1)

        print(f"[*] Initiating Multimodal & Parallel Grounded Audit for: {path.name}")
        print(f"    Project Title: {args.title}")
        print(f"    Gemini Model: {settings.GEMINI_MODEL} ({'Configured' if settings.is_gemini_configured() else 'Simulation Engine'})")
        print(f"    Parallel Search API: {settings.PARALLEL_BASE_URL} ({'Configured' if settings.is_parallel_configured() else 'Verified Knowledge Base'})")
        print("------------------------------------------------------------------------")

        report = await auditor.audit_media(
            file_path=str(path),
            project_title=args.title,
            media_type=args.media_type
        )

        print("\n========================= AUDIT SUMMARY =========================")
        print(f" Report ID       : {report.id}")
        print(f" Production      : {report.project_title}")
        print(f" Media Asset     : {report.media_filename}")
        print(f" Total Flags     : {report.total_flags}")
        print(f"   - CRITICAL    : {report.critical_count}")
        print(f"   - HIGH        : {report.high_count}")
        print(f"   - MEDIUM      : {report.medium_count}")
        print(f"   - LOW / PD    : {report.low_count}")
        print("=================================================================\n")

        print("----------------------- ITEMIZED CLEARANCE FLAGS -----------------------")
        for idx, flag in enumerate(report.flags, 1):
            print(f"[{idx}] {flag.timestamp_or_page} | {flag.category.value} | RISK: {flag.risk_level.value}")
            print(f"    Entity       : {flag.detected_entity}")
            print(f"    Visual/Scene : {flag.visual_description}")
            print(f"    Grounding    : {flag.verification.statutory_context[:120]}...")
            print(f"    Mitigation   : {flag.mitigation_action}")
            print("------------------------------------------------------------------------")

        if report.pdf_report_path:
            print(f"\n[+] Production-Grade E&O PDF Dossier Generated: {report.pdf_report_path}")

        if args.output_json:
            out_json = Path(args.output_json)
            out_json.write_text(report.model_dump_json(indent=2), encoding="utf-8")
            print(f"[+] Audit JSON saved to: {out_json.resolve()}")


if __name__ == "__main__":
    asyncio.run(run_cli())
