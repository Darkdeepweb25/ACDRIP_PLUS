"""
ACDRIP+ Risk Prediction ML Model
Uses scikit-learn for financial risk prediction based on cyber attack scenarios.
"""

import numpy as np
import json
import os

# Try to import sklearn, fall back to manual model
try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import pickle
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[!] scikit-learn not available - using built-in risk model")


class RiskPredictionModel:
    """ML-based financial risk prediction engine."""

    def __init__(self):
        self.loss_model = None
        self.risk_classifier = None
        self.scaler = None
        self.is_trained = False
        self._train_model()

    def _generate_training_data(self):
        """Generate synthetic training data for the risk model."""
        np.random.seed(42)
        n_samples = 2000

        # Features: [total_assets, num_critical_vulns, num_high_vulns,
        #            num_open_ports, has_firewall, has_ids, employee_count,
        #            industry_risk_factor]
        total_assets = np.random.lognormal(mean=15, sigma=2, size=n_samples)  # ₹ in various ranges
        num_critical = np.random.poisson(lam=2, size=n_samples)
        num_high = np.random.poisson(lam=5, size=n_samples)
        num_ports = np.random.poisson(lam=8, size=n_samples)
        has_firewall = np.random.binomial(1, 0.7, size=n_samples)
        has_ids = np.random.binomial(1, 0.5, size=n_samples)
        employee_count = np.random.lognormal(mean=4, sigma=1.5, size=n_samples).astype(int)
        industry_risk = np.random.uniform(0.2, 1.0, size=n_samples)

        X = np.column_stack([
            total_assets, num_critical, num_high, num_ports,
            has_firewall, has_ids, employee_count, industry_risk
        ])

        # Loss = f(assets, vulnerabilities, controls)
        base_loss_rate = 0.001 + 0.02 * num_critical + 0.008 * num_high + 0.002 * num_ports
        protection_factor = 1.0 - (0.3 * has_firewall + 0.2 * has_ids)
        noise = np.random.normal(1.0, 0.15, size=n_samples)
        y_loss = total_assets * base_loss_rate * protection_factor * industry_risk * noise
        y_loss = np.maximum(y_loss, 0)

        # Risk categories
        loss_ratio = y_loss / total_assets
        y_risk = np.zeros(n_samples, dtype=int)
        y_risk[loss_ratio > 0.001] = 1  # Low
        y_risk[loss_ratio > 0.01] = 2   # Medium
        y_risk[loss_ratio > 0.05] = 3   # High
        y_risk[loss_ratio > 0.15] = 4   # Critical

        return X, y_loss, y_risk

    def _train_model(self):
        """Train the risk prediction models."""
        X, y_loss, y_risk = self._generate_training_data()

        if SKLEARN_AVAILABLE:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Loss prediction model
            self.loss_model = GradientBoostingRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
            )
            self.loss_model.fit(X_scaled, y_loss)

            # Risk classification model
            self.risk_classifier = RandomForestClassifier(
                n_estimators=100, max_depth=8, random_state=42
            )
            self.risk_classifier.fit(X_scaled, y_risk)

            self.is_trained = True
            print("[OK] ML risk prediction models trained successfully")
        else:
            self.is_trained = True
            print("[OK] Built-in risk model initialized")

    def predict(
        self,
        total_assets: float,
        num_critical_vulns: int = 3,
        num_high_vulns: int = 5,
        num_open_ports: int = 8,
        has_firewall: bool = True,
        has_ids: bool = False,
        employee_count: int = 50,
        industry_risk_factor: float = 0.6,
    ) -> dict:
        """Predict financial loss and risk level from a cyber attack."""

        features = np.array([[
            total_assets, num_critical_vulns, num_high_vulns, num_open_ports,
            int(has_firewall), int(has_ids), employee_count, industry_risk_factor
        ]])

        if SKLEARN_AVAILABLE and self.loss_model is not None:
            X_scaled = self.scaler.transform(features)
            predicted_loss = float(self.loss_model.predict(X_scaled)[0])
            risk_class = int(self.risk_classifier.predict(X_scaled)[0])
            risk_proba = self.risk_classifier.predict_proba(X_scaled)[0].tolist()
        else:
            # Fallback calculation
            base_rate = 0.001 + 0.02 * num_critical_vulns + 0.008 * num_high_vulns
            protection = 1.0 - (0.3 * int(has_firewall) + 0.2 * int(has_ids))
            predicted_loss = total_assets * base_rate * protection * industry_risk_factor
            loss_ratio = predicted_loss / total_assets if total_assets > 0 else 0

            if loss_ratio > 0.15:
                risk_class = 4
            elif loss_ratio > 0.05:
                risk_class = 3
            elif loss_ratio > 0.01:
                risk_class = 2
            elif loss_ratio > 0.001:
                risk_class = 1
            else:
                risk_class = 0
            risk_proba = [0.0] * 5
            risk_proba[risk_class] = 1.0

        predicted_loss = max(0, predicted_loss)
        risk_labels = ["Minimal", "Low", "Medium", "High", "Critical"]
        risk_level = risk_labels[min(risk_class, 4)]

        # Risk probability percentage
        risk_probability = round(max(risk_proba) * 100, 1) if risk_proba else 50.0
        attack_probability = min(
            95.0,
            round(
                (num_critical_vulns * 12 + num_high_vulns * 6 + num_open_ports * 2)
                * industry_risk_factor
                * (2 - int(has_firewall) * 0.5 - int(has_ids) * 0.3),
                1
            )
        )

        # Recommendations
        recommendations = self._generate_recommendations(
            risk_level, num_critical_vulns, num_high_vulns,
            num_open_ports, has_firewall, has_ids
        )

        return {
            "total_assets": total_assets,
            "predicted_loss": round(predicted_loss, 2),
            "loss_percentage": round((predicted_loss / total_assets * 100) if total_assets > 0 else 0, 2),
            "risk_level": risk_level,
            "risk_class": risk_class,
            "risk_probability": risk_probability,
            "attack_probability": attack_probability,
            "risk_distribution": {
                "minimal": round(risk_proba[0] * 100, 1) if len(risk_proba) > 0 else 0,
                "low": round(risk_proba[1] * 100, 1) if len(risk_proba) > 1 else 0,
                "medium": round(risk_proba[2] * 100, 1) if len(risk_proba) > 2 else 0,
                "high": round(risk_proba[3] * 100, 1) if len(risk_proba) > 3 else 0,
                "critical": round(risk_proba[4] * 100, 1) if len(risk_proba) > 4 else 0,
            },
            "recommendations": recommendations,
        }

    def _generate_recommendations(
        self, risk_level, num_critical, num_high, num_ports, has_fw, has_ids
    ) -> list:
        """Generate AI-driven security recommendations."""
        recs = []

        if num_critical > 0:
            recs.append({
                "priority": "CRITICAL",
                "category": "Patch Management",
                "action": f"Immediately patch {num_critical} critical vulnerabilities",
                "detail": "Critical CVEs enable remote code execution. Apply vendor patches within 24 hours.",
            })

        if num_high > 3:
            recs.append({
                "priority": "HIGH",
                "category": "Vulnerability Remediation",
                "action": f"Address {num_high} high-severity vulnerabilities within 7 days",
                "detail": "Schedule emergency maintenance window for critical patching.",
            })

        if not has_fw:
            recs.append({
                "priority": "HIGH",
                "category": "Network Security",
                "action": "Deploy enterprise-grade firewall immediately",
                "detail": "Without a firewall, all services are exposed to the internet. Deploy WAF + network firewall.",
            })

        if not has_ids:
            recs.append({
                "priority": "MEDIUM",
                "category": "Detection",
                "action": "Implement Intrusion Detection System (IDS/IPS)",
                "detail": "Deploy Snort, Suricata, or commercial SIEM for real-time threat detection.",
            })

        if num_ports > 10:
            recs.append({
                "priority": "MEDIUM",
                "category": "Attack Surface",
                "action": f"Reduce attack surface — close {num_ports - 5} unnecessary ports",
                "detail": "Review all open ports and disable unused services. Apply principle of least privilege.",
            })

        # Always recommend
        recs.append({
            "priority": "MEDIUM",
            "category": "Security Program",
            "action": "Implement regular penetration testing schedule",
            "detail": "Perform quarterly penetration tests and annual red team exercises.",
        })

        recs.append({
            "priority": "LOW",
            "category": "Training",
            "action": "Conduct security awareness training for all employees",
            "detail": "Schedule phishing simulations and security best practices workshops.",
        })

        return recs


# Global model instance
risk_model = RiskPredictionModel()
