"""
ACDRIP+ Alert Monitoring Service
Background monitoring of IPs for port changes and suspicious activity.
"""

import threading
import time
import hashlib
import random
from datetime import datetime, timezone
from typing import Dict, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Alert, MonitoredIP
from scanner.nmap_service import run_scan


class AlertMonitor:
    """Background IP monitoring service."""

    def __init__(self):
        self._monitors: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}
        self._active = True
        print("[OK] Alert monitoring service initialized")

    def start_monitoring(self, user_id: str, target_ip: str, interval: int = 300) -> dict:
        """Start monitoring an IP address in the background."""
        key = f"{user_id}:{target_ip}"

        if key in self._monitors and self._monitors[key].is_alive():
            return {"status": "already_monitoring", "target_ip": target_ip}

        # Save to database
        db = SessionLocal()
        try:
            existing = db.query(MonitoredIP).filter(
                MonitoredIP.user_id == user_id,
                MonitoredIP.target_ip == target_ip,
            ).first()

            if existing:
                existing.is_active = True
                existing.interval_seconds = interval
            else:
                monitored = MonitoredIP(
                    user_id=user_id,
                    target_ip=target_ip,
                    interval_seconds=interval,
                    is_active=True,
                )
                db.add(monitored)
            db.commit()
        finally:
            db.close()

        # Start background monitoring thread
        stop_event = threading.Event()
        self._stop_events[key] = stop_event

        thread = threading.Thread(
            target=self._monitor_loop,
            args=(user_id, target_ip, interval, stop_event),
            daemon=True
        )
        thread.start()
        self._monitors[key] = thread

        return {
            "status": "monitoring_started",
            "target_ip": target_ip,
            "interval_seconds": interval,
        }

    def stop_monitoring(self, user_id: str, target_ip: str) -> dict:
        """Stop monitoring an IP address."""
        key = f"{user_id}:{target_ip}"

        if key in self._stop_events:
            self._stop_events[key].set()
            del self._stop_events[key]

        # Update database
        db = SessionLocal()
        try:
            monitored = db.query(MonitoredIP).filter(
                MonitoredIP.user_id == user_id,
                MonitoredIP.target_ip == target_ip,
            ).first()
            if monitored:
                monitored.is_active = False
                db.commit()
        finally:
            db.close()

        return {"status": "monitoring_stopped", "target_ip": target_ip}

    def _monitor_loop(self, user_id: str, target_ip: str, interval: int, stop_event: threading.Event):
        """Background monitoring loop."""
        previous_scan = None

        while not stop_event.is_set():
            try:
                current_scan = run_scan(target_ip)

                if previous_scan:
                    # Detect changes
                    alerts = self._detect_changes(
                        user_id, target_ip, previous_scan, current_scan
                    )
                    if alerts:
                        self._save_alerts(user_id, target_ip, alerts)

                # Update last scan in DB
                db = SessionLocal()
                try:
                    monitored = db.query(MonitoredIP).filter(
                        MonitoredIP.user_id == user_id,
                        MonitoredIP.target_ip == target_ip,
                    ).first()
                    if monitored:
                        monitored.last_scan = {
                            "open_ports": current_scan.get("open_ports", []),
                            "risk_score": current_scan.get("risk_score", 0),
                        }
                        monitored.last_checked = datetime.now(timezone.utc)
                        db.commit()
                finally:
                    db.close()

                previous_scan = current_scan

            except Exception as e:
                print(f"[!] Monitor error for {target_ip}: {str(e)}")

            # Wait for interval or stop event
            stop_event.wait(timeout=interval)

    def _detect_changes(self, user_id: str, target_ip: str, old_scan: dict, new_scan: dict) -> list:
        """Detect changes between two scans."""
        alerts = []

        old_ports = set(old_scan.get("open_ports", []))
        new_ports = set(new_scan.get("open_ports", []))

        # New ports opened
        opened = new_ports - old_ports
        for port in opened:
            alerts.append({
                "alert_type": "port_opened",
                "severity": "high",
                "message": f"New port {port} opened on {target_ip}",
                "details": {"port": port, "change": "opened"},
            })

        # Ports closed
        closed = old_ports - new_ports
        for port in closed:
            alerts.append({
                "alert_type": "port_closed",
                "severity": "medium",
                "message": f"Port {port} closed on {target_ip}",
                "details": {"port": port, "change": "closed"},
            })

        # Risk score change
        old_risk = old_scan.get("risk_score", 0)
        new_risk = new_scan.get("risk_score", 0)
        if new_risk > old_risk + 10:
            alerts.append({
                "alert_type": "risk_increase",
                "severity": "high",
                "message": f"Risk score increased from {old_risk} to {new_risk} on {target_ip}",
                "details": {"old_score": old_risk, "new_score": new_risk},
            })

        return alerts

    def _save_alerts(self, user_id: str, target_ip: str, alerts: list):
        """Save alerts to database."""
        db = SessionLocal()
        try:
            for alert_data in alerts:
                alert = Alert(
                    user_id=user_id,
                    target_ip=target_ip,
                    alert_type=alert_data["alert_type"],
                    severity=alert_data["severity"],
                    message=alert_data["message"],
                    details=alert_data.get("details"),
                )
                db.add(alert)
            db.commit()
        finally:
            db.close()

    def get_monitoring_status(self, user_id: str) -> list:
        """Get all monitored IPs for a user."""
        db = SessionLocal()
        try:
            monitored = db.query(MonitoredIP).filter(
                MonitoredIP.user_id == user_id
            ).all()

            return [
                {
                    "id": m.id,
                    "target_ip": m.target_ip,
                    "is_active": m.is_active,
                    "interval_seconds": m.interval_seconds,
                    "last_checked": str(m.last_checked) if m.last_checked else None,
                    "last_scan": m.last_scan,
                }
                for m in monitored
            ]
        finally:
            db.close()


# Global monitor instance
alert_monitor = AlertMonitor()
