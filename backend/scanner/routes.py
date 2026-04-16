"""
ACDRIP+ Network Scanner API Routes
Endpoints for running scans, retrieving results, and public scanning.
"""

import re
import random
import string
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from database import get_db
from models import User, Scan, Vulnerability
from auth.utils import get_current_user
from scanner.nmap_service import run_scan

router = APIRouter(prefix="/api/scanner", tags=["Network Scanner"])


# ── Schemas ───────────────────────────────────────────────────

class ScanRequest(BaseModel):
    target_ip: str

    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v):
        v = v.strip()
        # IPv4 validation
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        # Domain validation
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        # CIDR notation
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'

        if not (re.match(ipv4_pattern, v) or re.match(domain_pattern, v) or re.match(cidr_pattern, v)):
            raise ValueError("Invalid IP address or domain")

        # Block private/reserved ranges for security
        dangerous = ["127.0.0.1", "0.0.0.0", "localhost"]
        if v.lower() in dangerous:
            raise ValueError("Scanning localhost is not permitted in production")

        return v


def _generate_scan_id() -> str:
    """Generate a unique scan ID like ACD-XXXX."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f"ACD-{suffix}"


# ── Public Scan (No Auth Required) ──────────────────────────

@router.post("/public-scan")
def public_scan(req: ScanRequest, db: Session = Depends(get_db)):
    """Run a quick scan without authentication (landing page)."""
    result = run_scan(req.target_ip)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    scan = db.query(Scan).filter(Scan.target_ip == req.target_ip, Scan.user_id == None).first()
    
    if scan:
        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.risk_score = result["risk_score"]
        scan.risk_level = result["risk_level"]
        scan.open_ports = result["open_ports"]
        scan.services = result["services"]
        scan.os_detection = result.get("os_detection")
        db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).delete()
        scan_id = scan.scan_id
    else:
        scan_id = _generate_scan_id()
        scan = Scan(
            scan_id=scan_id,
            target_ip=req.target_ip,
            status="completed",
            completed_at=datetime.now(timezone.utc),
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            open_ports=result["open_ports"],
            services=result["services"],
            os_detection=result.get("os_detection"),
        )
        db.add(scan)
        
    db.flush()

    # Save vulnerabilities
    for v in result.get("vulnerabilities", []):
        vuln = Vulnerability(
            scan_id=scan.id,
            cve_id=v["cve_id"],
            port=v["port"],
            service=v["service"],
            severity=v["severity"],
            cvss_score=v["cvss_score"],
            description=v["description"],
            recommendation=v["recommendation"],
        )
        db.add(vuln)

    db.commit()
    db.refresh(scan)

    result["scan_id"] = scan_id
    result["db_id"] = scan.id
    return result


# ── Authenticated Scan ──────────────────────────────────────

@router.post("/scan")
def authenticated_scan(
    req: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run a full scan as an authenticated user."""
    result = run_scan(req.target_ip)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Check if scan exists for the same IP
    scan = db.query(Scan).filter(Scan.target_ip == req.target_ip, Scan.user_id == current_user.id).first()
    
    if scan:
        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.risk_score = result["risk_score"]
        scan.risk_level = result["risk_level"]
        scan.open_ports = result["open_ports"]
        scan.services = result["services"]
        scan.os_detection = result.get("os_detection")
        db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).delete()
        scan_id = scan.scan_id
    else:
        scan_id = _generate_scan_id()
        scan = Scan(
            scan_id=scan_id,
            user_id=current_user.id,
            target_ip=req.target_ip,
            status="completed",
            completed_at=datetime.now(timezone.utc),
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            open_ports=result["open_ports"],
            services=result["services"],
            os_detection=result.get("os_detection"),
        )
        db.add(scan)
    
    db.flush()

    for v in result.get("vulnerabilities", []):
        vuln = Vulnerability(
            scan_id=scan.id,
            cve_id=v["cve_id"],
            port=v["port"],
            service=v["service"],
            severity=v["severity"],
            cvss_score=v["cvss_score"],
            description=v["description"],
            recommendation=v["recommendation"],
        )
        db.add(vuln)

    db.commit()
    db.refresh(scan)

    result["scan_id"] = scan_id
    result["db_id"] = scan.id
    return result


# ── Get Scan History ────────────────────────────────────────

@router.get("/history")
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all scans for the current user."""
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "scan_id": s.scan_id,
            "target_ip": s.target_ip,
            "status": s.status,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "open_ports": s.open_ports,
            "services": s.services,
            "os_detection": s.os_detection,
            "created_at": str(s.created_at),
            "completed_at": str(s.completed_at) if s.completed_at else None,
        }
        for s in scans
    ]


# ── Get Single Scan ────────────────────────────────────────

@router.get("/scan/{scan_id}")
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    """Get a specific scan by scan_id."""
    scan = db.query(Scan).filter(
        (Scan.scan_id == scan_id) | (Scan.id == scan_id)
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    vulns = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()

    return {
        "id": scan.id,
        "scan_id": scan.scan_id,
        "target_ip": scan.target_ip,
        "status": scan.status,
        "risk_score": scan.risk_score,
        "risk_level": scan.risk_level,
        "open_ports": scan.open_ports,
        "services": scan.services,
        "os_detection": scan.os_detection,
        "created_at": str(scan.created_at),
        "completed_at": str(scan.completed_at) if scan.completed_at else None,
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


# ── Get Latest Scan by IP ──────────────────────────────────

@router.get("/by-ip/{target_ip}")
def get_scan_by_ip(target_ip: str, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    """Get the most recent scan for a given IP (for auto-fill)."""
    scan = (
        db.query(Scan)
        .filter(Scan.target_ip == target_ip, Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .first()
    )

    if not scan:
        raise HTTPException(status_code=404, detail="No scan found for this IP")

    vulns = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()

    num_critical = sum(1 for v in vulns if v.severity == "critical")
    num_high = sum(1 for v in vulns if v.severity == "high")
    num_medium = sum(1 for v in vulns if v.severity == "medium")

    return {
        "id": scan.id,
        "scan_id": scan.scan_id,
        "target_ip": scan.target_ip,
        "risk_score": scan.risk_score,
        "risk_level": scan.risk_level,
        "open_ports": scan.open_ports or [],
        "services": scan.services or [],
        "os_detection": scan.os_detection,
        "num_open_ports": len(scan.open_ports or []),
        "num_critical_vulns": num_critical,
        "num_high_vulns": num_high,
        "num_medium_vulns": num_medium,
        "total_vulns": len(vulns),
        "created_at": str(scan.created_at),
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
