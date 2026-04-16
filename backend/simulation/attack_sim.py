"""
ACDRIP+ Attack Simulation Engine
Simulates multi-phase cyber attack chains for threat modeling.
Generates dynamic AI-like explanations linking exact vulnerabilities to attack phases.
"""

import hashlib
import random
from datetime import datetime, timezone

def _seed_from_ip(ip: str) -> int:
    return int(hashlib.md5((ip + "sim_seed").encode()).hexdigest(), 16) % (2**32)

ATTACK_PHASES = [
    {
        "phase": 1,
        "name": "Reconnaissance",
        "description": "Information gathering and target profiling",
        "techniques": [
            {"id": "T1595", "name": "Active Scanning", "detail": "Port scanning and service enumeration using Nmap, Masscan"},
            {"id": "T1592", "name": "Gather Victim Host Info", "detail": "OS fingerprinting, technology stack identification"},
        ],
        "tools": ["Nmap", "Shodan", "Recon-ng"],
        "est_time_min": 15,
        "est_time_max": 60,
        "risk_multiplier": 0.1,
    },
    {
        "phase": 2,
        "name": "Weaponization & Scanning",
        "description": "Vulnerability assessment and exploit preparation",
        "techniques": [
            {"id": "T1190", "name": "Exploit Public-Facing App", "detail": "Identifying exploitable services (CVE matching)"},
            {"id": "T1587", "name": "Develop Capabilities", "detail": "Custom exploit development, payload generation"},
        ],
        "tools": ["Metasploit", "Burp Suite", "OpenVAS"],
        "est_time_min": 30,
        "est_time_max": 120,
        "risk_multiplier": 0.3,
    },
    {
        "phase": 3,
        "name": "Exploitation",
        "description": "Initial access and foothold establishment",
        "techniques": [
            {"id": "T1210", "name": "Exploitation of Remote Services", "detail": "RCE via unpatched services"},
            {"id": "T1059", "name": "Command & Scripting", "detail": "PowerShell, Bash, Python reverse shells"},
        ],
        "tools": ["Metasploit", "Cobalt Strike", "Empire"],
        "est_time_min": 10,
        "est_time_max": 90,
        "risk_multiplier": 0.7,
    },
    {
        "phase": 4,
        "name": "Privilege Escalation",
        "description": "Gaining elevated access and lateral movement",
        "techniques": [
            {"id": "T1068", "name": "Exploitation for Privilege Escalation", "detail": "Kernel exploits, SUID/SGID binaries"},
            {"id": "T1021", "name": "Lateral Movement", "detail": "RDP, SSH, SMB lateral movement to adjacent systems"},
        ],
        "tools": ["Mimikatz", "BloodHound", "CrackMapExec"],
        "est_time_min": 20,
        "est_time_max": 180,
        "risk_multiplier": 0.9,
    },
    {
        "phase": 5,
        "name": "Persistence & Exfiltration",
        "description": "Maintaining access and data extraction",
        "techniques": [
            {"id": "T1547", "name": "Boot or Logon Autostart", "detail": "Registry run keys, cron jobs, systemd services"},
            {"id": "T1041", "name": "Exfiltration Over C2", "detail": "Data theft via encrypted C2 channel"},
        ],
        "tools": ["Cobalt Strike", "Rclone", "Custom backdoors"],
        "est_time_min": 30,
        "est_time_max": 240,
        "risk_multiplier": 1.0,
    },
]

