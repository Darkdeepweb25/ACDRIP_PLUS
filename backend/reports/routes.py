"""
ACDRIP+ Report Generation API Routes
Autonomous Cyber Defense, Risk Intelligence & Pre-Breach Simulation Platform
"""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Scan, Vulnerability, Report
from auth.utils import get_current_user
from reports.pdf_generator import generate_report_pdf
from risk_engine.ml_model import risk_model
from simulation.attack_sim import simulate_attack

router = APIRouter(prefix="/api/reports", tags=["Reports"])


class ReportRequest(BaseModel):
    scan_id: str
    title: str = "ACDRIP+ Security Assessment Report"
    include_risk_data: bool = True
    risk_data: dict = None


@router.post("/generate")
def generate_report(
    req: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a comprehensive PDF security report with risk and simulation data."""
    # Find scan
    scan = db.query(Scan).filter(
        (Scan.scan_id == req.scan_id) | (Scan.id == req.scan_id)
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Get vulnerabilities
    vulns = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()

    num_critical = sum(1 for v in vulns if v.severity == "critical")
    num_high = sum(1 for v in vulns if v.severity == "high")

    scan_data = {
        "scan_id": scan.scan_id,
        "target_ip": scan.target_ip,
        "risk_score": scan.risk_score,
        "risk_level": scan.risk_level,
        "open_ports": scan.open_ports or [],
        "services": scan.services or [],
        "os_detection": scan.os_detection,
        "vulnerabilities": [
            {
                "cve_id": v.cve_id,
                "port": v.port,
                "service": v.service,
                "severity": v.severity,
                "cvss_score": v.cvss_score,
                "description": v.description,
                "recommendation": v.recommendation,
            }
            for v in vulns
        ],
    }

    # Auto-generate risk data if not provided
    risk_data = req.risk_data
    if risk_data is None and req.include_risk_data:
        try:
            risk_data = risk_model.predict(
                total_assets=10000000,  # Default
                num_critical_vulns=num_critical,
                num_high_vulns=num_high,
                num_open_ports=len(scan.open_ports or []),
                has_firewall=True,
                has_ids=False,
                employee_count=50,
                industry_risk_factor=0.6,
            )
        except Exception:
            risk_data = None

    # Auto-generate simulation data
    simulation_data = None
    try:
        sim_scan_data = {
            "open_ports": scan.open_ports or [],
            "services": scan.services or [],
            "risk_score": scan.risk_score or 50,
            "vulnerabilities": [
                {
                    "cve_id": v.cve_id,
                    "port": v.port,
                    "service": v.service,
                    "severity": v.severity,
                    "cvss_score": v.cvss_score,
                }
                for v in vulns
            ],
        }
        simulation_data = simulate_attack(scan.target_ip, sim_scan_data)
    except Exception:
        simulation_data = None

    # Generate PDF with all data
    pdf_path = generate_report_pdf(scan_data, risk_data, simulation_data)

    if pdf_path is None:
        raise HTTPException(
            status_code=500,
            detail="PDF generation failed — ReportLab may not be installed"
        )

    # Save report record
    report = Report(
        user_id=current_user.id,
        scan_id=scan.id,
        title=req.title,
        report_type="full",
        file_path=pdf_path,
        content=scan_data,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "title": report.title,
        "file_path": pdf_path,
        "download_url": f"/api/reports/download/{report.id}",
        "created_at": str(report.created_at),
    }


@router.get("/download/{report_id}")
def download_report(
    report_id: str,
    db: Session = Depends(get_db),
):
    """Download a generated PDF report."""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    return FileResponse(
        path=report.file_path,
        media_type="application/pdf",
        content_disposition_type="inline"
    )


@router.get("/list")
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all reports for the current user."""
    reports = (
        db.query(Report)
        .filter(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "report_type": r.report_type,
            "download_url": f"/api/reports/download/{r.id}",
            "created_at": str(r.created_at),
        }
        for r in reports
    ]


@router.delete("/{report_id}")
def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a generated report."""
    report = db.query(Report).filter(
        Report.id == report_id, Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.file_path and os.path.exists(report.file_path):
        try:
            os.remove(report.file_path)
        except OSError:
            pass

    db.delete(report)
    db.commit()
    return {"status": "success", "message": "Report deleted"}
