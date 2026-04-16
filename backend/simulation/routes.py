"""
ACDRIP+ Attack Simulation API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from database import get_db
from models import User, Scan, Vulnerability
from auth.utils import get_current_user
from simulation.attack_sim import simulate_attack
import re

router = APIRouter(prefix="/api/simulation", tags=["Attack Simulation"])


class SimulationRequest(BaseModel):
    target_ip: str
    scan_id: str = None  # Optional: use existing scan data

    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v):
        v = v.strip()
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        if not (re.match(ipv4_pattern, v) or re.match(domain_pattern, v)):
            raise ValueError("Invalid IP address or domain")
        return v


@router.post("/simulate")
def run_simulation(
    req: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run an attack simulation against the target."""
    scan_data = None

    # If scan_id provided, use existing scan data
    if req.scan_id:
        scan = db.query(Scan).filter(
            (Scan.scan_id == req.scan_id) | (Scan.id == req.scan_id)
        ).first()
        if scan:
            vulns = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()
            scan_data = {
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

    result = simulate_attack(req.target_ip, scan_data)
    return result
