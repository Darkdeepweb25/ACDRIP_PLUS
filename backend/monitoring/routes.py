"""
ACDRIP+ Alert Monitoring API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from database import get_db
from models import User, Alert
from auth.utils import get_current_user
from monitoring.alert_service import alert_monitor
import re

router = APIRouter(prefix="/api/monitoring", tags=["Alert Monitoring"])


class MonitorRequest(BaseModel):
    target_ip: str
    interval_seconds: int = 300

    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v):
        v = v.strip()
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        if not (re.match(ipv4_pattern, v) or re.match(domain_pattern, v)):
            raise ValueError("Invalid IP address or domain")
        return v


class StopMonitorRequest(BaseModel):
    target_ip: str


@router.post("/start")
def start_monitoring(
    req: MonitorRequest,
    current_user: User = Depends(get_current_user),
):
    """Start monitoring an IP address for changes."""
    result = alert_monitor.start_monitoring(
        user_id=current_user.id,
        target_ip=req.target_ip,
        interval=req.interval_seconds,
    )
    return result


@router.post("/stop")
def stop_monitoring(
    req: StopMonitorRequest,
    current_user: User = Depends(get_current_user),
):
    """Stop monitoring an IP address."""
    result = alert_monitor.stop_monitoring(
        user_id=current_user.id,
        target_ip=req.target_ip,
    )
    return result


@router.get("/status")
def get_monitoring_status(current_user: User = Depends(get_current_user)):
    """Get all monitored IPs and their status."""
    return alert_monitor.get_monitoring_status(current_user.id)


@router.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all alerts for the current user."""
    alerts = (
        db.query(Alert)
        .filter(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": a.id,
            "target_ip": a.target_ip,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "details": a.details,
            "is_read": a.is_read,
            "created_at": str(a.created_at),
        }
        for a in alerts
    ]


@router.put("/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as read."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id,
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.commit()
    return {"status": "marked_read"}
