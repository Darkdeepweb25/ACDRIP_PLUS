"""
ACDRIP+ Nmap Scanner Service
Integrates with python-nmap for network scanning and CVE vulnerability mapping.
Includes a simulation fallback when Nmap is not installed.
"""

import random
import hashlib
import struct
from datetime import datetime, timezone
from typing import Optional

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False
    print("[!] python-nmap not found - running in simulation mode")


# ── Extensive AI-Enhanced CVE Database ──────────
CVE_DATABASE = {
    "ssh": [
        {"cve_id": "CVE-2023-48795", "cvss": 5.9, "severity": "medium", "desc": "SSH Terrapin Attack - prefix truncation vulnerability", "fix": "Update OpenSSH to 9.6+"},
        {"cve_id": "CVE-2023-38408", "cvss": 9.8, "severity": "critical", "desc": "OpenSSH PKCS#11 remote code execution via forwarded agent", "fix": "Upgrade OpenSSH to 9.3p2+"},
        {"cve_id": "CVE-2021-41617", "cvss": 7.0, "severity": "high", "desc": "OpenSSH privilege escalation via AuthorizedKeysCommand", "fix": "Upgrade to OpenSSH 8.8+"},
        {"cve_id": "CVE-2020-15778", "cvss": 7.8, "severity": "high", "desc": "scp command injection leading to RCE", "fix": "Switch to SFTP or limit scp execution"},
        {"cve_id": "CVE-2018-15473", "cvss": 5.3, "severity": "medium", "desc": "OpenSSH Username Enumeration vulnerability", "fix": "Apply patches for version < 7.7"},
    ],
    "http": [
        {"cve_id": "CVE-2024-23897", "cvss": 9.8, "severity": "critical", "desc": "HTTP server arbitrary file read via crafted request", "fix": "Update web server to latest version, apply WAF rules"},
        {"cve_id": "CVE-2023-44487", "cvss": 7.5, "severity": "high", "desc": "HTTP/2 Rapid Reset DDoS Attack", "fix": "Apply vendor patches for HTTP/2 implementation"},
        {"cve_id": "CVE-2023-25690", "cvss": 9.8, "severity": "critical", "desc": "Apache HTTP Server request smuggling vulnerability", "fix": "Upgrade Apache to 2.4.56+"},
        {"cve_id": "CVE-2021-41773", "cvss": 9.8, "severity": "critical", "desc": "Apache HTTP Server Path Traversal & RCE", "fix": "Upgrade Apache to 2.4.51"},
        {"cve_id": "CVE-2021-44228", "cvss": 10.0, "severity": "critical", "desc": "Log4Shell - JNDI lookup arbitrary code execution", "fix": "Update Log4j to > 2.17.1"},
        {"cve_id": "CVE-2019-11043", "cvss": 9.8, "severity": "critical", "desc": "PHP-FPM underflow leading to RCE", "fix": "Update PHP to latest secure release"},
    ],
    "https": [
        {"cve_id": "CVE-2024-0567", "cvss": 7.5, "severity": "high", "desc": "TLS certificate verification bypass", "fix": "Update TLS library and verify certificate chain validation"},
        {"cve_id": "CVE-2023-0286", "cvss": 7.4, "severity": "high", "desc": "OpenSSL X.400 address type confusion", "fix": "Upgrade OpenSSL to 3.0.8+"},
        {"cve_id": "CVE-2014-0160", "cvss": 7.5, "severity": "high", "desc": "Heartbleed - OpenSSL memory leak", "fix": "Upgrade OpenSSL immediately"},
        {"cve_id": "CVE-2016-2107", "cvss": 7.4, "severity": "high", "desc": "Padding Oracle Attack in AES-NI implementation", "fix": "Update OpenSSL software libraries"},
    ],
    "ftp": [
        {"cve_id": "CVE-2023-3604", "cvss": 9.8, "severity": "critical", "desc": "FTP server buffer overflow leading to RCE", "fix": "Disable FTP, switch to SFTP, or patch FTP server"},
        {"cve_id": "CVE-2022-22836", "cvss": 7.5, "severity": "high", "desc": "FTP path traversal — arbitrary file write", "fix": "Update FTP server and restrict write permissions"},
        {"cve_id": "CVE-2015-3306", "cvss": 10.0, "severity": "critical", "desc": "ProFTPD mod_copy Remote Code Execution", "fix": "Upgrade ProFTPD > 1.3.5 or disable mod_copy"},
    ],
    "smtp": [
        {"cve_id": "CVE-2023-42793", "cvss": 9.8, "severity": "critical", "desc": "SMTP authentication bypass allowing relay abuse", "fix": "Update SMTP server and enforce authentication"},
        {"cve_id": "CVE-2021-3449", "cvss": 5.9, "severity": "medium", "desc": "SMTP TLS renegotiation crash", "fix": "Upgrade TLS implementation"},
        {"cve_id": "CVE-2020-28017", "cvss": 8.1, "severity": "high", "desc": "Exim Mail Server Integer Overflow", "fix": "Update Exim > 4.94.2"},
    ],
    "mysql": [
        {"cve_id": "CVE-2024-20960", "cvss": 6.5, "severity": "medium", "desc": "MySQL Server optimizer denial of service", "fix": "Upgrade MySQL to latest patch release"},
        {"cve_id": "CVE-2023-21977", "cvss": 4.9, "severity": "medium", "desc": "MySQL Server information disclosure", "fix": "Apply Oracle Critical Patch Update"},
        {"cve_id": "CVE-2012-2122", "cvss": 5.1, "severity": "medium", "desc": "MySQL Authentication Bypass", "fix": "Update MySQL server immediately"},
    ],
    "rdp": [
        {"cve_id": "CVE-2019-0708", "cvss": 9.8, "severity": "critical", "desc": "BlueKeep - RDP remote code execution (wormable)", "fix": "Patch Windows, enable NLA, restrict RDP access"},
        {"cve_id": "CVE-2023-24905", "cvss": 7.8, "severity": "high", "desc": "RDP client remote code execution", "fix": "Apply latest Windows security updates"},
        {"cve_id": "CVE-2020-0609", "cvss": 9.8, "severity": "critical", "desc": "Remote Desktop Gateway RCE Vulnerability", "fix": "Apply relevant Microsoft patches"},
    ],
    "dns": [
        {"cve_id": "CVE-2023-50387", "cvss": 7.5, "severity": "high", "desc": "KeyTrap — DNSSEC algorithmic complexity attack", "fix": "Update DNS resolver and limit DNSSEC validation"},
        {"cve_id": "CVE-2020-1350", "cvss": 10.0, "severity": "critical", "desc": "SIGRed - Windows DNS Server RCE", "fix": "Patch Windows Server DNS"},
    ],
    "smb": [
        {"cve_id": "CVE-2020-0796", "cvss": 10.0, "severity": "critical", "desc": "SMBGhost — SMBv3 remote code execution", "fix": "Disable SMBv3 compression or apply KB4551762"},
        {"cve_id": "CVE-2017-0144", "cvss": 9.8, "severity": "critical", "desc": "EternalBlue — SMBv1 RCE (WannaCry)", "fix": "Disable SMBv1, apply MS17-010 patch"},
        {"cve_id": "CVE-2024-30064", "cvss": 8.8, "severity": "high", "desc": "SMB remote privilege escalation", "fix": "Apply Microsoft Update Rollup"},
    ],
    "telnet": [
        {"cve_id": "CVE-2022-29154", "cvss": 7.4, "severity": "high", "desc": "Telnet service unencrypted credential exposure", "fix": "Disable Telnet, use SSH instead"},
        {"cve_id": "CVE-2019-10665", "cvss": 8.0, "severity": "high", "desc": "Cisco IOS Telnet remote buffer overflow", "fix": "Apply latest Cisco firmware"},
    ],
    "redis": [
        {"cve_id": "CVE-2023-25155", "cvss": 8.1, "severity": "high", "desc": "Redis unauthenticated RCE via crafted payload", "fix": "Upgrade Redis and block public network access"},
        {"cve_id": "CVE-2022-0543", "cvss": 10.0, "severity": "critical", "desc": "Redis Lua Sandbox Escape", "fix": "Upgrade Redis and sanitize inputs"},
    ],
    "mongodb": [
        {"cve_id": "CVE-2019-2386", "cvss": 6.8, "severity": "medium", "desc": "MongoDB User enumeration via authentication", "fix": "Upgrade MongoDB > 4.2"},
        {"cve_id": "CVE-2023-XXXX", "cvss": 9.1, "severity": "critical", "desc": "MongoDB Default Credential Risk", "fix": "Implement RBAC immediately"},
    ]
}

