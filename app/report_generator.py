import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)

from app.config import settings
from app.models import (
    ClearanceAuditReport,
    RiskLevel,
    ClearanceCategory,
    UPL_LEGAL_DISCLAIMER,
    RogersTestAssessment,
)


def get_risk_color(risk: RiskLevel) -> colors.Color:
    if risk == RiskLevel.CRITICAL:
        return colors.HexColor("#dc2626")  # Vibrant Red
    elif risk == RiskLevel.HIGH:
        return colors.HexColor("#ea580c")  # Vibrant Orange
    elif risk == RiskLevel.MEDIUM:
        return colors.HexColor("#d97706")  # Amber / Yellow
    else:
        return colors.HexColor("#16a34a")  # Green


def generate_eo_clearance_binder(report: ClearanceAuditReport, output_path: Optional[str] = None) -> str:
    """
    Generates a Hollywood-grade Errors & Omissions (E&O) Legal Clearance Binder in PDF format.
    """
    if not output_path:
        filename = f"EO_Clearance_Binder_{report.project_title.replace(' ', '_')}_{report.id[:8]}.pdf"
        output_path = str(settings.REPORT_OUTPUT_DIR / filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=48
    )

    def _draw_page_chrome(canvas, _doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.setFont("Helvetica", 6)
        canvas.drawString(
            36,
            22,
            "DECISION-SUPPORT ONLY — not legal advice, not a clearance certificate, not an underwriting approval. Licensed counsel must sign."
        )
        canvas.restoreState()

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        alignment=0
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569")
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>CINECLEAR AI // COUNSEL RESEARCH DOSSIER (NOT A LEGAL OPINION)</b>", ParagraphStyle('HeaderTop', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#4f46e5"))),
            Paragraph(f"<b>REPORT ID:</b> {report.id[:8].upper()}", ParagraphStyle('HeaderRight', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#64748b"), alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)

    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4f46e5"), spaceAfter=10))

    # Main Title
    story.append(Paragraph("E&amp;O RISK MITIGATION &amp; EVIDENCE-GATHERING DOSSIER", title_style))
    story.append(Paragraph("For licensed production counsel and E&amp;O broker review only — not a distribution clearance.", subtitle_style))
    story.append(Paragraph(f"Production Title: <b>{report.project_title}</b>", subtitle_style))
    story.append(Spacer(1, 10))

    # 2. Executive Metadata Box
    meta_data = [
        [
            Paragraph(f"<b>Analyzed Media:</b> {report.media_filename}", body_style),
            Paragraph(f"<b>Audit Date:</b> {report.generated_at}", body_style)
        ],
        [
            Paragraph(f"<b>Media Type:</b> {report.media_type.upper()}", body_style),
            Paragraph("<b>Underwriting Standard:</b> Entertainment E&O Guidelines v4.2", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # UPL Statutory Decision-Support Notice
    upl_text = getattr(report, "legal_disclaimer", None) or UPL_LEGAL_DISCLAIMER
    upl_table = Table([[
        Paragraph(f"<b>UPL STATUTORY NOTICE:</b> {upl_text}", ParagraphStyle('UPLNotice', parent=body_style, fontSize=7.5, leading=10, textColor=colors.HexColor("#475569")))
    ]], colWidths=[540])
    upl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(upl_table)
    story.append(Spacer(1, 10))

    # 3. Executive Risk Matrix
    story.append(Paragraph("1. Executive Risk Summary & Flag Breakdown", section_heading))
    
    tally_data = [
        [
            Paragraph("<b>TOTAL LIABILITIES</b>", ParagraphStyle('TallyH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1)),
            Paragraph("<b>CRITICAL RISK</b>", ParagraphStyle('TallyH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1)),
            Paragraph("<b>HIGH RISK</b>", ParagraphStyle('TallyH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1)),
            Paragraph("<b>MEDIUM RISK</b>", ParagraphStyle('TallyH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1)),
            Paragraph("<b>LOW RISK</b>", ParagraphStyle('TallyH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1))
        ],
        [
            Paragraph(f"<font size=16><b>{report.total_flags}</b></font>", ParagraphStyle('TallyV', parent=styles['Normal'], fontName='Helvetica-Bold', alignment=1)),
            Paragraph(f"<font size=16 color='#dc2626'><b>{report.critical_count}</b></font>", ParagraphStyle('TallyV', parent=styles['Normal'], fontName='Helvetica-Bold', alignment=1)),
            Paragraph(f"<font size=16 color='#ea580c'><b>{report.high_count}</b></font>", ParagraphStyle('TallyV', parent=styles['Normal'], fontName='Helvetica-Bold', alignment=1)),
            Paragraph(f"<font size=16 color='#d97706'><b>{report.medium_count}</b></font>", ParagraphStyle('TallyV', parent=styles['Normal'], fontName='Helvetica-Bold', alignment=1)),
            Paragraph(f"<font size=16 color='#16a34a'><b>{report.low_count}</b></font>", ParagraphStyle('TallyV', parent=styles['Normal'], fontName='Helvetica-Bold', alignment=1))
        ]
    ]
    tally_table = Table(tally_data, colWidths=[108, 108, 108, 108, 108])
    tally_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f1f5f9")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tally_table)
    story.append(Spacer(1, 12))

    # 4. Itemized Clearance Ledger Table
    story.append(Paragraph("2. Itemized Legal Clearance Ledger", section_heading))

    ledger_header = [
        Paragraph("<b>Time / Page</b>", ParagraphStyle('LH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
        Paragraph("<b>Category</b>", ParagraphStyle('LH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
        Paragraph("<b>Detected Entity</b>", ParagraphStyle('LH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
        Paragraph("<b>Risk Level</b>", ParagraphStyle('LH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1)),
        Paragraph("<b>Actionable Mitigation</b>", ParagraphStyle('LH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
    ]
    ledger_rows = [ledger_header]

    for f in report.flags:
        risk_color_hex = "#dc2626" if f.risk_level == RiskLevel.CRITICAL else (
            "#ea580c" if f.risk_level == RiskLevel.HIGH else (
                "#d97706" if f.risk_level == RiskLevel.MEDIUM else "#16a34a"
            )
        )
        ledger_rows.append([
            Paragraph(f"<b>{f.timestamp_or_page}</b>", body_style),
            Paragraph(f.category.value.replace("_", " "), body_style),
            Paragraph(f"<b>{f.detected_entity}</b>", body_style),
            Paragraph(f"<font color='{risk_color_hex}'><b>{f.risk_level.value}</b></font>", ParagraphStyle('RC', parent=body_style, alignment=1)),
            Paragraph(f.mitigation_action, ParagraphStyle('MC', parent=body_style, fontSize=8, leading=11))
        ])

    ledger_table = Table(ledger_rows, colWidths=[65, 95, 115, 65, 200])
    ledger_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(ledger_table)
    story.append(Spacer(1, 14))

    # 5. Deep-Dive Audit Dossiers
    story.append(Paragraph("3. Detailed Clearance Dossiers & Web Grounding Evidence", section_heading))

    for idx, flag in enumerate(report.flags, 1):
        risk_color_hex = "#dc2626" if flag.risk_level == RiskLevel.CRITICAL else (
            "#ea580c" if flag.risk_level == RiskLevel.HIGH else (
                "#d97706" if flag.risk_level == RiskLevel.MEDIUM else "#16a34a"
            )
        )

        dossier_content = [
            [
                Paragraph(f"<b>FLAG #{idx}: {flag.detected_entity.upper()}</b>", ParagraphStyle('FH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.white)),
                Paragraph(f"<b>RISK: <font color='{risk_color_hex}'>{flag.risk_level.value}</font></b> | {flag.timestamp_or_page}", ParagraphStyle('FHR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white, alignment=2))
            ],
            [
                Paragraph(f"<b>Visual Context:</b> {flag.visual_description}", body_style),
                Paragraph(f"<b>Category:</b> {flag.category.value}", body_style)
            ],
            [
                Paragraph(f"<b>Parallel Search Objective:</b> <i>{flag.verification.search_objective}</i>", ParagraphStyle('SO', parent=body_style, fontSize=8, textColor=colors.HexColor("#475569"))),
                Paragraph(f"<b>Rights Holder:</b> {flag.verification.rights_holder_identified or 'Unspecified'}", body_style)
            ],
            [
                Paragraph(f"<b>Statutory Analysis:</b> {flag.verification.statutory_context}", ParagraphStyle('SA', parent=body_style, fontSize=8.5, leading=12)),
                Paragraph(f"<b>Mitigation Action:</b> <b>{flag.mitigation_action}</b>", ParagraphStyle('MA', parent=body_style, fontSize=8.5, leading=12, textColor=colors.HexColor("#0f172a")))
            ]
        ]

        if flag.verification.sources_checked:
            sources_str = ", ".join(flag.verification.sources_checked[:3])
            dossier_content.append([
                Paragraph(f"<b>Sources Checked:</b> <font color='#2563eb'>{sources_str}</font>", ParagraphStyle('SC', parent=body_style, fontSize=7.5)),
                Paragraph(f"<b>Public Domain:</b> {'YES' if flag.verification.is_public_domain else 'NO'} | <b>Active TM:</b> {'YES' if flag.verification.active_trademark_found else 'NO'}", body_style)
            ])

        # Fair Use Scorecard (17 U.S.C. § 107)
        if flag.fair_use_scorecard:
            sc = flag.fair_use_scorecard
            dossier_content.append([
                Paragraph(f"<b>Statutory Fair Use Defense (17 U.S.C. § 107):</b> {sc.defense_rating} (Score: <b>{sc.composite_score}/5.0</b>)", ParagraphStyle('FUD', parent=body_style, fontSize=8, textColor=colors.HexColor("#0f172a"))),
                Paragraph(f"F1: {sc.purpose_and_character.score}/5 | F2: {sc.nature_of_work.score}/5 | F3: {sc.amount_and_substantiality.score}/5 | F4: {sc.market_harm.score}/5", ParagraphStyle('FUDS', parent=body_style, fontSize=7.5, alignment=1))
            ])

        # Multi-Territory Jurisdictional Matrix
        if flag.territory_matrix:
            terr_summary = " | ".join([f"<b>{t.territory}:</b> {t.clearance_status}" for t in flag.territory_matrix[:4]])
            dossier_content.append([
                Paragraph(f"<b>Multi-Territory Status:</b> {terr_summary}", ParagraphStyle('MTS', parent=body_style, fontSize=7.5, leading=10, textColor=colors.HexColor("#334155"))),
                Paragraph(f"<b>Jurisdictions:</b> US, UK, EU, CA", ParagraphStyle('MTJ', parent=body_style, fontSize=7.5, alignment=1))
            ])

        # AWCPA § 120(a) Architectural Assessment
        if flag.arch_assessment:
            aa = flag.arch_assessment
            arch_status_color = "#16a34a" if aa.is_public_view_safe_harbor else "#dc2626"
            dossier_content.append([
                Paragraph(f"<b>AWCPA Architectural Status:</b> <font color='{arch_status_color}'><b>{aa.jurisdiction_status}</b></font><br/><i>{aa.governing_statute}:</i> {aa.commercial_filing_restrictions}", ParagraphStyle('AAS', parent=body_style, fontSize=7.5, leading=10)),
                Paragraph(f"<b>Safe Harbor:</b> {'YES' if aa.is_public_view_safe_harbor else 'RESTRICTED'}", ParagraphStyle('AAJ', parent=body_style, fontSize=7.5, alignment=1))
            ])

        # Rogers v. Grimaldi Artistic Relevance Assessment (Lanham Act § 1125)
        if flag.rogers_assessment:
            ra = flag.rogers_assessment
            rogers_color = "#16a34a" if ra.rogers_protection_applies else "#dc2626"
            dossier_content.append([
                Paragraph(f"<b>Rogers v. Grimaldi Test:</b> <font color='{rogers_color}'><b>{'PROTECTION APPLIES' if ra.rogers_protection_applies else 'HIGH LITIGATION RISK'}</b></font><br/><i>Artistic Relevance:</i> {'PASSED' if ra.artistic_relevance_passed else 'FAILED'} | <i>Explicitly Misleading:</i> {'YES' if ra.explicitly_misleading else 'NO'}", ParagraphStyle('RAS', parent=body_style, fontSize=7.5, leading=10)),
                Paragraph(f"<b>Expressive Shield:</b> {'YES' if ra.rogers_protection_applies else 'NO'}", ParagraphStyle('RAJ', parent=body_style, fontSize=7.5, alignment=1))
            ])

        dossier_table = Table(dossier_content, colWidths=[360, 180])
        dossier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(KeepTogether([
            dossier_table,
            Spacer(1, 8)
        ]))

    # 6. Music Cue Sheet Appendix (if present)
    has_music_cues = (
        report.remediation_package is not None
        and report.remediation_package.music_cue_sheet is not None
        and bool(report.remediation_package.music_cue_sheet.cue_entries)
    )

    if has_music_cues:
        story.append(Spacer(1, 10))
        story.append(KeepTogether([
            Paragraph("4. Standard Entertainment Music Cue Sheet (ASCAP / BMI / SESAC)", section_heading),
            Paragraph(f"Synchronized audio compositions and sound recordings requiring dual-tier master & sync clearance for '{report.project_title}'.", ParagraphStyle('CueSub', parent=body_style, fontSize=8, leading=11, textColor=colors.HexColor("#64748b"))),
            Spacer(1, 6)
        ]))

        cue_rows = [
            [
                Paragraph("<b>Cue #</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
                Paragraph("<b>Track / Performer</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
                Paragraph("<b>PRO / Publisher</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
                Paragraph("<b>Master Rights Owner</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
                Paragraph("<b>Usage</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
                Paragraph("<b>Status</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', fontSize=8, textColor=colors.white))
            ]
        ]
        for cue in report.remediation_package.music_cue_sheet.cue_entries:
            cue_rows.append([
                Paragraph(cue.cue_number, ParagraphStyle('CD', parent=body_style, fontSize=7.5)),
                Paragraph(f"<b>{cue.track_title}</b><br/><i>{cue.artist_performer}</i>", ParagraphStyle('CD', parent=body_style, fontSize=7.5)),
                Paragraph(cue.publisher_pro, ParagraphStyle('CD', parent=body_style, fontSize=7.5)),
                Paragraph(cue.master_rights_holder, ParagraphStyle('CD', parent=body_style, fontSize=7.5)),
                Paragraph(f"{cue.usage_type}<br/>({cue.duration})", ParagraphStyle('CD', parent=body_style, fontSize=7.5)),
                Paragraph(f"<font color='#dc2626'><b>{cue.clearance_status}</b></font>", ParagraphStyle('CD', parent=body_style, fontSize=7.5))
            ])

        cue_table = Table(cue_rows, colWidths=[45, 125, 95, 115, 75, 85])
        cue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(cue_table)
        story.append(Spacer(1, 12))

    # 7. Human-in-the-loop counsel / broker sign-off (CineClear is the gatherer, not the certifier)
    cert_section_num = 5 if has_music_cues else 4
    story.append(Spacer(1, 10))
    story.append(KeepTogether([
        Paragraph(f"{cert_section_num}. Licensed Counsel / E&amp;O Broker Review (Required Human Sign-Off)", section_heading),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8),
        Paragraph(
            "CineClear AI compiled this research dossier as a paralegal accelerator. It does not certify clearance, "
            "insurability, or fitness for distribution. A licensed production attorney and/or E&amp;O broker must "
            "independently review the evidence, accept or reject each flag, and provide the only legally operative sign-off. "
            "Until those signatures appear, this document is an evidence-gathering work product only.",
            ParagraphStyle('CertText', parent=body_style, fontSize=8, leading=11, textColor=colors.HexColor("#64748b"))
        ),
        Spacer(1, 14),
        Table([
            [
                Paragraph("____________________________________________<br/><b>Licensed Production Attorney Signature</b><br/><font size='7'>Bar No. / Jurisdiction</font>", body_style),
                Paragraph("____________________________________________<br/><b>Date of Independent Legal Review</b>", body_style)
            ],
            [
                Paragraph("<br/>____________________________________________<br/><b>E&amp;O Broker Review (not an insurance binder)</b>", body_style),
                Paragraph("<br/>____________________________________________<br/><b>Production Executive Acknowledgement</b>", body_style)
            ]
        ], colWidths=[270, 270])
    ]))

    doc.build(story, onFirstPage=_draw_page_chrome, onLaterPages=_draw_page_chrome)
    return output_path
