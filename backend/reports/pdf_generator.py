"""
ACDRIP+ PDF Report Generator
Autonomous Cyber Defense, Risk Intelligence & Pre-Breach Simulation Platform
Generates comprehensive PDF security reports using ReportLab.
"""

import os
import io
from datetime import datetime, timezone
from typing import Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable, Image
    )
    from reportlab.graphics.shapes import Drawing, Rect, String, Circle
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics import renderPDF
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[!] ReportLab not available - PDF generation disabled")

from config import settings


def generate_report_pdf(scan_data: dict, risk_data: dict = None, simulation_data: dict = None, output_path: str = None) -> Optional[str]:
    """Generate a comprehensive PDF security report."""
    if not REPORTLAB_AVAILABLE:
        return None

    # Ensure output directory exists
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        scan_id = scan_data.get("scan_id", "unknown")
        output_path = os.path.join(settings.REPORTS_DIR, f"ACDRIP_Report_{scan_id}_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=28,
        spaceAfter=6,
        textColor=colors.HexColor("#00bcd4"),
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        spaceAfter=20,
        textColor=colors.HexColor("#666666"),
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=20,
        textColor=colors.HexColor("#1a237e"),
        fontName="Helvetica-Bold",
    )

    subheading_style = ParagraphStyle(
        "CustomSubheading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor("#283593"),
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=6,
        leading=14,
    )

    elements = []

    # ── Cover Page ────────────────────────────────────────────

    elements.append(Spacer(1, 80))
    elements.append(Paragraph("ACDRIP+", title_style))
    elements.append(Paragraph(
        "Autonomous Cyber Defense, Risk Intelligence &amp; Pre-Breach Simulation Platform",
        subtitle_style
    ))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=colors.HexColor("#00bcd4"),
        spaceAfter=20
    ))

    elements.append(Paragraph("SECURITY ASSESSMENT REPORT", ParagraphStyle(
        "ReportTitle", parent=styles["Heading1"], fontSize=22,
        textColor=colors.HexColor("#d32f2f"), alignment=1
    )))

    elements.append(Spacer(1, 30))

    # Report metadata
    meta_data = [
        ["Report ID:", scan_data.get("scan_id", "N/A")],
        ["Target:", scan_data.get("target_ip", "N/A")],
        ["Date:", datetime.now(timezone.utc).strftime("%B %d, %Y %H:%M UTC")],
        ["Risk Level:", scan_data.get("risk_level", "N/A")],
        ["Risk Score:", f"{scan_data.get('risk_score', 0)}/100"],
        ["Platform:", "ACDRIP+ v" + settings.APP_VERSION],
        ["Classification:", "CONFIDENTIAL"],
    ]

    meta_table = Table(meta_data, colWidths=[120, 350])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#333333")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(meta_table)

    elements.append(PageBreak())

    # ── Table of Contents ────────────────────────────────────

    elements.append(Paragraph("Table of Contents", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))
    toc_items = [
        "1. Executive Summary",
        "2. Risk Analysis & Vulnerability Distribution",
        "3. Open Ports & Services",
        "4. Vulnerability Details",
        "5. Attack Simulation Results",
        "6. Financial Risk Assessment",
        "7. Remediation Recommendations",
        "8. Compliance & Security Posture",
    ]
    for item in toc_items:
        elements.append(Paragraph(item, body_style))
    elements.append(PageBreak())

    # ── 1. Executive Summary ─────────────────────────────────

    elements.append(Paragraph("1. Executive Summary", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    risk_score = scan_data.get("risk_score", 0)
    risk_level = scan_data.get("risk_level", "Unknown")
    num_vulns = len(scan_data.get("vulnerabilities", []))
    num_ports = len(scan_data.get("open_ports", []))

    summary_text = (
        f"This security assessment was conducted by <b>ACDRIP+ (Autonomous Cyber Defense, Risk Intelligence "
        f"&amp; Pre-Breach Simulation Platform)</b> against <b>{scan_data.get('target_ip', 'N/A')}</b> "
        f"and identified <b>{num_ports} open ports</b> and <b>{num_vulns} potential vulnerabilities</b>. "
        f"The overall risk score is <b>{risk_score}/100</b> ({risk_level}). "
    )

    if scan_data.get("os_detection"):
        summary_text += f"<br/><br/>Detected operating system: <b>{scan_data['os_detection']}</b>. "

    if risk_score >= 70:
        summary_text += (
            "<br/><br/><b>CRITICAL:</b> Immediate action is required. Multiple high-severity "
            "vulnerabilities were identified that could lead to system compromise, data exfiltration, "
            "or ransomware deployment."
        )
    elif risk_score >= 40:
        summary_text += (
            "<br/><br/><b>WARNING:</b> Several vulnerabilities require attention. "
            "Remediation should be prioritized within the next 30 days to prevent potential exploitation."
        )
    else:
        summary_text += (
            "<br/><br/>The target has a relatively low risk profile, but continuous "
            "monitoring is recommended to maintain security posture."
        )

    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 15))

    # Key findings summary table
    vulns = scan_data.get("vulnerabilities", [])
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for v in vulns:
        sev = v.get("severity", "info").lower()
        if sev in severity_counts:
            severity_counts[sev] += 1

    findings_data = [
        ["Finding Category", "Count", "Risk Impact"],
        ["Critical Vulnerabilities", str(severity_counts["critical"]), "Immediate exploitation possible"],
        ["High Vulnerabilities", str(severity_counts["high"]), "Exploitation likely within days"],
        ["Medium Vulnerabilities", str(severity_counts["medium"]), "Moderate risk, patch within 30 days"],
        ["Low Vulnerabilities", str(severity_counts["low"]), "Minimal immediate risk"],
        ["Informational", str(severity_counts["info"]), "Best practice recommendations"],
        ["Open Ports", str(num_ports), "Attack surface exposure"],
    ]

    findings_table = Table(findings_data, colWidths=[150, 60, 260])
    findings_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("Key Findings Summary", subheading_style))
    elements.append(findings_table)
    elements.append(Spacer(1, 15))

    # ── 2. Risk Analysis ──────────────────────────────────────

    elements.append(PageBreak())
    elements.append(Paragraph("2. Risk Analysis &amp; Vulnerability Distribution", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    # Severity distribution pie chart
    if any(severity_counts.values()):
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 15
        pie.width = 170
        pie.height = 170

        data = []
        labels = []
        pie_colors = []
        color_map = {
            "critical": colors.HexColor("#d32f2f"),
            "high": colors.HexColor("#f57c00"),
            "medium": colors.HexColor("#ffc107"),
            "low": colors.HexColor("#4caf50"),
            "info": colors.HexColor("#2196f3"),
        }

        for sev, count in severity_counts.items():
            if count > 0:
                data.append(count)
                labels.append(f"{sev.title()}: {count}")
                pie_colors.append(color_map[sev])

        pie.data = data
        pie.labels = labels
        pie.sideLabels = True

        for i, c in enumerate(pie_colors):
            pie.slices[i].fillColor = c
            pie.slices[i].strokeWidth = 0.5
            pie.slices[i].strokeColor = colors.white

        drawing.add(pie)
        elements.append(Paragraph("Vulnerability Severity Distribution", subheading_style))
        elements.append(drawing)
        elements.append(Spacer(1, 10))

    # CVSS Score Analysis
    if vulns:
        max_cvss = max(v.get("cvss_score", 0) for v in vulns)
        avg_cvss = sum(v.get("cvss_score", 0) for v in vulns) / len(vulns)
        elements.append(Paragraph("CVSS Score Analysis", subheading_style))
        cvss_data = [
            ["Metric", "Value"],
            ["Average CVSS Score", f"{avg_cvss:.1f}"],
            ["Maximum CVSS Score", f"{max_cvss:.1f}"],
            ["Total Vulnerabilities", str(len(vulns))],
            ["Attack Surface Score", f"{min(100, num_ports * 5 + len(vulns) * 3)}/100"],
        ]
        cvss_table = Table(cvss_data, colWidths=[200, 270])
        cvss_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e3f2fd")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(cvss_table)

    elements.append(Spacer(1, 15))

    # ── 3. Open Ports & Services ─────────────────────────────

    elements.append(PageBreak())
    elements.append(Paragraph("3. Open Ports &amp; Services", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    services = scan_data.get("services", [])
    if services:
        port_data = [["Port", "Protocol", "Service", "Version"]]
        for svc in services:
            port_data.append([
                str(svc.get("port", "")),
                svc.get("protocol", "tcp"),
                svc.get("service", "unknown"),
                svc.get("version", ""),
            ])

        port_table = Table(port_data, colWidths=[60, 70, 120, 220])
        port_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(port_table)

        # Service risk assessment
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Service Risk Notes:", subheading_style))
        high_risk_services = {"ssh": "Ensure key-based auth only", "ftp": "Consider replacing with SFTP",
                              "telnet": "CRITICAL: Replace with SSH immediately", "mysql": "Ensure not exposed to public",
                              "rdp": "Enable NLA and strong passwords", "smb": "Block from external access",
                              "http": "Ensure HTTPS redirect is enforced"}
        for svc in services:
            svc_name = svc.get("service", "").lower()
            if svc_name in high_risk_services:
                elements.append(Paragraph(
                    f"• <b>{svc.get('service', '')} (port {svc.get('port', '')})</b>: {high_risk_services[svc_name]}",
                    body_style
                ))
    else:
        elements.append(Paragraph("No open ports detected.", body_style))

    elements.append(Spacer(1, 15))

    # ── 4. Vulnerabilities ───────────────────────────────────

    elements.append(PageBreak())
    elements.append(Paragraph("4. Vulnerability Details", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    if vulns:
        vuln_data = [["CVE ID", "Port", "Severity", "CVSS", "Description"]]
        for v in vulns:
            vuln_data.append([
                v.get("cve_id", "N/A"),
                str(v.get("port", "")),
                v.get("severity", "info").upper(),
                str(v.get("cvss_score", 0)),
                Paragraph(v.get("description", "")[:120], ParagraphStyle(
                    "VulnDesc", fontSize=8, leading=10
                )),
            ])

        vuln_table = Table(vuln_data, colWidths=[90, 40, 60, 40, 240])
        vuln_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#b71c1c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff3f3")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(vuln_table)

        # Detailed vulnerability remediation
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Detailed Remediation Steps:", subheading_style))
        seen = set()
        for v in vulns:
            rec = v.get("recommendation", "")
            cve = v.get("cve_id", "")
            if rec and cve not in seen:
                seen.add(cve)
                elements.append(Paragraph(
                    f"<b>{cve}</b> ({v.get('severity', 'info').upper()}, CVSS: {v.get('cvss_score', 0)}): {rec}",
                    body_style
                ))
    else:
        elements.append(Paragraph("No vulnerabilities identified.", body_style))

    elements.append(Spacer(1, 15))

    # ── 5. Attack Simulation Results ──────────────────────────

    elements.append(PageBreak())
    elements.append(Paragraph("5. Attack Simulation Results", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    sim_data = simulation_data or scan_data.get("simulation_data")
    if sim_data and isinstance(sim_data, dict):
        if "phases" in sim_data:
            # Full simulation data
            elements.append(Paragraph(
                f"<b>Simulation ID:</b> {sim_data.get('simulation_id', 'N/A')}<br/>"
                f"<b>Overall Risk:</b> {sim_data.get('overall_risk', 'N/A')}<br/>"
                f"<b>Attack Success Probability:</b> {sim_data.get('attack_success_probability', 0)}%<br/>"
                f"<b>Phases Succeeded:</b> {sim_data.get('phases_succeeded', 0)}/{sim_data.get('total_phases', 5)}<br/>"
                f"<b>Total Estimated Time:</b> {sim_data.get('total_estimated_time_minutes', 0)} minutes",
                body_style
            ))
            elements.append(Spacer(1, 10))

            # Phase details table
            phase_data = [["Phase", "Name", "Status", "Probability", "Est. Time"]]
            for p in sim_data.get("phases", []):
                phase_data.append([
                    str(p.get("phase", "")),
                    p.get("name", ""),
                    p.get("status", "").upper(),
                    f"{p.get('success_probability', 0)}%",
                    f"{p.get('estimated_time_minutes', 0)} min",
                ])

            phase_table = Table(phase_data, colWidths=[40, 140, 70, 80, 60])
            phase_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a148c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3e5f5")]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(Paragraph("Attack Chain Phase Analysis", subheading_style))
            elements.append(phase_table)
            elements.append(Spacer(1, 10))

            # MITRE ATT&CK Techniques
            elements.append(Paragraph("MITRE ATT&amp;CK Techniques Mapped", subheading_style))
            for p in sim_data.get("phases", []):
                for t in p.get("techniques", []):
                    elements.append(Paragraph(
                        f"• <b>{t.get('id', '')}: {t.get('name', '')}</b> — {t.get('detail', '')}",
                        body_style
                    ))

            # Mitigation recommendations  
            if sim_data.get("mitigations"):
                elements.append(Spacer(1, 10))
                elements.append(Paragraph("Simulation Mitigation Strategies", subheading_style))
                for m in sim_data["mitigations"]:
                    elements.append(Paragraph(
                        f"<b>[{m.get('priority', 'MEDIUM')}] {m.get('phase', '')}:</b> {m.get('action', '')} — {m.get('detail', '')}",
                        body_style
                    ))
        else:
            # Basic simulation data
            elements.append(Paragraph(
                f"<b>Attack Vectors Identified:</b> {', '.join(sim_data.get('attack_vectors', ['N/A']))}<br/>"
                f"<b>Mitigation Status:</b> {sim_data.get('mitigation_status', 'N/A')}<br/>"
                f"<b>Compliance Score:</b> {sim_data.get('compliance_score', 'N/A')}%",
                body_style
            ))
    else:
        elements.append(Paragraph(
            "No attack simulation data available. Run an attack simulation from the ACDRIP+ platform "
            "to include detailed multi-phase attack chain analysis in future reports.",
            body_style
        ))

    # ── 6. Financial Risk Assessment ─────────────────────────

    elements.append(PageBreak())
    elements.append(Paragraph("6. Financial Risk Assessment", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    if risk_data:
        fin_data = [
            ["Metric", "Value"],
            ["Total Assets", f"₹{risk_data.get('total_assets', 0):,.2f}"],
            ["Predicted Financial Loss", f"₹{risk_data.get('predicted_loss', 0):,.2f}"],
            ["Loss Percentage", f"{risk_data.get('loss_percentage', 0)}%"],
            ["Risk Level", risk_data.get("risk_level", "N/A")],
            ["Risk Probability", f"{risk_data.get('risk_probability', 0)}%"],
            ["Attack Probability", f"{risk_data.get('attack_probability', 0)}%"],
        ]

        fin_table = Table(fin_data, colWidths=[180, 290])
        fin_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e3f2fd")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(fin_table)

        # Risk distribution
        if risk_data.get("risk_distribution"):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Risk Distribution Probabilities:", subheading_style))
            dist = risk_data["risk_distribution"]
            dist_data = [
                ["Risk Category", "Probability"],
                ["Minimal", f"{dist.get('minimal', 0)}%"],
                ["Low", f"{dist.get('low', 0)}%"],
                ["Medium", f"{dist.get('medium', 0)}%"],
                ["High", f"{dist.get('high', 0)}%"],
                ["Critical", f"{dist.get('critical', 0)}%"],
            ]
            dist_table = Table(dist_data, colWidths=[180, 290])
            dist_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e65100")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff3e0")]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(dist_table)

        # AI Recommendations from risk engine
        if risk_data.get("recommendations"):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("AI-Generated Risk Recommendations:", subheading_style))
            for r in risk_data["recommendations"]:
                elements.append(Paragraph(
                    f"<b>[{r.get('priority', 'MEDIUM')}] {r.get('category', '')}:</b> {r.get('action', '')} — {r.get('detail', '')}",
                    body_style
                ))
    else:
        elements.append(Paragraph(
            "No financial risk data available for this report. Use the Risk Prediction Engine "
            "in ACDRIP+ to generate ML-based financial loss estimates.", body_style
        ))

    # ── 7. Recommendations ───────────────────────────────────

    elements.append(PageBreak())
    elements.append(Paragraph("7. Remediation Recommendations", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    if vulns:
        seen = set()
        for v in vulns:
            rec = v.get("recommendation", "")
            if rec and rec not in seen:
                seen.add(rec)
                priority = "HIGH" if v.get("severity") in ("critical", "high") else "MEDIUM"
                elements.append(Paragraph(
                    f"<b>[{priority}]</b> {v.get('cve_id', '')}: {rec}",
                    body_style
                ))

    # General recommendations
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("General Security Recommendations:", subheading_style))
    general_recs = [
        "Implement regular vulnerability scanning schedule (weekly automated, monthly manual)",
        "Deploy network segmentation to limit lateral movement between zones",
        "Enable multi-factor authentication (MFA) on all critical services and admin access",
        "Establish incident response procedures and test quarterly with tabletop exercises",
        "Maintain up-to-date patch management across all systems (automated where possible)",
        "Implement Security Information and Event Management (SIEM) for centralized logging",
        "Deploy Web Application Firewall (WAF) for all public-facing applications",
        "Conduct regular penetration testing (quarterly external, semi-annual internal)",
        "Implement Data Loss Prevention (DLP) policies for sensitive data",
        "Ensure backup and disaster recovery procedures are tested regularly",
    ]
    for rec in general_recs:
        elements.append(Paragraph(f"• {rec}", body_style))

    # ── 8. Compliance & Security Posture ───────────────────────

    elements.append(PageBreak())
    elements.append(Paragraph("8. Compliance &amp; Security Posture", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))

    compliance_score = max(0, 100 - severity_counts["critical"] * 20 - severity_counts["high"] * 10 - severity_counts["medium"] * 5 - num_ports * 2)
    compliance_score = min(100, compliance_score)

    comp_data = [
        ["Framework", "Assessment", "Score"],
        ["NIST CSF", "Based on vulnerability count and controls", f"{compliance_score}%"],
        ["ISO 27001", "Estimated control effectiveness", f"{max(0, compliance_score - 5)}%"],
        ["PCI DSS", "Payment data security posture", f"{max(0, compliance_score - 10)}%"],
        ["OWASP Top 10", "Web application security", f"{max(0, 100 - severity_counts['critical'] * 15 - severity_counts['high'] * 8)}%"],
        ["CIS Controls", "Infrastructure hardening level", f"{max(0, compliance_score - 8)}%"],
    ]

    comp_table = Table(comp_data, colWidths=[100, 220, 80])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b5e20")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8f5e9")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(comp_table)

    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Security Posture Assessment:", subheading_style))
    if compliance_score >= 80:
        posture_text = "The target system demonstrates a <b>STRONG</b> security posture with adequate controls in place. Continue maintaining current security practices and address any remaining vulnerabilities."
    elif compliance_score >= 50:
        posture_text = "The target system has a <b>MODERATE</b> security posture. Several areas require improvement, particularly in vulnerability management and access controls."
    else:
        posture_text = "The target system has a <b>WEAK</b> security posture with significant gaps in security controls. Immediate remediation is strongly recommended across all identified areas."
    elements.append(Paragraph(posture_text, body_style))

    # ── Footer ──────────────────────────────────────────────

    elements.append(Spacer(1, 40))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#00bcd4")))
    elements.append(Paragraph(
        f"<i>Generated by ACDRIP+ — Autonomous Cyber Defense, Risk Intelligence &amp; Pre-Breach Simulation Platform | "
        f"v{settings.APP_VERSION} | "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | "
        f"CONFIDENTIAL — FOR AUTHORIZED PERSONNEL ONLY</i>",
        ParagraphStyle("Footer", fontSize=8, textColor=colors.HexColor("#999999"), alignment=1)
    ))

    # Build PDF
    doc.build(elements)
    return output_path
