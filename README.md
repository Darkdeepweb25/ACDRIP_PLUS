# 🛡️ ACDRIP+

## Autonomous Cyber Defender, Risk Intelligence & Pre-Breach Simulation Platform

<p align="center">
<b>ACDRIP+</b> is a production-ready cybersecurity SaaS platform that scans networks, detects vulnerabilities, predicts financial risk using AI/ML, simulates attack chains, monitors IPs in real-time, and generates comprehensive PDF reports.
</p>

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Nmap** (optional — runs in simulation mode without it)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
python main.py
```

The platform will be available at: **http://localhost:8000**

### 3. Access the Platform

Open your browser and navigate to `http://localhost:8000`. You'll see the ACDRIP+ landing page.

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build and start
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f acdrip-plus
```

The platform will be available at: **http://localhost:8000**

### Stop

```bash
docker-compose down
```

---

## 🏗️ Architecture

```
ACDRIP+/
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration & settings
│   ├── database.py              # SQLAlchemy database setup
│   ├── models.py                # ORM models (Users, Scans, etc.)
│   ├── auth/
│   │   ├── routes.py            # Auth API (register, login)
│   │   └── utils.py             # JWT & password utilities
│   ├── scanner/
│   │   ├── routes.py            # Scanner API routes
│   │   └── nmap_service.py      # Nmap integration & CVE mapping
│   ├── risk_engine/
│   │   ├── routes.py            # Risk prediction API
│   │   └── ml_model.py          # ML model (GradientBoosting + RF)
│   ├── simulation/
│   │   ├── routes.py            # Attack simulation API
│   │   └── attack_sim.py        # Multi-phase attack chain engine
│   ├── monitoring/
│   │   ├── routes.py            # Monitoring API
│   │   └── alert_service.py     # Background IP monitoring
│   ├── reports/
│   │   ├── routes.py            # Report API
│   │   └── pdf_generator.py     # PDF generation with ReportLab
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── index.html               # Single-page application
│   ├── css/style.css            # Dark cybersecurity theme
│   └── js/app.js                # Frontend application logic
├── Dockerfile                    # Docker image
├── docker-compose.yml            # Docker Compose config
└── README.md                     # This file
```

---

## 📊 Features

### 1. 🔍 Network Scanner
- **Nmap-powered** port scanning and service detection
- **CVE database** with vulnerability mapping
- **Risk scoring** algorithm (0-100)
- OS fingerprinting and service versioning
- Simulation mode for environments without Nmap

### 2. 🧠 AI Risk Prediction Engine
- **GradientBoosting** regression for financial loss prediction
- **RandomForest** classification for risk categorization
- Input: Total assets, vulnerabilities, security controls
- Output: Predicted loss (₹), risk level, attack probability
- AI-driven security recommendations

### 3. ⚔️ Attack Simulation Engine
- **5-phase attack chain** simulation (MITRE ATT&CK mapped)
- Phases: Recon → Scanning → Exploitation → Privilege Escalation → Persistence
- Visual timeline with technique IDs and tools
- Attack path network graph generation
- Tailored mitigation recommendations

### 4. 📡 24/7 Alert Monitoring
- Background IP monitoring threads
- Port change detection
- Risk score change alerts
- Real-time notification system
- Alert history and management

### 5. 📄 PDF Report Generation
- Professional multi-section PDF reports
- Pie charts (severity distribution)
- Vulnerability tables with CVE data
- Financial risk assessment section
- AI recommendations included

---

## 🔐 Security Features

- **JWT Authentication** with configurable expiry
- **bcrypt** password hashing
- **Input validation** on all endpoints (Pydantic)
- **CORS** configuration
- IP address validation to prevent scanning restricted targets

---

## 🔌 API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/health` | GET | No | Health check |
| `/api/auth/register` | POST | No | Register new user |
| `/api/auth/login` | POST | No | Login (returns JWT) |
| `/api/auth/me` | GET | Yes | Get current user profile |
| `/api/scanner/public-scan` | POST | No | Quick scan (landing page) |
| `/api/scanner/scan` | POST | Yes | Full authenticated scan |
| `/api/scanner/history` | GET | Yes | Get scan history |
| `/api/scanner/scan/{id}` | GET | No | Get scan details |
| `/api/risk/predict` | POST | Yes | Risk prediction |
| `/api/risk/quick-predict` | POST | No | Quick risk prediction |
| `/api/simulation/simulate` | POST | Yes | Run attack simulation |
| `/api/monitoring/start` | POST | Yes | Start IP monitoring |
| `/api/monitoring/stop` | POST | Yes | Stop IP monitoring |
| `/api/monitoring/status` | GET | Yes | Get monitor status |
| `/api/monitoring/alerts` | GET | Yes | Get alerts |
| `/api/reports/generate` | POST | Yes | Generate PDF report |
| `/api/reports/download/{id}` | GET | No | Download report PDF |
| `/api/reports/list` | GET | Yes | List user reports |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | FastAPI (Python) |
| Database | SQLite (SQLAlchemy ORM) — swappable to PostgreSQL |
| Authentication | JWT (python-jose) + bcrypt |
| Network Scanning | python-nmap + Nmap |
| ML/AI | scikit-learn (GradientBoosting, RandomForest) |
| PDF Generation | ReportLab |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js |
| Containerization | Docker + Docker Compose |

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `true` | Debug mode |
| `DATABASE_URL` | `sqlite:///./acdrip_plus.db` | Database URL |
| `JWT_SECRET_KEY` | (built-in default) | JWT signing secret |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry (minutes) |
| `NMAP_PATH` | `nmap` | Path to Nmap binary |

---

## 📝 License

This project is provided for educational and authorized security testing purposes only. Always obtain proper authorization before scanning any network.

---

<p align="center">
Built with ❤️ by the <b>ACDRIP+</b> team
</p>