# Extensive Service Port Map
SERVICE_PORT_MAP = {
    22: "ssh", 80: "http", 443: "https", 21: "ftp", 25: "smtp",
    53: "dns", 110: "pop3", 143: "imap", 3306: "mysql", 5432: "postgresql",
    3389: "rdp", 8080: "http", 8443: "https", 445: "smb", 5900: "vnc",
    139: "smb", 23: "telnet", 993: "imaps", 995: "pop3s",
    6379: "redis", 27017: "mongodb", 5000: "http", 9200: "http",
}


def _seed_from_ip(ip: str) -> int:
    """
    Create a deterministic seed from IP that is highly sensitive to small IP changes.
    Consecutive IPs (e.g. .1 vs .2) will have completely different seeds.
    """
    # Use SHA-256 for better avalanche effect than MD5
    raw = hashlib.sha256((ip + "acdrip_v3_salt").encode()).digest()
    # Combine bytes into a big int for high entropy
    seed = struct.unpack("<Q", raw[:8])[0]
    return seed % (2**32)


def _get_host_profile(rng: random.Random) -> dict:
    """
    Return a realistic host profile that determines port characteristics.
    Different profiles have very different numbers of open ports.
    """
    profiles = [
        # Profile, weight, min_ports, max_ports
        ("minimal_device",    20, 1,  4),
        ("workstation",       20, 2,  6),
        ("web_server",        20, 3,  9),
        ("application_server",15, 6, 14),
        ("database_server",   10, 4,  8),
        ("enterprise_server",  8, 10, 18),
        ("legacy_system",      5, 8, 20),
        ("full_exposure",      2, 15, 22),
    ]
    weights = [p[1] for p in profiles]
    chosen = rng.choices(profiles, weights=weights, k=1)[0]
    return {
        "name": chosen[0],
        "min_ports": chosen[2],
        "max_ports": chosen[3],
    }


