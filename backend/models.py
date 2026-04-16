"""
ACDRIP+ Database Models
All SQLAlchemy ORM models for the platform.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    target_ip = Column(String(45), nullable=False)
    scan_type = Column(String(50), default="full")
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="Unknown")
    open_ports = Column(JSON, default=list)
    services = Column(JSON, default=list)
    os_detection = Column(String(200), nullable=True)
    raw_output = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    user = relationship("User", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    cve_id = Column(String(30), nullable=True)
    port = Column(Integer, nullable=True)
    service = Column(String(100), nullable=True)
    severity = Column(String(20), default="info")  # critical, high, medium, low, info
    cvss_score = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    scan = relationship("Scan", back_populates="vulnerabilities")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=True)
    title = Column(String(200), nullable=False)
    report_type = Column(String(50), default="full")
    file_path = Column(String(500), nullable=True)
    content = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    user = relationship("User", back_populates="reports")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    target_ip = Column(String(45), nullable=False)
    alert_type = Column(String(50), nullable=False)  # port_change, new_service, suspicious_activity
    severity = Column(String(20), default="medium")
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    user = relationship("User", back_populates="alerts")


class MonitoredIP(Base):
    __tablename__ = "monitored_ips"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    target_ip = Column(String(45), nullable=False)
    is_active = Column(Boolean, default=True)
    interval_seconds = Column(Integer, default=300)  # 5 minutes
    last_scan = Column(JSON, nullable=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