def generate_ai_explanation(phase_id: int, phase_name: str, vulns: list, open_ports: list, rng) -> str:
    """Generates an AI-like specific explanation tying the attack phase to the found vulnerabilities."""
    
    if not vulns and not open_ports:
        return f"During {phase_name}, the attacker relies on generic network sweeping since no clear vectors are known."

    vuln_names = [v.get("cve_id") for v in vulns]
    services = list(set([v.get("service") for v in vulns]))
    
    if phase_id == 1:
        return f"AI Analysis: The attacker actively probes ports {', '.join([str(p) for p in open_ports[:3]])} to discover the running services. By identifying {', '.join(services[:2]) if services else 'open services'}, they profile the exact target surface for potential unpatched exploits."
    
    elif phase_id == 2:
        if vulns:
            return f"AI Analysis: Detecting {', '.join(vuln_names[:2])}, the attacker weaponizes specific exploit payloads targeting the {services[0]} framework. The payload is heavily obfuscated to bypass initial perimeter defenses."
        return f"AI Analysis: Since no major CVEs are exposed, the attacker attempts to brute force or find zero-day misconfigurations on port {open_ports[0] if open_ports else '80'}."

    elif phase_id == 3:
        if vulns:
            critical_vulns = [v for v in vulns if v.get("severity") in ["critical", "high"]]
            if critical_vulns:
                v = critical_vulns[0]
                return f"AI Analysis: Using {v.get('cve_id')}, the attacker achieves direct initial access through the vulnerable {v.get('service')} service on port {v.get('port')}. This RCE grants them a reverse shell to the target environment."
            return f"AI Analysis: Exploiting {vulns[0].get('cve_id')}, the attacker gains a foothold, bypassing authentication on the {services[0]} layer."
        return "AI Analysis: The attacker uses credential stuffing against exposed administrative panels to gain initial access."

    elif phase_id == 4:
        return f"AI Analysis: Having gained initial access, the attacker abuses misconfigured kernel permissions or service accounts related to the {services[0] if services else 'base'} daemon to escalate privileges to SYSTEM/root, granting full control."

    elif phase_id == 5:
        return "AI Analysis: The attacker establishes a persistent C2 beacon using hidden cron jobs or registry keys, and begins encrypting/exfiltrating high-value internal data to an external drop server."
    
    return ""


def simulate_attack(target_ip: str, scan_data: dict = None) -> dict:
    rng = random.Random(_seed_from_ip(target_ip))
    now = datetime.now(timezone.utc)

    open_ports = scan_data.get("open_ports", []) if scan_data else [22, 80, 443]
    vulns = scan_data.get("vulnerabilities", []) if scan_data else []
    risk_score = scan_data.get("risk_score", 50) if scan_data else 50

    num_critical = sum(1 for v in vulns if v.get("severity") == "critical")
    num_high = sum(1 for v in vulns if v.get("severity") == "high")

    base_prob = 0.3
    vuln_bonus = num_critical * 0.12 + num_high * 0.06
    port_bonus = len(open_ports) * 0.02
    attack_success_prob = min(0.98, base_prob + vuln_bonus + port_bonus)

    phases = []
    cumulative_time = 0
    attack_blocked = False

    for phase_def in ATTACK_PHASES:
        if attack_blocked:
            est_time = 0
            success = False
            status = "blocked"
            success_probability = 0
            ai_desc = "Phase blocked due to earlier failure."
        else:
            est_time = rng.randint(phase_def["est_time_min"], phase_def["est_time_max"])
            phase_success_prob = attack_success_prob * phase_def["risk_multiplier"]
            adjusted_prob = min(0.98, phase_success_prob + (risk_score / 100) * 0.4)
            success = rng.random() < adjusted_prob
            success_probability = round(adjusted_prob * 100, 1)

            if not success and phase_def["phase"] >= 3:
                attack_blocked = True
                status = "detected"
            else:
                status = "success" if success else "partial"
                
            ai_desc = generate_ai_explanation(phase_def["phase"], phase_def["name"], vulns, open_ports, rng)

        cumulative_time += est_time

        num_techniques = rng.randint(1, len(phase_def["techniques"]))
        used_techniques = rng.sample(phase_def["techniques"], num_techniques)
        used_tools = rng.sample(phase_def["tools"], min(2, len(phase_def["tools"])))

        phases.append({
            "phase": phase_def["phase"],
            "name": phase_def["name"],
            "description": phase_def["description"],
            "ai_explanation": ai_desc,
            "status": status,
            "success_probability": success_probability,
            "estimated_time_minutes": est_time,
            "cumulative_time_minutes": cumulative_time,
            "techniques": used_techniques,
            "tools_used": used_tools,
        })

    phases_succeeded = sum(1 for p in phases if p["status"] == "success")
    overall_risk = "Critical" if phases_succeeded >= 4 else "High" if phases_succeeded >= 3 else "Medium" if phases_succeeded >= 2 else "Low"

    mitigations = _generate_mitigations(phases, vulns, open_ports)

    return {
        "target_ip": target_ip,
        "simulation_id": f"SIM-{rng.randint(10000, 99999)}",
        "timestamp": str(now),
        "total_phases": len(ATTACK_PHASES),
        "phases_succeeded": phases_succeeded,
        "overall_risk": overall_risk,
        "attack_success_probability": round(attack_success_prob * 100, 1),
        "total_estimated_time_minutes": cumulative_time,
        "phases": phases,
        "attack_path": _generate_attack_path(target_ip, open_ports, vulns),
        "mitigations": mitigations,
    }

