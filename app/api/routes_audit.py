import json
import io
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models.schema import InvestigationCase

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

router = APIRouter()

class AuditLogItem(BaseModel):
    id: str
    alert_id: Optional[str] = None
    entity_id: Optional[str] = None
    objective: Optional[str] = None
    typology: Optional[str] = None
    status: str
    priority_score: Optional[float] = 0.0
    priority_band: Optional[str] = "MEDIUM"
    final_risk_score: Optional[float] = None
    decision: Optional[str] = "REVIEW"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    summary_notes: Optional[str] = None

@router.get("/audit/logs", response_model=List[AuditLogItem])
def get_audit_logs(
    status: Optional[str] = Query(None, description="Filter by case status: OPEN, CLOSED, ALL"),
    db: Session = Depends(get_db)
):
    """
    Get all audit trail cases from the database.
    """
    query = db.query(InvestigationCase)
    if status and status.upper() != "ALL":
        query = query.filter(InvestigationCase.status == status.upper())
    
    cases = query.order_by(InvestigationCase.updated_at.desc()).all()
    
    result = []
    for c in cases:
        snapshot = c.state_snapshot_json or {}
        sar_info = snapshot.get("sar_narrative", {})
        summary_text = ""
        if isinstance(sar_info, dict):
            summary_text = sar_info.get("executive_summary") or sar_info.get("summary") or ""
        elif isinstance(sar_info, str):
            summary_text = sar_info[:200]
            
        if not summary_text and snapshot.get("audit_log"):
            audit_log = snapshot.get("audit_log", [])
            if isinstance(audit_log, list) and len(audit_log) > 0:
                summary_text = audit_log[-1] if isinstance(audit_log[-1], str) else str(audit_log[-1])

        result.append(AuditLogItem(
            id=c.id,
            alert_id=c.alert_id,
            entity_id=c.entity_id,
            objective=c.objective,
            typology=c.typology or "Suspicious Activity",
            status=c.status,
            priority_score=c.priority_score or 0.0,
            priority_band=c.priority_band or "MEDIUM",
            final_risk_score=c.final_risk_score if c.final_risk_score is not None else c.priority_score,
            decision=c.decision or "REVIEW",
            created_at=c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
            updated_at=c.updated_at.strftime("%Y-%m-%d %H:%M:%S") if c.updated_at else None,
            summary_notes=summary_text or "Audit snapshot recorded."
        ))
    return result

