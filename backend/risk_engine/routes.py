"""
ACDRIP+ Risk Prediction API Routes
Endpoints for financial risk analysis using the ML model.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth.utils import get_current_user
from risk_engine.ml_model import risk_model

router = APIRouter(prefix="/api/risk", tags=["Risk Prediction"])


class RiskPredictionRequest(BaseModel):
    total_assets: float
    num_critical_vulns: int = 3
    num_high_vulns: int = 5
    num_open_ports: int = 8
    has_firewall: bool = True
    has_ids: bool = False
    employee_count: int = 50
    industry_risk_factor: float = 0.6

    @field_validator("total_assets")
    @classmethod
    def validate_assets(cls, v):
        if v <= 0:
            raise ValueError("Total assets must be positive")
        if v > 1e15:
            raise ValueError("Total assets value too large")
        return v

    @field_validator("industry_risk_factor")
    @classmethod
    def validate_risk_factor(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Industry risk factor must be between 0 and 1")
        return v


@router.post("/predict")
def predict_risk(
    req: RiskPredictionRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict financial risk from a potential cyber attack."""
    result = risk_model.predict(
        total_assets=req.total_assets,
        num_critical_vulns=req.num_critical_vulns,
        num_high_vulns=req.num_high_vulns,
        num_open_ports=req.num_open_ports,
        has_firewall=req.has_firewall,
        has_ids=req.has_ids,
        employee_count=req.employee_count,
        industry_risk_factor=req.industry_risk_factor,
    )
    return result


@router.post("/quick-predict")
def quick_predict(req: RiskPredictionRequest):
    """Quick risk prediction (no auth required for demo)."""
    result = risk_model.predict(
        total_assets=req.total_assets,
        num_critical_vulns=req.num_critical_vulns,
        num_high_vulns=req.num_high_vulns,
        num_open_ports=req.num_open_ports,
        has_firewall=req.has_firewall,
        has_ids=req.has_ids,
        employee_count=req.employee_count,
        industry_risk_factor=req.industry_risk_factor,
    )
    return result