def _simulate_scan(target_ip: str) -> dict:
    """Simulate an Nmap scan with realistic per-IP variety."""
    rng = random.Random(_seed_from_ip(target_ip))

    # Assign this IP a host profile — determines port count range
    profile = _get_host_profile(rng)
    num_ports = rng.randint(profile["min_ports"], profile["max_ports"])

    # Shuffle and pick ports — different IPs will pick different subsets
    possible_ports = list(SERVICE_PORT_MAP.keys())
    rng.shuffle(possible_ports)
    open_ports = sorted(possible_ports[:num_ports])

    services = []
    vulnerabilities = []

    for port in open_ports:
        service_name = SERVICE_PORT_MAP.get(port, "unknown")
        version = f"{rng.randint(1, 15)}.{rng.randint(0, 20)}.{rng.randint(0, 50)}"
        services.append({
            "port": port,
            "state": "open",
            "service": service_name,
            "version": version,
            "protocol": "tcp",
        })

        if service_name in CVE_DATABASE:
            cve_list = CVE_DATABASE[service_name]
            # 70% chance a service has at least one vulnerability
            if rng.random() > 0.3:
                num_cves = rng.randint(1, len(cve_list))
                selected = rng.sample(cve_list, num_cves)
                for cve in selected:
                    vulnerabilities.append({
                        "cve_id": cve["cve_id"],
                        "port": port,
                        "service": service_name,
                        "severity": cve["severity"],
                        "cvss_score": cve["cvss"],
                        "description": cve["desc"],
                        "recommendation": cve["fix"],
                    })

    risk_score = calculate_risk_score(open_ports, vulnerabilities)

    os_options = [
        "Linux 5.15 (Ubuntu 22.04)", "Windows Server 2022", "Linux 6.1 (Debian 12)",
        "FreeBSD 13.2", "Windows 10 22H2", "CentOS Stream 9", "Oracle Solaris 11.4",
        "Cisco IOS 15.4", "macOS Ventura 13.5", "Alpine Linux 3.18",
    ]

    return {
        "target_ip": target_ip,
        "open_ports": open_ports,
        "services": services,
        "vulnerabilities": vulnerabilities,
        "risk_score": risk_score,
        "risk_level": get_risk_level(risk_score),
        "os_detection": rng.choice(os_options),
        "scan_method": "simulation",
        "host_profile": profile["name"],
    }


