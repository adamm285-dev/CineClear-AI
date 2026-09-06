"""
CineClear AI - NLE Timeline Marker & EDL Exporter
Converts clearance liabilities into industry-standard CMX 3600 Edit Decision Lists (EDL)
for direct import into DaVinci Resolve, Adobe Premiere Pro, and Avid Media Composer.
"""

import re
from app.models import ClearanceAuditReport, RiskLevel


def timecode_to_frames(tc: str, fps: int = 24) -> int:
    """Converts HH:MM:SS, HH:MM:SS:FF, or Page N to total frames."""
    clean_tc = re.sub(r'[^\d:]', '', tc).strip(":")
    parts = clean_tc.split(":") if clean_tc else []
    try:
        if len(parts) == 1 and parts[0]:
            return int(parts[0]) * fps
        elif len(parts) == 2:
            return (int(parts[0]) * 60 + int(parts[1])) * fps
        elif len(parts) == 3:
            return (int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])) * fps
        elif len(parts) == 4:
            return (int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])) * fps + int(parts[3])
    except ValueError:
        pass
    return 0


def frames_to_timecode(total_frames: int, fps: int = 24) -> str:
    """Converts frame integer to standard SMPTE timecode (HH:MM:SS:FF) with 24-hour wrap."""
    total_frames = max(0, int(total_frames))
    fps = max(1, int(fps))
    total_seconds = total_frames // fps
    f = total_frames % fps
    s = total_seconds % 60
    m = (total_seconds // 60) % 60
    h = (total_seconds // 3600) % 24
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


class EDLExporter:
    """Generates standard CMX 3600 EDL with locator markers and color codes."""

    @staticmethod
    def generate_cmx3600_edl(report: ClearanceAuditReport, fps: int = 24) -> str:
        safe_title = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in report.project_title).strip("_")
        lines = [
            f"TITLE: CINECLEAR_{safe_title.upper()}",
            "FCM: NON-DROP FRAME",
            "* COMMENT: Decision-support markers only. Not a legal clearance or distribution certificate.",
            "* COMMENT: Licensed production counsel must review before relying on any flag.",
            ""
        ]

        marker_colors = {
            RiskLevel.CRITICAL: "Red",
            RiskLevel.HIGH: "Orange",
            RiskLevel.MEDIUM: "Yellow",
            RiskLevel.LOW: "Green"
        }

        event_num = 1
        for flag in report.flags:
            start_frame = timecode_to_frames(flag.timestamp_or_page, fps)
            duration_frames = fps * 2  # 2-second standard locator window
            end_frame = start_frame + duration_frames

            src_in = "00:00:00:00"
            src_out = frames_to_timecode(duration_frames, fps)
            rec_in = frames_to_timecode(start_frame, fps)
            rec_out = frames_to_timecode(end_frame, fps)

            # CMX 3600 Event line
            lines.append(f"{event_num:03d}  AX       V     C        {src_in} {src_out} {rec_in} {rec_out}")
            lines.append(f"* FROM CLIP NAME: {report.media_filename}")
            
            # DaVinci Resolve & Premiere Marker metadata
            color = marker_colors.get(flag.risk_level, "Blue")
            clean_desc = flag.detected_entity.replace("\n", " ").strip()
            clean_mitigation = flag.mitigation_action.replace("\n", " ").strip()
            
            lines.append(f"* LOC: {rec_in} {color} CINECLEAR: [{flag.risk_level.value}] {clean_desc}")
            lines.append(f"* COMMENT: Action: {clean_mitigation}")
            lines.append("")
            event_num += 1

        return "\n".join(lines)