def _generate_attack_path(target_ip: str, open_ports: list, vulns: list) -> dict:
    nodes = [
        {"id": "attacker", "label": "Attacker", "type": "threat"},
        {"id": "internet", "label": "Internet", "type": "network"},
        {"id": "firewall", "label": "Firewall", "type": "defense"},
        {"id": "target", "label": target_ip, "type": "target"},
    ]
    edges = [
        {"from": "attacker", "to": "internet", "label": "Recon"},
        {"from": "internet", "to": "firewall", "label": "Probe"},
        {"from": "firewall", "to": "target", "label": "Exploit"},
    ]
    for port in open_ports[:5]:
        svc_id = f"svc_{port}"
        nodes.append({"id": svc_id, "label": f"Port {port}", "type": "service"})
        edges.append({"from": "target", "to": svc_id, "label": "Runs"})

    for v in vulns[:4]:
        vuln_id = f"vuln_{v.get('cve_id', 'unknown')}"
        nodes.append({"id": vuln_id, "label": v.get("cve_id", "CVE-XXXX"), "type": "vulnerability", "desc": v.get('description')})
        svc_port = v.get("port", 80)
        edges.append({"from": f"svc_{svc_port}", "to": vuln_id, "label": v.get("severity", "medium")})

    return {"nodes": nodes, "edges": edges}


def _generate_mitigations(phases: list, vulns: list, open_ports: list) -> list:
    mitigations = []
    
    mitigations.append({
        "phase": "Reconnaissance",
        "action": "Deploy network-level rate limiting and IDS rules.",
        "detail": "Configure firewall to detect and block port scanning patterns.",
        "priority": "HIGH",
    })

    if vulns:
        critical_cves = [v.get("cve_id") for v in vulns if v.get("severity") in ("critical", "high")]
        if critical_cves:
            mitigations.append({
                "phase": "Weaponization",
                "action": "Patch identified critical vulnerabilities immediately.",
                "detail": f"Prioritize patching {', '.join(critical_cves[:2])} to break the exploit chain.",
                "priority": "CRITICAL",
            })

    if any(p["status"] == "success" for p in phases if p["phase"] == 3):
        mitigations.append({
            "phase": "Exploitation",
            "action": "Implement application-level security controls.",
            "detail": "Deploy Web Application Firewall, enable logging, implement input validation.",
            "priority": "CRITICAL",
        })

    if any(p["status"] == "success" for p in phases if p["phase"] >= 4):
        mitigations.append({
            "phase": "Post-Exploitation",
            "action": "Implement zero-trust architecture and network segmentation.",
            "detail": "Deploy micro-segmentation, enforce MFA, implement least-privilege access controls.",
            "priority": "CRITICAL",
        })

    return mitigations