def _real_nmap_scan(target_ip: str) -> dict:
    """Perform an actual Nmap scan using python-nmap."""
    nm = nmap.PortScanner()

    try:
        nm.scan(hosts=target_ip, arguments="-sV -sC --top-ports 1000 -T4")
    except nmap.PortScannerError as e:
        return {"error": f"Nmap scan failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Scan error: {str(e)}"}

    if target_ip not in nm.all_hosts():
        hosts = nm.all_hosts()
        if not hosts:
            return {"error": "No hosts found — target may be unreachable"}
        target_ip = hosts[0]

    host = nm[target_ip]
    open_ports = []
    services = []
    vulnerabilities = []

    for proto in host.all_protocols():
        ports = sorted(host[proto].keys())
        for port in ports:
            port_info = host[proto][port]
            if port_info["state"] == "open":
                open_ports.append(port)
                service_name = port_info.get("name", "unknown")
                version = port_info.get("version", "")
                product = port_info.get("product", "")

                services.append({
                    "port": port,
                    "state": "open",
                    "service": service_name,
                    "version": f"{product} {version}".strip(),
                    "protocol": proto,
                })

                svc_key = service_name.split("-")[0]
                if svc_key in CVE_DATABASE:
                    for cve in CVE_DATABASE[svc_key]:
                        vulnerabilities.append({
                            "cve_id": cve["cve_id"],
                            "port": port,
                            "service": service_name,
                            "severity": cve["severity"],
                            "cvss_score": cve["cvss"],
                            "description": cve["desc"],
                            "recommendation": cve["fix"],
                        })

    risk_score = calculate_risk_score(open_ports, vulnerabilities)

    os_detection = "Unknown"
    if "osmatch" in host and host["osmatch"]:
        os_detection = host["osmatch"][0].get("name", "Unknown")

    return {
        "target_ip": target_ip,
        "open_ports": open_ports,
        "services": services,
        "vulnerabilities": vulnerabilities,
        "risk_score": risk_score,
        "risk_level": get_risk_level(risk_score),
        "os_detection": os_detection,
        "scan_method": "nmap",
    }


def calculate_risk_score(open_ports: list, vulnerabilities: list) -> float:
    """Calculate a risk score (0-100) based on open ports and vulnerabilities."""
    score = 0.0
    score += min(len(open_ports) * 3, 20)

    high_risk_ports = {21, 23, 445, 3389, 139, 25, 6379, 27017}
    for port in open_ports:
        if port in high_risk_ports:
            score += 5

    severity_weights = {"critical": 15, "high": 10, "medium": 5, "low": 2, "info": 1}
    for vuln in vulnerabilities:
        weight = severity_weights.get(vuln.get("severity", "info"), 1)
        score += weight

    if vulnerabilities:
        max_cvss = max(v.get("cvss_score", 0) for v in vulnerabilities)
        score += max_cvss * 1.5

    return min(round(score, 1), 100.0)


def get_risk_level(score: float) -> str:
    if score >= 80: return "Critical"
    elif score >= 60: return "High"
    elif score >= 40: return "Medium"
    elif score >= 20: return "Low"
    return "Info"


def run_scan(target_ip: str) -> dict:
    if NMAP_AVAILABLE:
        try:
            return _real_nmap_scan(target_ip)
        except Exception:
            return _simulate_scan(target_ip)
    return _simulate_scan(target_ip)
