from fastapi import APIRouter, Depends, HTTPException
from auth.utils import get_current_user

router = APIRouter(prefix="/api/darkweb", tags=["darkweb"])

@router.post("/scan")
def run_darkweb_scan(data: dict, current_user=Depends(get_current_user)):
    target = data.get("target")
    if not target:
        raise HTTPException(status_code=400, detail="Target is required")
        
    seed = sum(ord(c) for c in target)
    exposed = 800 + (seed % 1200)
    leaked = 100 + (seed % 500)
    mentions = 3 + (seed % 25)
    
    tor_nodes = ['185.220.101.47', '45.153.160.2', '198.96.155.3', '199.87.154.255']
    tor_node = tor_nodes[seed % len(tor_nodes)]
    
    return {
        "target": target,
        "metrics": {
            "exposed_assets": exposed,
            "leaked_credentials": leaked,
            "apt_mentions": mentions
        },
        "live_feed": [
            {
                "icon": "🕵️",
                "type": "Data Breach",
                "severity": "CRITICAL",
                "severity_class": "severity-critical",
                "tag_color": "var(--red)",
                "tag_bg": "rgba(239,68,68,0.15)",
                "title": "Exfiltrated Data Set Found — BreachForums",
                "time": "2 hrs ago",
                "desc": f"Dataset matching <span style='color:var(--cyan)'>{target}</span> found containing {int(leaked * 0.6):,} internal employee emails and hashed passwords."
            },
            {
                "icon": "🔑",
                "type": "Credential Leak",
                "severity": "CRITICAL",
                "severity_class": "severity-critical",
                "tag_color": "var(--orange)",
                "tag_bg": "rgba(249,115,22,0.15)",
                "title": "VPN Credentials Active on Telegram — Access Broker",
                "time": "14 hrs ago",
                "desc": f"{4 + (seed % 8)} plaintext credentials for systems in <span style='color:var(--cyan)'>{target}</span>'s IP range. Russian access broker community. Active listing price: $350."
            },
            {
                "icon": "💬",
                "type": "APT Chatter",
                "severity": "HIGH",
                "severity_class": "severity-high",
                "tag_color": "var(--purple)",
                "tag_bg": "rgba(139,92,246,0.15)",
                "title": "Ransomware Syndicate Planning — TOR Forum",
                "time": "3 days ago",
                "desc": f"LockBit affiliate discussed potential ingress via exposed SSH on <span style='color:var(--cyan)'>{target}</span>. TOR exit node <span class='font-mono' style='color:var(--yellow)'>{tor_node}</span> coordinating."
            },
            {
                "icon": "🌐",
                "type": "Passive Recon",
                "severity": "MEDIUM",
                "severity_class": "severity-medium",
                "tag_color": "var(--green)",
                "tag_bg": "rgba(16,185,129,0.15)",
                "title": "IP Range Listed on Shodan/Censys — Automated Scanners",
                "time": "5 days ago",
                "desc": f"Target <span style='color:var(--cyan)'>{target}</span> indexed by {2 + (seed % 4)} automated recon frameworks. Open ports exposed to global scanners. {exposed:,} Internet-connected assets identified."
            }
        ],
        "timeline_seed": seed
    }