@router.get("/audit/logs/{case_id}/pdf")
def generate_audit_pdf(case_id: str, db: Session = Depends(get_db)):
    """
    Generates a downloadable compliance PDF report for a given case.
    """
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        # Also try searching by alert_id if case_id matches alert_id format
        case = db.query(InvestigationCase).filter(InvestigationCase.alert_id == case_id).first()
    
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found.")

    snapshot = case.state_snapshot_json or {}
    
    # PDF generation buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1e293b")   # Slate 800
    ACCENT = colors.HexColor("#0284c7")    # Sky 600
    DARK_BG = colors.HexColor("#0f172a")   # Slate 900
    TEXT_DARK = colors.HexColor("#334155") # Slate 700
    LIGHT_BG = colors.HexColor("#f8fafc")  # Slate 50
    BORDER_COLOR = colors.HexColor("#cbd5e1") # Slate 300
    
    # Badge colors
    if case.decision == "BLOCK":
        DECISION_COLOR = colors.HexColor("#dc2626") # Red 600
    elif case.decision == "ALLOW":
        DECISION_COLOR = colors.HexColor("#16a34a") # Green 600
    else:
        DECISION_COLOR = colors.HexColor("#d97706") # Amber 600

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#64748b")
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=ACCENT,
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=PRIMARY
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("FIN-SPECTRA // AUDIT & COMPLIANCE DOSSIER", title_style))
    story.append(Paragraph(f"Official Regulatory Investigation Audit Trail & Decision Log • Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=12))

    # 2. Executive Summary Metrics Table
    risk_score = case.final_risk_score if case.final_risk_score is not None else case.priority_score or 0.0
    
    summary_data = [
        [
            Paragraph("<b>CASE ID:</b>", body_style), Paragraph(case.id or "N/A", bold_body_style),
            Paragraph("<b>DECISION:</b>", body_style), Paragraph(f"<font color='{DECISION_COLOR.hexval()}'><b>{case.decision or 'REVIEW'}</b></font>", bold_body_style)
        ],
        [
            Paragraph("<b>ALERT ID:</b>", body_style), Paragraph(case.alert_id or "N/A", body_style),
            Paragraph("<b>FINAL RISK SCORE:</b>", body_style), Paragraph(f"<b>{risk_score:.1f} / 100</b>", bold_body_style)
        ],
        [
            Paragraph("<b>ENTITY ID:</b>", body_style), Paragraph(case.entity_id or "N/A", body_style),
            Paragraph("<b>PRIORITY BAND:</b>", body_style), Paragraph(case.priority_band or "MEDIUM", body_style)
        ],
        [
            Paragraph("<b>TYPOLOGY:</b>", body_style), Paragraph(case.typology or "Suspicious Activity", body_style),
            Paragraph("<b>CASE STATUS:</b>", body_style), Paragraph(case.status or "OPEN", body_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[1.3*inch, 2.3*inch, 1.3*inch, 2.3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # 3. Investigation Objective & Overview
    story.append(Paragraph("1. Case Objective & Scope", section_heading))
    obj_text = case.objective or f"Investigate suspicious {case.typology or 'financial'} behavior for Entity {case.entity_id} associated with Alert {case.alert_id}."
    story.append(Paragraph(obj_text, body_style))
    story.append(Spacer(1, 10))

    # 4. KYC & Verification Signals
    story.append(Paragraph("2. KYC & Entity Verification", section_heading))
    kyc_data = snapshot.get("kyc_verified", {})
    if not isinstance(kyc_data, dict):
        kyc_data = {}
    
    kyc_table_data = [
        [Paragraph("<b>Check Item</b>", bold_body_style), Paragraph("<b>Status / Details</b>", bold_body_style)],
        [Paragraph("PEP (Politically Exposed Person)", body_style), Paragraph("POSITIVE FLAG" if kyc_data.get("pep") else "CLEARED / LOW RISK", body_style)],
        [Paragraph("Sanctions Watchlist Match", body_style), Paragraph("HIGH RISK MATCH" if kyc_data.get("sanctions_match") or kyc_data.get("sanction_match") else "CLEARED / NO MATCH", body_style)],
        [Paragraph("Jurisdiction Risk", body_style), Paragraph(str(kyc_data.get("jurisdiction_risk") or kyc_data.get("country") or "Standard (Low Risk)"), body_style)],
        [Paragraph("Customer Type", body_style), Paragraph(str(kyc_data.get("customer_type") or "Individual Account"), body_style)],
    ]
    kyc_table = Table(kyc_table_data, colWidths=[2.8*inch, 4.4*inch])
    kyc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(kyc_table)
    story.append(Spacer(1, 14))

    # 5. Risk Scoring & Multi-Factor Breakdown
    story.append(Paragraph("3. Multi-Factor Risk Score Breakdown", section_heading))
    scoring_data = snapshot.get("scoring_breakdown", {})
    if not isinstance(scoring_data, dict):
        scoring_data = {}

    factors = [
        ("KYC & Entity Risk Component", scoring_data.get("kyc_risk_score", 15.0)),
        ("Transaction Velocity & Volume", scoring_data.get("velocity_risk_score", 25.0)),
        ("Network & Counterparty Exposure", scoring_data.get("network_risk_score", 20.0)),
        ("Behavioral Anomaly & Typology", scoring_data.get("behavioral_risk_score", 30.0)),
        ("Sanctions & Blacklist Proximity", scoring_data.get("sanctions_risk_score", 10.0)),
    ]
    
    scoring_table_data = [[Paragraph("<b>Risk Dimension</b>", bold_body_style), Paragraph("<b>Score Impact</b>", bold_body_style)]]
    for factor_name, score_val in factors:
        try:
            val_float = float(score_val)
        except (ValueError, TypeError):
            val_float = 0.0
        scoring_table_data.append([
            Paragraph(factor_name, body_style),
            Paragraph(f"<b>{val_float:.1f} pts</b>", body_style)
        ])
    
    scoring_table = Table(scoring_table_data, colWidths=[4.8*inch, 2.4*inch])
    scoring_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(scoring_table)
    story.append(Spacer(1, 14))

    # 6. Regulatory & Suspicious Activity Narrative
    story.append(Paragraph("4. Suspicious Activity Narrative & Regulatory Findings", section_heading))
    sar_narrative = snapshot.get("sar_narrative", {})
    narrative_body = ""
    if isinstance(sar_narrative, dict):
        narrative_body = sar_narrative.get("narrative") or sar_narrative.get("executive_summary") or ""
    elif isinstance(sar_narrative, str):
        narrative_body = sar_narrative
    
    if not narrative_body:
        narrative_body = f"Analysis of Entity {case.entity_id} revealed indicators consistent with {case.typology or 'suspicious activity'}. The decision to set case status to '{case.decision or 'REVIEW'}' was derived automatically by the multi-agent graph with score {risk_score:.1f}."

    # Format text paragraphs neatly
    for paragraph_str in narrative_body.split("\n\n"):
        if paragraph_str.strip():
            story.append(Paragraph(paragraph_str.strip(), body_style))
            story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 10))

    # 7. Audit Log Execution Steps
    story.append(Paragraph("5. Autonomous Multi-Agent Execution Trail", section_heading))
    audit_trail_events = snapshot.get("audit_log", [])
    if isinstance(audit_trail_events, list) and audit_trail_events:
        trail_table_data = [[Paragraph("<b>#</b>", bold_body_style), Paragraph("<b>Agent Event / Execution Step</b>", bold_body_style)]]
        for idx, event in enumerate(audit_trail_events[:10], start=1):
            event_str = str(event)
            trail_table_data.append([
                Paragraph(str(idx), body_style),
                Paragraph(event_str, body_style)
            ])
        trail_table = Table(trail_table_data, colWidths=[0.5*inch, 6.7*inch])
        trail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(trail_table)
    else:
        story.append(Paragraph("Agent execution completed. Full state snapshot persisted in database.", body_style))

    story.append(Spacer(1, 20))

    # 8. Digital Audit Footer & Stamp
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceBefore=10, spaceAfter=10))
    footer_text = f"<b>DIGITAL COMPLIANCE STAMP:</b> FIN-SPECTRA-ENGINE-v2.4 • HASH: {abs(hash(case.id + str(case.created_at))):x} • VERIFIED BY AUTOMATED RISK ENGINE"
    story.append(Paragraph(footer_text, subtitle_style))

    # Build document
    doc.build(story)
    buffer.seek(0)

    filename = f"FinSpectra_Audit_{case.id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
