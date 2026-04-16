"""
ACDRIP+ Configuration Module
Autonomous Cyber Defense, Risk Intelligence & Pre-Breach Simulation Platform
"""

import os
from datetime import timedelta


class Settings:
    # Application
    APP_NAME = "ACDRIP+"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Autonomous Cyber Defense, Risk Intelligence & Pre-Breach Simulation Platform"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./acdrip_plus.db"
    )

    # JWT Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "acdrip-plus-super-secret-key-change-in-production-2026")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 1440))  # 24 hours

    # Rate Limiting
    RATE_LIMIT = os.getenv("RATE_LIMIT", "60/minute")

    # Nmap
    NMAP_PATH = os.getenv("NMAP_PATH", "nmap")
    SCAN_TIMEOUT = int(os.getenv("SCAN_TIMEOUT", 300))  # 5 minutes

    # Reports directory
    REPORTS_DIR = os.getenv("REPORTS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports_output"))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


settings = Settings()
