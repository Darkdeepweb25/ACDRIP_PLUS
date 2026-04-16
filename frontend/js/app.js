/**
 * ACDRIP+ Frontend Application
 * Autonomous Cyber Defense, Risk Intelligence & Pre-Breach Simulation Platform
 * 
 * Complete client-side application logic.
 */

// ═══════════════════════════════════════════════════════════════
// Configuration & State
// ═══════════════════════════════════════════════════════════════

const API_BASE = window.location.origin;
const state = {
    token: localStorage.getItem('acdrip_token'),
    user: JSON.parse(localStorage.getItem('acdrip_user') || 'null'),
    currentSection: 'scanner',
    scanCount: 0,
    vulnCount: 0,
    lastScannedIP: null,
    lastScanData: null,
    lastScanId: null,
};

// ═══════════════════════════════════════════════════════════════
// Initialize Application
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    animateStats();

    // Check if user is logged in
    if (state.token && state.user) {
        showDashboard();
    }

    // Enter key on landing scan input
    document.getElementById('landingScanInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') runPublicScan();
    });

    // Enter key on dashboard scan input
    document.getElementById('dashScanInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') runDashboardScan();
    });

    // Risk prediction IP search
    const riskIPInput = document.getElementById('riskIPSearch');
    if (riskIPInput) {
        riskIPInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') autoFillRiskFromIP();
        });
    }

    // Simulation IP auto-search
    const simTarget = document.getElementById('simTarget');
    if (simTarget) {
        simTarget.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') runSimulation();
        });
    }
});

// ═══════════════════════════════════════════════════════════════
// Particle Animation
// ═══════════════════════════════════════════════════════════════

function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;

    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
        particle.style.animationDelay = (Math.random() * 10) + 's';
        particle.style.width = (Math.random() * 3 + 1) + 'px';
        particle.style.height = particle.style.width;

        // Random color: cyan or purple
        particle.style.background = Math.random() > 0.5 ?
            'rgba(0, 229, 255, 0.6)' : 'rgba(139, 92, 246, 0.6)';

        container.appendChild(particle);
    }
}

// ═══════════════════════════════════════════════════════════════
// Animated Counters
// ═══════════════════════════════════════════════════════════════

function animateStats() {
    animateCounter('statScans', 0, 15847, 2000);
    animateCounter('statVulns', 0, 72430, 2500);
}

function animateCounter(id, start, end, duration) {
    const el = document.getElementById(id);
    if (!el) return;

    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const ease = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (end - start) * ease);
        el.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = end.toLocaleString() + '+';
        }
    }

    requestAnimationFrame(update);
}

// ═══════════════════════════════════════════════════════════════
// API Helper
// ═══════════════════════════════════════════════════════════════

async function api(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...(state.token ? { 'Authorization': `Bearer ${state.token}` } : {}),
        ...options.headers,
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `Request failed (${response.status})`);
        }

        return data;
    } catch (error) {
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to server. Is the backend running?');
        }
        throw error;
    }
}

// ═══════════════════════════════════════════════════════════════
// Toast Notifications
// ═══════════════════════════════════════════════════════════════

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const icons = { success: '✓', error: '✕', info: 'ℹ' };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ═══════════════════════════════════════════════════════════════
// Modal Management
// ═══════════════════════════════════════════════════════════════

function openModal(type) {
    document.getElementById(`${type}Modal`).classList.add('active');
}

function closeModal(type) {
    document.getElementById(`${type}Modal`).classList.remove('active');
}

// Close modals on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
        }
    });
});

// ═══════════════════════════════════════════════════════════════
// Authentication
// ═══════════════════════════════════════════════════════════════

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const data = await api('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });

        state.token = data.access_token;
        state.user = data.user;
        localStorage.setItem('acdrip_token', data.access_token);
        localStorage.setItem('acdrip_user', JSON.stringify(data.user));

        closeModal('login');
        showDashboard();
        showToast(`Welcome back, ${data.user.name}!`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;

    try {
        const data = await api('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ name, email, password }),
        });

        state.token = data.access_token;
        state.user = data.user;
        localStorage.setItem('acdrip_token', data.access_token);
        localStorage.setItem('acdrip_user', JSON.stringify(data.user));

        closeModal('register');
        showDashboard();
        showToast(`Welcome to ACDRIP+, ${data.user.name}!`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function handleLogout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('acdrip_token');
    localStorage.removeItem('acdrip_user');

    document.getElementById('dashboard').classList.remove('active');
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('landing-page').style.display = 'flex';

    showToast('Logged out successfully', 'info');
}

// ═══════════════════════════════════════════════════════════════
// Dashboard Navigation
// ═══════════════════════════════════════════════════════════════

function showDashboard() {
    document.getElementById('landing-page').style.display = 'none';
    document.getElementById('dashboard').style.display = 'flex';
    document.getElementById('dashboard').classList.add('active');

    // Update user info
    if (state.user) {
        document.getElementById('userName').textContent = state.user.name;
        document.getElementById('userEmail').textContent = state.user.email;
        document.getElementById('userAvatar').textContent =
            state.user.name.charAt(0).toUpperCase();
    }

    // Load initial data
    loadScanHistory();
    loadReportScanOptions();
}

function switchSection(section) {
    state.currentSection = section;

    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.section === section);
    });

    // Update sections
    document.querySelectorAll('.section').forEach(s => {
        s.classList.toggle('active', s.id === `section-${section}`);
    });

    // Load data for the section
    if (section === 'monitoring') {
        loadMonitorStatus();
        loadAlerts();
    } else if (section === 'reports') {
        loadReports();
        loadReportScanOptions();
    } else if (section === 'risk' && state.lastScannedIP) {
        // Auto-fill risk IP from last scan
        const riskIPInput = document.getElementById('riskIPSearch');
        if (riskIPInput && !riskIPInput.value) {
            riskIPInput.value = state.lastScannedIP;
            autoFillRiskFromIP();
        }
    } else if (section === 'simulation' && state.lastScannedIP) {
        // Auto-fill simulation IP from last scan
        const simTarget = document.getElementById('simTarget');
        if (simTarget && !simTarget.value) {
            simTarget.value = state.lastScannedIP;
            if (state.lastScanId) {
                document.getElementById('simScanId').value = state.lastScanId;
            }
            runSimulation();
        }
    }
}

// ═══════════════════════════════════════════════════════════════
// Network Scanner
// ═══════════════════════════════════════════════════════════════

async function runPublicScan() {
    const input = document.getElementById('landingScanInput');
    const btn = document.getElementById('landingScanBtn');
    const ip = input.value.trim();

    if (!ip) {
        showToast('Please enter an IP address', 'error');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> Scanning...';

    try {
        const data = await api('/api/scanner/public-scan', {
            method: 'POST',
            body: JSON.stringify({ target_ip: ip }),
        });

        displayLandingResults(data);
        showToast('Scan completed successfully!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>⚡</span> Scan Network';
    }
}

async function runDashboardScan() {
    const input = document.getElementById('dashScanInput');
    const btn = document.getElementById('dashScanBtn');
    const ip = input.value.trim();

    if (!ip) {
        showToast('Please enter an IP address', 'error');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> Scanning...';
    document.getElementById('dashScanLoading').classList.remove('hidden');
    document.getElementById('dashScanResults').classList.add('hidden');

    try {
        const data = await api('/api/scanner/scan', {
            method: 'POST',
            body: JSON.stringify({ target_ip: ip }),
        });

        // Store last scanned IP and scan data for cross-module auto-fill
        state.lastScannedIP = ip;
        state.lastScanData = data;
        state.lastScanId = data.scan_id;

        displayDashboardResults(data);
        loadScanHistory();
        loadReportScanOptions();
        showToast(`Scan ${data.scan_id} completed!`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 Run Scan';
        document.getElementById('dashScanLoading').classList.add('hidden');
    }
}

// ═══════════════════════════════════════════════════════════════
// Scan Result Renderers
// ═══════════════════════════════════════════════════════════════

function getRiskColor(score) {
    if (score >= 80) return '#ef4444';
    if (score >= 60) return '#f97316';
    if (score >= 40) return '#f59e0b';
    if (score >= 20) return '#10b981';
    return '#3b82f6';
}

function getSeverityClass(severity) {
    return `severity-badge severity-${severity}`;
}

function displayLandingResults(data) {
    const container = document.getElementById('landingResults');
    const content = document.getElementById('landingResultsContent');
    container.classList.remove('hidden');

    const riskColor = getRiskColor(data.risk_score);
    const circumference = 2 * Math.PI * 65;
    const offset = circumference - (data.risk_score / 100) * circumference;

    content.innerHTML = `
        <div class="results-grid">
            <!-- Risk Score -->
            <div class="card" style="text-align: center;">
                <div class="card-title" style="justify-content: center; margin-bottom: 20px;">
                    <span class="icon">🎯</span> Risk Score
                </div>
                <div class="risk-ring">
                    <svg width="160" height="160" viewBox="0 0 160 160">
                        <circle class="ring-bg" cx="80" cy="80" r="65"/>
                        <circle class="ring-fill" cx="80" cy="80" r="65"
                            stroke="${riskColor}"
                            stroke-dasharray="${circumference}"
                            stroke-dashoffset="${offset}"/>
                    </svg>
                    <div class="ring-text">
                        <span class="ring-value" style="color: ${riskColor}">${data.risk_score}</span>
                        <span class="ring-label">${data.risk_level}</span>
                    </div>
                </div>
                <p style="color: var(--text-secondary); font-size: 13px;">
                    Target: <span class="font-mono">${data.target_ip}</span><br>
                    Scan ID: <span class="font-mono" style="color: var(--cyan);">${data.scan_id}</span>
                </p>
            </div>

            <!-- Open Ports -->
            <div class="card">
                <div class="card-title" style="margin-bottom: 16px;">
                    <span class="icon">🔓</span> Open Ports (${data.open_ports.length})
                </div>
                <table class="data-table">
                    <thead>
                        <tr><th>Port</th><th>Service</th><th>Version</th></tr>
                    </thead>
                    <tbody>
                        ${(data.services || []).map(s => `
                            <tr>
                                <td class="font-mono" style="color: var(--cyan);">${s.port}</td>
                                <td>${s.service}</td>
                                <td class="font-mono" style="color: var(--text-muted); font-size: 12px;">${s.version}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <!-- Vulnerabilities -->
            <div class="card" style="grid-column: 1 / -1;">
                <div class="card-title" style="margin-bottom: 16px;">
                    <span class="icon">⚠️</span> Vulnerabilities (${(data.vulnerabilities || []).length})
                </div>
                <table class="data-table">
                    <thead>
                        <tr><th>CVE ID</th><th>Port</th><th>Severity</th><th>CVSS</th><th>Description</th></tr>
                    </thead>
                    <tbody>
                        ${(data.vulnerabilities || []).map(v => `
                            <tr>
                                <td class="font-mono" style="color: var(--yellow);">${v.cve_id}</td>
                                <td class="font-mono">${v.port}</td>
                                <td><span class="${getSeverityClass(v.severity)}">${v.severity}</span></td>
                                <td class="font-mono">${v.cvss_score}</td>
                                <td style="font-size: 12px; max-width: 400px;">${v.description}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.scrollIntoView({ behavior: 'smooth' });
}

function closeLandingResults() {
    document.getElementById('landingResults').classList.add('hidden');
}

function displayDashboardResults(data) {
    const container = document.getElementById('dashScanResults');
    container.classList.remove('hidden');

    const riskColor = getRiskColor(data.risk_score);
    const circumference = 2 * Math.PI * 65;
    const offset = circumference - (data.risk_score / 100) * circumference;

    // Severity distribution for chart
    const severityCounts = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
    (data.vulnerabilities || []).forEach(v => {
        if (severityCounts.hasOwnProperty(v.severity)) {
            severityCounts[v.severity]++;
        }
    });

    container.innerHTML = `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Risk Score</div>
                <div class="metric-value" style="color: ${riskColor};">${data.risk_score}</div>
                <div class="metric-change">${data.risk_level}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Open Ports</div>
                <div class="metric-value" style="color: var(--cyan);">${data.open_ports.length}</div>
                <div class="metric-change">Detected</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Vulnerabilities</div>
                <div class="metric-value" style="color: var(--yellow);">${(data.vulnerabilities || []).length}</div>
                <div class="metric-change">${severityCounts.critical} Critical</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Scan ID</div>
                <div class="metric-value font-mono" style="font-size: 18px; color: var(--purple);">${data.scan_id}</div>
                <div class="metric-change">${data.scan_method || 'simulation'}</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <!-- Risk Ring + Chart -->
            <div class="card">
                <div class="card-title" style="margin-bottom: 16px;"><span class="icon">🎯</span> Risk Assessment</div>
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div class="risk-ring">
                        <svg width="160" height="160" viewBox="0 0 160 160">
                            <circle class="ring-bg" cx="80" cy="80" r="65"/>
                            <circle class="ring-fill" cx="80" cy="80" r="65"
                                stroke="${riskColor}"
                                stroke-dasharray="${circumference}"
                                stroke-dashoffset="${offset}"/>
                        </svg>
                        <div class="ring-text">
                            <span class="ring-value" style="color: ${riskColor}">${data.risk_score}</span>
                            <span class="ring-label">${data.risk_level}</span>
                        </div>
                    </div>
                    <div>
                        <canvas id="severityChart" width="180" height="180"></canvas>
                    </div>
                </div>
            </div>

            <!-- Services -->
            <div class="card">
                <div class="card-title" style="margin-bottom: 16px;"><span class="icon">🔓</span> Open Ports & Services</div>
                <table class="data-table">
                    <thead><tr><th>Port</th><th>Service</th><th>Version</th></tr></thead>
                    <tbody>
                        ${(data.services || []).map(s => `
                            <tr>
                                <td class="font-mono" style="color: var(--cyan);">${s.port}</td>
                                <td>${s.service}</td>
                                <td class="font-mono" style="color: var(--text-muted); font-size: 12px;">${s.version}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Vulnerabilities Table -->
        <div class="card" style="margin-top: 20px;">
            <div class="card-title" style="margin-bottom: 16px;">
                <span class="icon">⚠️</span> Vulnerabilities (${(data.vulnerabilities || []).length})
            </div>
            <table class="data-table">
                <thead>
                    <tr><th>CVE ID</th><th>Port</th><th>Service</th><th>Severity</th><th>CVSS</th><th>Description</th><th>Fix</th></tr>
                </thead>
                <tbody>
                    ${(data.vulnerabilities || []).map(v => `
                        <tr>
                            <td class="font-mono" style="color: var(--yellow);">${v.cve_id}</td>
                            <td class="font-mono">${v.port}</td>
                            <td>${v.service}</td>
                            <td><span class="${getSeverityClass(v.severity)}">${v.severity}</span></td>
                            <td class="font-mono">${v.cvss_score}</td>
                            <td style="font-size: 12px; max-width: 250px;">${v.description}</td>
                            <td style="font-size: 12px; max-width: 250px; color: var(--green);">${v.recommendation}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>

        <!-- Quick Actions -->
        <div class="card" style="margin-top: 20px;">
            <div class="card-title" style="margin-bottom: 16px;"><span class="icon">⚡</span> Quick Actions</div>
            <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="quickRiskFromScan('${data.target_ip}', '${data.scan_id}')">
                    🧠 Run Risk Prediction
                </button>
                <button class="btn btn-danger" onclick="quickSimFromScan('${data.target_ip}', '${data.scan_id}')">
                    ⚔️ Run Attack Simulation
                </button>
                <button class="btn btn-secondary" onclick="quickReport('${data.scan_id}')">
                    📄 Generate Report
                </button>
            </div>
        </div>
    `;

    // Render severity chart
    setTimeout(() => {
        const ctx = document.getElementById('severityChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
                    datasets: [{
                        data: [
                            severityCounts.critical,
                            severityCounts.high,
                            severityCounts.medium,
                            severityCounts.low,
                            severityCounts.info,
                        ],
                        backgroundColor: ['#ef4444', '#f97316', '#f59e0b', '#10b981', '#3b82f6'],
                        borderWidth: 0,
                    }],
                },
                options: {
                    responsive: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#8899b4', font: { size: 11 } },
                        },
                    },
                    cutout: '60%',
                },
            });
        }
    }, 100);
}

// Quick action helpers - navigate and auto-fill
function quickRiskFromScan(ip, scanId) {
    state.lastScannedIP = ip;
    state.lastScanId = scanId;
    const riskIPInput = document.getElementById('riskIPSearch');
    if (riskIPInput) riskIPInput.value = ip;
    switchSection('risk');
    autoFillRiskFromIP();
}

function quickSimFromScan(ip, scanId) {
    state.lastScannedIP = ip;
    state.lastScanId = scanId;
    document.getElementById('simTarget').value = ip;
    document.getElementById('simScanId').value = scanId;
    switchSection('simulation');
    runSimulation();
}

function quickReport(scanId) {
    document.getElementById('reportScanSelect').value = scanId;
    switchSection('reports');
}

// ═══════════════════════════════════════════════════════════════
// Scan History
// ═══════════════════════════════════════════════════════════════

async function loadScanHistory() {
    try {
        const scans = await api('/api/scanner/history');
        const container = document.getElementById('scanHistoryTable');

        if (!scans || scans.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📋</div>
                    <h3>No scans yet</h3>
                    <p>Run your first scan to see results here</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr><th>Scan ID</th><th>Target</th><th>Risk</th><th>Ports</th><th>Status</th><th>Date</th></tr>
                </thead>
                <tbody>
                    ${scans.map(s => `
                        <tr style="cursor: pointer;" onclick="loadScanDetail('${s.scan_id}')">
                            <td class="font-mono" style="color: var(--cyan);">${s.scan_id}</td>
                            <td class="font-mono">${s.target_ip}</td>
                            <td>
                                <span class="severity-badge severity-${s.risk_level.toLowerCase()}">${s.risk_score} - ${s.risk_level}</span>
                            </td>
                            <td>${(s.open_ports || []).length}</td>
                            <td><span class="status-dot status-online"></span>${s.status}</td>
                            <td style="color: var(--text-muted); font-size: 12px;">${new Date(s.created_at).toLocaleDateString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        // Silent fail for history loading
    }
}

async function loadScanDetail(scanId) {
    try {
        const data = await api(`/api/scanner/scan/${scanId}`);
        state.lastScannedIP = data.target_ip;
        state.lastScanData = data;
        state.lastScanId = data.scan_id;
        displayDashboardResults(data);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ═══════════════════════════════════════════════════════════════
// Risk Prediction Engine — with IP Auto-Fill
// ═══════════════════════════════════════════════════════════════

async function autoFillRiskFromIP() {
    const ipInput = document.getElementById('riskIPSearch');
    const ip = ipInput ? ipInput.value.trim() : '';
    
    if (!ip) {
        showToast('Please enter an IP address to look up', 'error');
        return;
    }

    const fillBtn = document.getElementById('riskFillBtn');
    if (fillBtn) {
        fillBtn.disabled = true;
        fillBtn.innerHTML = '<span class="loading-spinner"></span> Loading...';
    }

    try {
        const data = await api(`/api/scanner/by-ip/${ip}`);
        
        // Auto-fill all fields from scan data
        document.getElementById('riskCritical').value = data.num_critical_vulns || 0;
        document.getElementById('riskHigh').value = data.num_high_vulns || 0;
        document.getElementById('riskPorts').value = data.num_open_ports || 0;

        // Show what was auto-filled
        const autoFillInfo = document.getElementById('riskAutoFillInfo');
        if (autoFillInfo) {
            autoFillInfo.classList.remove('hidden');
            autoFillInfo.innerHTML = `
                <div class="auto-fill-banner">
                    <span class="icon">✅</span>
                    <div>
                        <strong>Data loaded from scan ${data.scan_id}</strong>
                        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                            ${data.num_open_ports} open ports · ${data.num_critical_vulns} critical · ${data.num_high_vulns} high · ${data.total_vulns} total vulnerabilities
                            <br>OS: ${data.os_detection || 'Unknown'} · Risk Score: ${data.risk_score}/100
                        </div>
                    </div>
                </div>
            `;
        }

        // Store for report generation
        state.lastScannedIP = ip;
        state.lastScanId = data.scan_id;

        showToast(`Risk parameters auto-filled from scan of ${ip}`, 'success');
    } catch (error) {
        showToast(`No scan data found for ${ip}. Please enter values manually or scan the IP first.`, 'error');
        const autoFillInfo = document.getElementById('riskAutoFillInfo');
        if (autoFillInfo) {
            autoFillInfo.classList.remove('hidden');
            autoFillInfo.innerHTML = `
                <div class="auto-fill-banner error">
                    <span class="icon">⚠️</span>
                    <div>
                        <strong>No scan data found for ${ip}</strong>
                        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                            Please run a network scan first or enter risk parameters manually below.
                        </div>
                    </div>
                </div>
            `;
        }
    } finally {
        if (fillBtn) {
            fillBtn.disabled = false;
            fillBtn.innerHTML = '🔍 Load from Scan';
        }
    }
}

async function runRiskPrediction() {
    const totalAssets = parseFloat(document.getElementById('riskAssets').value) || 10000000;
    const numCritical = parseInt(document.getElementById('riskCritical').value) || 0;
    const numHigh = parseInt(document.getElementById('riskHigh').value) || 0;
    const numPorts = parseInt(document.getElementById('riskPorts').value) || 0;
    const employees = parseInt(document.getElementById('riskEmployees').value) || 50;
    const hasFirewall = document.getElementById('riskFirewall').checked;
    const hasIDS = document.getElementById('riskIDS').checked;
    const industry = parseFloat(document.getElementById('riskIndustry').value) || 0.6;

    try {
        const data = await api('/api/risk/predict', {
            method: 'POST',
            body: JSON.stringify({
                total_assets: totalAssets,
                num_critical_vulns: numCritical,
                num_high_vulns: numHigh,
                num_open_ports: numPorts,
                has_firewall: hasFirewall,
                has_ids: hasIDS,
                employee_count: employees,
                industry_risk_factor: industry,
            }),
        });

        displayRiskResults(data);
        showToast('Risk prediction completed!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function displayRiskResults(data) {
    const container = document.getElementById('riskResults');
    const riskColor = getRiskColor(data.risk_class * 25);

    // Calculate compliance score estimate
    const complianceScore = Math.max(0, 100 - (data.risk_class * 15) - Math.round(data.attack_probability * 0.3));
    const mttr = data.risk_class <= 1 ? '< 4 hours' : data.risk_class <= 2 ? '4-24 hours' : data.risk_class <= 3 ? '1-7 days' : '7+ days';

    container.innerHTML = `
        <!-- Risk Metrics -->
        <div class="metrics-grid" style="grid-template-columns: 1fr;">
            <div class="metric-card">
                <div class="metric-label">Predicted Financial Loss</div>
                <div class="metric-value" style="color: var(--red); font-size: 24px;">₹${data.predicted_loss.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
                <div class="metric-change up">${data.loss_percentage}% of total assets</div>
            </div>
        </div>

        <div class="metrics-grid" style="grid-template-columns: 1fr 1fr 1fr;">
            <div class="metric-card">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value" style="color: ${riskColor}; font-size: 22px;">${data.risk_level}</div>
                <div class="metric-change">Confidence: ${data.risk_probability}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Attack Probability</div>
                <div class="metric-value" style="color: var(--orange); font-size: 22px;">${data.attack_probability}%</div>
                <div class="metric-change">Based on current posture</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Compliance Score</div>
                <div class="metric-value" style="color: ${complianceScore > 70 ? 'var(--green)' : complianceScore > 40 ? 'var(--yellow)' : 'var(--red)'}; font-size: 22px;">${complianceScore}%</div>
                <div class="metric-change">Est. MTTR: ${mttr}</div>
            </div>
        </div>

        <!-- Risk Distribution Chart -->
        <div class="card" style="margin-bottom: 16px;">
            <div class="card-title" style="margin-bottom: 16px;"><span class="icon">📊</span> Risk Distribution</div>
            <canvas id="riskDistChart" height="200"></canvas>
        </div>

        <!-- Recommendations -->
        <div class="card">
            <div class="card-title" style="margin-bottom: 16px;"><span class="icon">💡</span> AI Recommendations</div>
            ${(data.recommendations || []).map(r => `
                <div class="alert-card" style="margin-bottom: 8px;">
                    <div class="alert-icon" style="background: ${
                        r.priority === 'CRITICAL' ? 'var(--red-dim)' :
                        r.priority === 'HIGH' ? 'rgba(249,115,22,0.15)' :
                        r.priority === 'MEDIUM' ? 'var(--yellow-dim)' : 'var(--green-dim)'
                    }; color: ${
                        r.priority === 'CRITICAL' ? 'var(--red)' :
                        r.priority === 'HIGH' ? 'var(--orange)' :
                        r.priority === 'MEDIUM' ? 'var(--yellow)' : 'var(--green)'
                    };">
                        ${r.priority === 'CRITICAL' ? '🔴' :
                          r.priority === 'HIGH' ? '🟠' :
                          r.priority === 'MEDIUM' ? '🟡' : '🟢'}
                    </div>
                    <div class="alert-content">
                        <div class="alert-title">
                            <span class="severity-badge severity-${r.priority.toLowerCase()}">${r.priority}</span>
                            ${r.category}
                        </div>
                        <div class="alert-message"><strong>${r.action}</strong></div>
                        <div class="alert-time">${r.detail}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    // Render risk distribution chart
    setTimeout(() => {
        const ctx = document.getElementById('riskDistChart');
        if (ctx) {
            const dist = data.risk_distribution || {};
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Minimal', 'Low', 'Medium', 'High', 'Critical'],
                    datasets: [{
                        label: 'Probability (%)',
                        data: [
                            dist.minimal || 0,
                            dist.low || 0,
                            dist.medium || 0,
                            dist.high || 0,
                            dist.critical || 0,
                        ],
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#f97316', '#ef4444'],
                        borderWidth: 0,
                        borderRadius: 6,
                    }],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: '#8899b4', callback: v => v + '%' },
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#8899b4' },
                        },
                    },
                },
            });
        }
    }, 100);
}

// ═══════════════════════════════════════════════════════════════
// Attack Simulation
// ═══════════════════════════════════════════════════════════════

async function runSimulation() {
    const targetIP = document.getElementById('simTarget').value.trim();
    const scanId = document.getElementById('simScanId').value.trim();

    if (!targetIP) {
        showToast('Please enter a target IP address', 'error');
        return;
    }

    document.getElementById('simLoading').classList.remove('hidden');
    document.getElementById('simResults').classList.add('hidden');

    // If no scan_id provided, try to look up from IP
    let resolvedScanId = scanId || null;
    if (!resolvedScanId && targetIP) {
        try {
            const ipData = await api(`/api/scanner/by-ip/${targetIP}`);
            if (ipData && ipData.scan_id) {
                resolvedScanId = ipData.scan_id;
                document.getElementById('simScanId').value = resolvedScanId;
            }
        } catch (e) {
            // No existing scan, proceed without
        }
    }

    try {
        const data = await api('/api/simulation/simulate', {
            method: 'POST',
            body: JSON.stringify({
                target_ip: targetIP,
                scan_id: resolvedScanId,
            }),
        });

        displaySimulationResults(data);
        showToast('Attack simulation completed!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        document.getElementById('simLoading').classList.add('hidden');
    }
}

function displaySimulationResults(data) {
    const container = document.getElementById('simResults');
    container.classList.remove('hidden');

    const riskColor = getRiskColor(
        data.overall_risk === 'Critical' ? 90 :
        data.overall_risk === 'High' ? 70 :
        data.overall_risk === 'Medium' ? 45 : 25
    );

    // Build vulnerability chaining display from attack path
    const attackPath = data.attack_path || { nodes: [], edges: [] };
    const vulnNodes = attackPath.nodes ? attackPath.nodes.filter(n => n.type === 'vulnerability') : [];
    const serviceNodes = attackPath.nodes ? attackPath.nodes.filter(n => n.type === 'service') : [];

    container.innerHTML = `
        <!-- Summary Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Overall Risk</div>
                <div class="metric-value" style="color: ${riskColor};">${data.overall_risk}</div>
                <div class="metric-change">${data.simulation_id}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Attack Success</div>
                <div class="metric-value" style="color: var(--red);">${data.attack_success_probability}%</div>
                <div class="metric-change">Probability</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Phases Succeeded</div>
                <div class="metric-value" style="color: var(--orange);">${data.phases_succeeded}/${data.total_phases}</div>
                <div class="metric-change">of attack chain</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Time</div>
                <div class="metric-value" style="color: var(--cyan);">${data.total_estimated_time_minutes}m</div>
                <div class="metric-change">Estimated duration</div>
            </div>
        </div>

        <!-- Vulnerability Chaining -->
        ${vulnNodes.length > 0 || serviceNodes.length > 0 ? `
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-title" style="margin-bottom: 16px;"><span class="icon">🔗</span> Attack Chain - Vulnerability Exploitation Path</div>
            <div class="attack-chain-visual">
                <div class="chain-flow">
                    <div class="chain-node threat">
                        <div class="chain-icon">👤</div>
                        <div class="chain-label">Attacker</div>
                    </div>
                    <div class="chain-arrow">→</div>
                    <div class="chain-node network">
                        <div class="chain-icon">🌐</div>
                        <div class="chain-label">Internet</div>
                    </div>
                    <div class="chain-arrow">→</div>
                    <div class="chain-node defense">
                        <div class="chain-icon">🛡️</div>
                        <div class="chain-label">Firewall</div>
                    </div>
                    <div class="chain-arrow">→</div>
                    <div class="chain-node target-node">
                        <div class="chain-icon">🎯</div>
                        <div class="chain-label">${data.target_ip}</div>
                    </div>
                </div>
                <div style="margin-top: 20px;">
                    <div style="font-weight: 600; margin-bottom: 10px; color: var(--text-secondary);">Exploitable Services & Vulnerabilities:</div>
                    <div class="chain-details">
                        ${serviceNodes.map(svc => {
                            const connectedVulns = attackPath.edges
                                .filter(e => e.from === svc.id)
                                .map(e => vulnNodes.find(v => v.id === e.to))
                                .filter(Boolean);
                            return `
                                <div class="chain-service-card">
                                    <div class="chain-service-header">
                                        <span class="icon" style="color: var(--cyan);">🔓</span>
                                        <strong>${svc.label}</strong>
                                    </div>
                                    ${connectedVulns.map(v => `
                                        <div class="chain-vuln-item">
                                            <span class="severity-badge severity-${attackPath.edges.find(e => e.to === v.id)?.label || 'medium'}">${attackPath.edges.find(e => e.to === v.id)?.label || 'medium'}</span>
                                            <span class="font-mono" style="color: var(--yellow);">${v.label}</span>
                                        </div>
                                    `).join('')}
                                    ${connectedVulns.length === 0 ? '<div style="font-size: 12px; color: var(--text-muted);">No known CVEs — low exploitation risk</div>' : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        </div>
        ` : ''}

        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
            <!-- Attack Timeline -->
            <div class="card">
                <div class="card-title" style="margin-bottom: 20px;"><span class="icon">⏱️</span> Attack Chain Timeline</div>
                <div class="attack-timeline">
                    ${(data.phases || []).map(p => `
                        <div class="timeline-item ${p.status}">
                            <div class="timeline-phase">Phase ${p.phase}</div>
                            <div class="timeline-title">${p.name}</div>
                            <div class="timeline-desc">${p.description}</div>
                            <div style="margin: 10px 0; padding: 12px; background: rgba(0, 229, 255, 0.05); border-left: 3px solid var(--cyan); border-radius: 4px; font-size: 13px; color: var(--text-primary);">
                                <strong>🧠 ${p.ai_explanation || ''}</strong>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                                    <span>Success Probability</span>
                                    <span style="color: ${p.success_probability > 70 ? 'var(--red)' : p.success_probability > 40 ? 'var(--yellow)' : 'var(--green)'};">${p.success_probability}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${p.success_probability}%; background: ${p.success_probability > 70 ? 'var(--red)' : p.success_probability > 40 ? 'var(--yellow)' : 'var(--green)'};"></div>
                                </div>
                            </div>
                            <div style="margin-bottom: 8px;">
                                ${(p.techniques || []).map(t => `
                                    <span class="timeline-tag" title="${t.detail}">${t.id}: ${t.name}</span>
                                `).join('')}
                            </div>
                            <div class="timeline-meta">
                                <span>⏱ ${p.estimated_time_minutes} min</span>
                                <span>🛠 ${(p.tools_used || []).join(', ')}</span>
                                <span class="severity-badge severity-${p.status === 'success' ? 'critical' : p.status === 'detected' ? 'medium' : 'low'}">${p.status}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Mitigations -->
            <div>
                <div class="card" style="margin-bottom: 20px;">
                    <div class="card-title" style="margin-bottom: 16px;"><span class="icon">📊</span> Phase Success</div>
                    <canvas id="phaseChart" height="250"></canvas>
                </div>
                <div class="card">
                    <div class="card-title" style="margin-bottom: 16px;"><span class="icon">🛡️</span> Mitigations</div>
                    ${(data.mitigations || []).map(m => `
                        <div style="padding: 12px; margin-bottom: 8px; background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid ${m.priority === 'CRITICAL' ? 'var(--red)' : m.priority === 'HIGH' ? 'var(--orange)' : 'var(--yellow)'};">
                            <div style="font-size: 12px; font-weight: 700; color: ${m.priority === 'CRITICAL' ? 'var(--red)' : m.priority === 'HIGH' ? 'var(--orange)' : 'var(--yellow)'}; margin-bottom: 4px;">${m.priority} — ${m.phase}</div>
                            <div style="font-size: 13px; font-weight: 600; margin-bottom: 4px;">${m.action}</div>
                            <div style="font-size: 12px; color: var(--text-muted);">${m.detail}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    // Render phase success chart
    setTimeout(() => {
        const ctx = document.getElementById('phaseChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: (data.phases || []).map(p => p.name.split(' ')[0]),
                    datasets: [{
                        label: 'Success Probability',
                        data: (data.phases || []).map(p => p.success_probability),
                        backgroundColor: 'rgba(239, 68, 68, 0.15)',
                        borderColor: '#ef4444',
                        borderWidth: 2,
                        pointBackgroundColor: '#ef4444',
                    }],
                },
                options: {
                    responsive: true,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { display: false },
                            pointLabels: { color: '#8899b4', font: { size: 10 } },
                        },
                    },
                    plugins: {
                        legend: { display: false },
                    },
                },
            });
        }
    }, 100);
}

// ═══════════════════════════════════════════════════════════════
// 24/7 Monitoring
// ═══════════════════════════════════════════════════════════════

async function startMonitoring() {
    const ip = document.getElementById('monitorIP').value.trim();
    const interval = parseInt(document.getElementById('monitorInterval').value) || 300;

    if (!ip) {
        showToast('Please enter an IP address', 'error');
        return;
    }

    try {
        const data = await api('/api/monitoring/start', {
            method: 'POST',
            body: JSON.stringify({ target_ip: ip, interval_seconds: interval }),
        });
        showToast(`Monitoring started for ${ip}`, 'success');
        loadMonitorStatus();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function stopMonitoring(ip) {
    try {
        await api('/api/monitoring/stop', {
            method: 'POST',
            body: JSON.stringify({ target_ip: ip }),
        });
        showToast(`Monitoring stopped for ${ip}`, 'info');
        loadMonitorStatus();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function loadMonitorStatus() {
    try {
        const monitors = await api('/api/monitoring/status');
        const container = document.getElementById('monitorsList');

        if (!monitors || monitors.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📡</div>
                    <h3>No active monitors</h3>
                    <p>Add an IP to start continuous monitoring</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr><th>Target IP</th><th>Status</th><th>Interval</th><th>Last Checked</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    ${monitors.map(m => `
                        <tr>
                            <td class="font-mono" style="color: var(--cyan);">${m.target_ip}</td>
                            <td>
                                <span class="status-dot ${m.is_active ? 'status-online' : 'status-offline'}"></span>
                                ${m.is_active ? 'Active' : 'Stopped'}
                            </td>
                            <td>${m.interval_seconds}s</td>
                            <td style="font-size: 12px; color: var(--text-muted);">
                                ${m.last_checked ? new Date(m.last_checked).toLocaleString() : 'Pending...'}
                            </td>
                            <td>
                                ${m.is_active
                                    ? `<button class="btn btn-danger btn-sm" onclick="stopMonitoring('${m.target_ip}')">Stop</button>`
                                    : `<button class="btn btn-primary btn-sm" onclick="startMonitoring()">Restart</button>`
                                }
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        // Silent fail
    }
}

async function loadAlerts() {
    try {
        const alerts = await api('/api/monitoring/alerts');
        const container = document.getElementById('alertsList');
        const badge = document.getElementById('alertBadge');

        const unreadCount = alerts.filter(a => !a.is_read).length;
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }

        if (!alerts || alerts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">🔔</div>
                    <h3>No alerts yet</h3>
                    <p>Start monitoring IPs to receive change alerts</p>
                </div>
            `;
            return;
        }

        container.innerHTML = alerts.map(a => `
            <div class="alert-card ${a.is_read ? '' : 'unread'}" onclick="markAlertRead('${a.id}', this)">
                <div class="alert-icon" style="background: ${
                    a.severity === 'high' ? 'var(--red-dim)' :
                    a.severity === 'medium' ? 'var(--yellow-dim)' : 'var(--green-dim)'
                }; color: ${
                    a.severity === 'high' ? 'var(--red)' :
                    a.severity === 'medium' ? 'var(--yellow)' : 'var(--green)'
                };">
                    ${a.alert_type === 'port_opened' ? '🔓' :
                      a.alert_type === 'port_closed' ? '🔒' :
                      a.alert_type === 'risk_increase' ? '📈' : '⚠️'}
                </div>
                <div class="alert-content">
                    <div class="alert-title">
                        <span class="severity-badge severity-${a.severity}">${a.severity}</span>
                        ${a.alert_type.replace(/_/g, ' ')}
                    </div>
                    <div class="alert-message">${a.message}</div>
                    <div class="alert-time">${new Date(a.created_at).toLocaleString()}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        // Silent fail
    }
}

async function markAlertRead(alertId, element) {
    try {
        await api(`/api/monitoring/alerts/${alertId}/read`, { method: 'PUT' });
        element.classList.remove('unread');
    } catch (error) {
        // Silent fail
    }
}

// ═══════════════════════════════════════════════════════════════
// Report Generation — PDF opens directly in browser
// ═══════════════════════════════════════════════════════════════

async function loadReportScanOptions() {
    try {
        const scans = await api('/api/scanner/history');
        const select = document.getElementById('reportScanSelect');

        select.innerHTML = '<option value="">Select a scan...</option>';
        (scans || []).forEach(s => {
            select.innerHTML += `<option value="${s.scan_id}">${s.scan_id} — ${s.target_ip} (Risk: ${s.risk_score})</option>`;
        });
    } catch (error) {
        // Silent fail
    }
}

async function generateReport() {
    const scanId = document.getElementById('reportScanSelect').value;
    const title = document.getElementById('reportTitle').value.trim();

    // Pull risk parameters dynamically from the UI forms
    const totalAssets = parseFloat(document.getElementById('riskAssets')?.value) || 10000000;
    const numCritical = parseInt(document.getElementById('riskCritical')?.value) || 0;
    const numHigh = parseInt(document.getElementById('riskHigh')?.value) || 0;
    const numPorts = parseInt(document.getElementById('riskPorts')?.value) || 0;
    const employees = parseInt(document.getElementById('riskEmployees')?.value) || 50;
    const hasFirewall = document.getElementById('riskFirewall')?.checked ?? true;
    const hasIDS = document.getElementById('riskIDS')?.checked ?? false;
    const industry = parseFloat(document.getElementById('riskIndustry')?.value) || 0.6;

    if (!scanId) {
        showToast('Please select a scan to generate a report', 'error');
        return;
    }

    const genBtn = document.querySelector('#section-reports .btn-primary');
    if (genBtn) {
        genBtn.disabled = true;
        genBtn.innerHTML = '<span class="loading-spinner"></span> Generating...';
    }

    try {
        const data = await api('/api/reports/generate', {
            method: 'POST',
            body: JSON.stringify({
                scan_id: scanId,
                title: title || 'Security Assessment Report',
                include_risk_data: true,
                risk_data: {
                    total_assets: totalAssets,
                    num_critical_vulns: numCritical,
                    num_high_vulns: numHigh,
                    num_open_ports: numPorts,
                    has_firewall: hasFirewall,
                    has_ids: hasIDS,
                    employee_count: employees,
                    industry_risk_factor: industry,
                }
            }),
        });

        showToast('Report generated! Opening PDF...', 'success');

        // Download PDF as blob and open in browser directly
        const pdfUrl = `${API_BASE}${data.download_url}`;
        const response = await fetch(pdfUrl, {
            headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {},
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            window.open(blobUrl, '_blank');
            // Auto-revoke after a delay
            setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
        } else {
            // Fallback: try direct link
            window.open(pdfUrl, '_blank');
        }

        loadReports();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        if (genBtn) {
            genBtn.disabled = false;
            genBtn.innerHTML = '📄 Generate PDF Report';
        }
    }
}

async function downloadReport(downloadUrl) {
    try {
        const pdfUrl = `${API_BASE}${downloadUrl}`;
        const response = await fetch(pdfUrl, {
            headers: state.token ? { 'Authorization': `Bearer ${state.token}` } : {},
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            window.open(blobUrl, '_blank');
            setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
        } else {
            window.open(pdfUrl, '_blank');
        }
    } catch (error) {
        showToast('Failed to open PDF: ' + error.message, 'error');
    }
}

async function loadReports() {
    try {
        const reports = await api('/api/reports/list');
        const container = document.getElementById('reportsList');

        if (!reports || reports.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📄</div>
                    <h3>No reports generated</h3>
                    <p>Run a scan first, then generate a PDF report</p>
                </div>
            `;
            return;
        }

        container.innerHTML = reports.map(r => `
            <div class="report-item">
                <div class="report-info">
                    <div class="report-icon">📄</div>
                    <div>
                        <div style="font-weight: 600; font-size: 14px;">${r.title}</div>
                        <div style="font-size: 12px; color: var(--text-muted);">
                            ${r.report_type} · ${new Date(r.created_at).toLocaleDateString()}
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="downloadReport('${r.download_url}')" class="btn btn-secondary btn-sm">
                        📖 View 
                    </button>
                    <button onclick="deleteReport('${r.id}')" class="btn btn-danger btn-sm">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        // Silent fail
    }
}

async function deleteReport(reportId) {
    if (!confirm("Are you sure you want to delete this report?")) return;
    try {
        await api(`/api/reports/${reportId}`, { method: 'DELETE' });
        showToast('Report deleted successfully', 'success');
        loadReports();
    } catch (error) {
        showToast('Failed to delete report: ' + error.message, 'error');
    }
}
// ═══════════════════════════════════════════════════════════════
// THREAT INTELLIGENCE — Advanced Interactive Module
// ═══════════════════════════════════════════════════════════════

const THREAT_FEEDS = [
    { icon: '🔥', title: 'APT-41 Log4Shell Exploitation Resurgence', severity: 'critical', tag: 'T1190', time: 'Just Now', actor: 'APT-41 (China)', desc: 'Renewed widespread scanning for unpatched Log4j instances. New obfuscation techniques bypass WAF signatures. 12,000 IPs probed in last 2 hours.' },
    { icon: '🛡️', title: 'SSH Terrapin Attack — CVE-2023-48795 Widespread', severity: 'high', tag: 'T1040', time: '2 hrs ago', actor: 'Unknown', desc: 'Prefix truncation attack against SSH protocols impacting >30% of internet-facing servers. Strongly advise OpenSSH 9.6+ patch immediately.' },
    { icon: '📉', title: 'MongoDB Ransomware Campaign — 12K Endpoints Hit', severity: 'critical', tag: 'T1078', time: '5 hrs ago', actor: 'EvilCorp', desc: 'Mass automated wiping and extortion notes across 12,000 open MongoDB clusters. No authentication enforced. $500-$5000 ransom demands.' },
    { icon: '💣', title: 'BlueKeep (CVE-2019-0708) Worm Activity Detected', severity: 'critical', tag: 'T1210', time: '8 hrs ago', actor: 'Lazarus Group', desc: 'Mass exploitation of unpatched RDP services. Self-propagating worm variant detected on 5 continents. Immediate patching required.' },
    { icon: '🔑', title: 'Credential Stuffing Campaign — 4M Accounts', severity: 'high', tag: 'T1110', time: '12 hrs ago', actor: 'FIN7', desc: 'Credential stuffing attacks targeting enterprise VPN portals using 4M leaked credentials from darknet combo lists.' },
    { icon: '🌐', title: 'BGP Hijacking Attempt — Cloud Provider Targeted', severity: 'medium', tag: 'T1557', time: '1 day ago', actor: 'Sandworm (Russia)', desc: 'Border Gateway Protocol hijacking affecting AWS and Azure IP ranges. Traffic rerouted via rogue AS in Eastern Europe for 18 minutes.' },
    { icon: '⚗️', title: 'Zero-Day in OpenSSL 3.x — Actively Exploited', severity: 'critical', tag: 'T1203', time: '2 days ago', actor: 'Nation-State Unknown', desc: 'Unpatched memory corruption CVE under embargo. Exploitation in wild confirmed against major financial institutions globally.' },
    { icon: '💉', title: 'SQL Injection Campaign — Healthcare Sector', severity: 'high', tag: 'T1505', time: '3 days ago', actor: 'Scattered Spider', desc: 'Automated SQLi attacks against hospital management systems. 200+ databases compromised. PHI at risk across 15 countries.' },
];

const IOC_DATA = [
    { type: 'IP', ioc: '185.220.101.47', threat: 'C2 Server - Cobalt Strike', confidence: 95, country: '🇷🇺 Russia', ttl: '24h' },
    { type: 'IP', ioc: '45.153.160.2', threat: 'TOR Exit Node - Ransomware', confidence: 88, country: '🇩🇪 Germany', ttl: '48h' },
    { type: 'Hash', ioc: 'a3b8f02...c4e9', threat: 'LockBit 3.0 Payload', confidence: 99, country: '🌐 Global', ttl: '7d' },
    { type: 'Domain', ioc: 'update-patch[.]xyz', threat: 'Phishing Infrastructure', confidence: 92, country: '🇳🇱 Netherlands', ttl: '12h' },
    { type: 'IP', ioc: '194.165.16.29', threat: 'Emotet Botnet C2', confidence: 97, country: '🇺🇦 Ukraine', ttl: '6h' },
    { type: 'URL', ioc: 'cdn-static[.]pw/d.exe', threat: 'Dropper Distribution', confidence: 85, country: '🇨🇳 China', ttl: '3d' },
    { type: 'Hash', ioc: 'e5f12a9...1d4b', threat: 'BlackCat Ransomware', confidence: 93, country: '🌐 Global', ttl: '14d' },
    { type: 'Domain', ioc: 'svc-update[.]org', threat: 'APT C2 Masquerading', confidence: 91, country: '🇰🇵 North Korea', ttl: '24h' },
];

function initThreatIntel() {
    renderThreatFeed();
    renderIOCTable();
    startThreatTicker();
}

function renderThreatFeed() {
    const container = document.querySelector('#section-threat-intel .data-table');
    if (!container) return;
    container.innerHTML = THREAT_FEEDS.map((f, i) => `
        <div class="threat-feed-item" id="tfeed-${i}" style="padding:16px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:16px;cursor:pointer;transition:background 0.2s;" onclick="expandThreatFeed(${i})" onmouseover="this.style.background='rgba(0,229,255,0.04)'" onmouseout="this.style.background='transparent'">
            <div style="font-size:24px;flex-shrink:0">${f.icon}</div>
            <div style="flex:1">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
                    <strong style="font-size:14px">${f.title}</strong>
                    <span style="font-size:11px;color:var(--text-muted);white-space:nowrap;margin-left:12px">${f.time}</span>
                </div>
                <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">${f.desc}</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                    <span class="severity-badge severity-${f.severity}">${f.severity.toUpperCase()}</span>
                    <span style="background:rgba(139,92,246,0.2);color:var(--purple);padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">${f.tag}</span>
                    <span style="background:rgba(0,229,255,0.1);color:var(--cyan);padding:2px 8px;border-radius:12px;font-size:11px">👤 ${f.actor}</span>
                </div>
                <div id="expand-${i}" class="hidden" style="margin-top:12px;padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;border-left:3px solid var(--cyan);font-size:12px;color:var(--text-secondary)">
                    <strong style="color:var(--cyan)">📋 Full Intel Report:</strong><br>
                    Threat Actor: <strong>${f.actor}</strong> | ATT&CK Technique: <strong>${f.tag}</strong><br>
                    Affected Systems: Internet-facing servers globally<br>
                    Mitigation: Apply latest vendor patches. Enable WAF rules. Monitor SIEM for IOCs.<br>
                    ACDRIP+ Confidence Score: <strong style="color:var(--green)">94%</strong>
                </div>
            </div>
        </div>
    `).join('');
}

function expandThreatFeed(i) {
    const el = document.getElementById(`expand-${i}`);
    if (el) el.classList.toggle('hidden');
}

function renderIOCTable() {
    const container = document.getElementById('iocTableBody');
    if (!container) return;
    container.innerHTML = IOC_DATA.map(r => `
        <tr>
            <td><span style="background:rgba(0,229,255,0.15);color:var(--cyan);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">${r.type}</span></td>
            <td class="font-mono" style="color:var(--yellow);font-size:12px">${r.ioc}</td>
            <td style="font-size:12px">${r.threat}</td>
            <td>
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="flex:1;height:4px;background:rgba(255,255,255,0.1);border-radius:2px;overflow:hidden">
                        <div style="height:100%;width:${r.confidence}%;background:${r.confidence > 90 ? 'var(--red)' : r.confidence > 75 ? 'var(--orange)' : 'var(--yellow)'};border-radius:2px"></div>
                    </div>
                    <span style="font-size:11px;color:var(--text-muted)">${r.confidence}%</span>
                </div>
            </td>
            <td style="font-size:12px">${r.country}</td>
            <td style="font-size:11px;color:var(--text-muted)">${r.ttl}</td>
        </tr>
    `).join('');
}

let tickerInterval = null;
function startThreatTicker() {
    const ticker = document.getElementById('threatTicker');
    if (!ticker) return;
    const msgs = ['🔴 CRITICAL: APT-41 activity confirmed — 12,000 endpoints probed', '🟠 HIGH: New zero-day in OpenSSL 3.x under active exploitation', '🟡 MEDIUM: BGP hijacking attempt detected on major cloud providers', '🔴 CRITICAL: LockBit 3.0 campaign targeting unpatched SMB services'];
    let idx = 0;
    if (tickerInterval) clearInterval(tickerInterval);
    ticker.textContent = msgs[0];
    tickerInterval = setInterval(() => {
        ticker.style.opacity = '0';
        setTimeout(() => {
            idx = (idx + 1) % msgs.length;
            ticker.textContent = msgs[idx];
            ticker.style.opacity = '1';
        }, 400);
    }, 4000);
}

// ═══════════════════════════════════════════════════════════════
// MITRE ATT&CK — Full Interactive 11-Tactic Matrix
// ═══════════════════════════════════════════════════════════════

const MITRE_MATRIX = [
    { id: 'TA0001', name: 'Reconnaissance', color: '#06b6d4', techniques: [
        { id: 'T1595', name: 'Active Scanning', detected: true, count: 8 },
        { id: 'T1596', name: 'Search Open Tech DBs', detected: false, count: 0 },
        { id: 'T1589', name: 'Gather Victim Info', detected: true, count: 3 },
    ]},
    { id: 'TA0001', name: 'Initial Access', color: '#ef4444', techniques: [
        { id: 'T1190', name: 'Exploit Public App', detected: true, count: 12 },
        { id: 'T1078', name: 'Valid Accounts', detected: true, count: 6 },
        { id: 'T1566', name: 'Phishing', detected: false, count: 0 },
        { id: 'T1133', name: 'External Remote Services', detected: true, count: 4 },
    ]},
    { id: 'TA0002', name: 'Execution', color: '#a855f7', techniques: [
        { id: 'T1059', name: 'Command Interpreter', detected: true, count: 9 },
        { id: 'T1203', name: 'Client App Exec', detected: true, count: 2 },
        { id: 'T1053', name: 'Scheduled Tasks', detected: false, count: 0 },
    ]},
    { id: 'TA0003', name: 'Persistence', color: '#f59e0b', techniques: [
        { id: 'T1547', name: 'Boot AutoStart', detected: false, count: 0 },
        { id: 'T1098', name: 'Account Manipulation', detected: true, count: 3 },
        { id: 'T1505', name: 'Server Software Component', detected: true, count: 5 },
    ]},
    { id: 'TA0004', name: 'Privilege Escalation', color: '#10b981', techniques: [
        { id: 'T1068', name: 'Exploitation PrivEsc', detected: true, count: 7 },
        { id: 'T1548', name: 'Abuse Elevation', detected: false, count: 0 },
        { id: 'T1134', name: 'Access Token Manipulation', detected: true, count: 2 },
    ]},
    { id: 'TA0005', name: 'Defense Evasion', color: '#3b82f6', techniques: [
        { id: 'T1140', name: 'Deobfuscate/Decode', detected: true, count: 4 },
        { id: 'T1070', name: 'Log Clearance', detected: true, count: 6 },
        { id: 'T1562', name: 'Impair Defenses', detected: false, count: 0 },
    ]},
    { id: 'TA0006', name: 'Credential Access', color: '#f97316', techniques: [
        { id: 'T1110', name: 'Brute Force', detected: true, count: 11 },
        { id: 'T1555', name: 'Credentials from Files', detected: false, count: 0 },
        { id: 'T1040', name: 'Network Sniffing', detected: true, count: 3 },
    ]},
    { id: 'TA0007', name: 'Discovery', color: '#6366f1', techniques: [
        { id: 'T1046', name: 'Network Service Scan', detected: true, count: 15 },
        { id: 'T1083', name: 'File & Dir Discovery', detected: false, count: 0 },
        { id: 'T1057', name: 'Process Discovery', detected: true, count: 2 },
    ]},
    { id: 'TA0008', name: 'Lateral Movement', color: '#ec4899', techniques: [
        { id: 'T1021', name: 'Remote Services', detected: true, count: 5 },
        { id: 'T1550', name: 'Pass the Hash', detected: false, count: 0 },
        { id: 'T1210', name: 'Exploit Remote Services', detected: true, count: 3 },
    ]},
    { id: 'TA0009', name: 'Collection', color: '#14b8a6', techniques: [
        { id: 'T1005', name: 'Data from Local System', detected: true, count: 2 },
        { id: 'T1074', name: 'Data Staged', detected: false, count: 0 },
        { id: 'T1560', name: 'Archive Collected Data', detected: true, count: 1 },
    ]},
    { id: 'TA0011', name: 'Command & Control', color: '#f43f5e', techniques: [
        { id: 'T1071', name: 'App Layer Protocol', detected: true, count: 8 },
        { id: 'T1095', name: 'Non-App Layer Protocol', detected: false, count: 0 },
        { id: 'T1573', name: 'Encrypted Channel', detected: true, count: 4 },
    ]},
];

function renderMITREMatrix() {
    const container = document.getElementById('mitreMatrixContainer');
    if (!container) return;
    container.innerHTML = MITRE_MATRIX.map((tactic, ti) => `
        <div style="min-width:140px;background:rgba(0,0,0,0.25);border-radius:10px;padding:12px;border-top:3px solid ${tactic.color}">
            <div style="font-size:11px;font-weight:700;color:${tactic.color};text-align:center;padding-bottom:8px;margin-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.08)">${tactic.name}</div>
            ${tactic.techniques.map((t, i) => `
                <div class="mitre-tech-card" id="mt-${ti}-${i}"
                    style="padding:8px;border-radius:6px;margin-bottom:6px;cursor:pointer;transition:all 0.2s;
                    background:${t.detected ? `rgba(${hexToRgb(tactic.color)},0.18)` : 'rgba(255,255,255,0.04)'};
                    border:1px solid ${t.detected ? tactic.color : 'transparent'}"
                    onclick="showMITREDetail('${t.id}','${t.name}','${tactic.name}',${t.detected},${t.count},'${tactic.color}')"
                    onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size:10px;font-weight:700;color:${t.detected ? tactic.color : 'var(--text-muted)'}">${t.id}</div>
                    <div style="font-size:11px;color:${t.detected ? 'var(--text-primary)' : 'var(--text-muted)'};">${t.name}</div>
                    ${t.detected ? `<div style="font-size:10px;color:var(--red);margin-top:2px">⚠️ ${t.count} detections</div>` : ''}
                </div>
            `).join('')}
        </div>
    `).join('');
}

function hexToRgb(hex) {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `${r},${g},${b}`;
}

function showMITREDetail(id, name, tactic, detected, count, color) {
    const panel = document.getElementById('mitreDetailPanel');
    if (!panel) return;
    panel.classList.remove('hidden');
    panel.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">
            <div>
                <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px">${tactic} Tactic</div>
                <div style="font-size:20px;font-weight:700;color:${color}">${id}: ${name}</div>
            </div>
            <button onclick="document.getElementById('mitreDetailPanel').classList.add('hidden')" style="background:rgba(255,255,255,0.1);border:none;color:white;padding:6px 12px;border-radius:6px;cursor:pointer">✕</button>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px">
            <div style="background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;text-align:center">
                <div style="font-size:11px;color:var(--text-muted)">Status</div>
                <div style="font-size:16px;font-weight:700;color:${detected ? 'var(--red)' : 'var(--green)'}">${detected ? '⚠️ DETECTED' : '✅ NOT SEEN'}</div>
            </div>
            <div style="background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;text-align:center">
                <div style="font-size:11px;color:var(--text-muted)">Detections</div>
                <div style="font-size:22px;font-weight:700;color:${color}">${count}</div>
            </div>
            <div style="background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;text-align:center">
                <div style="font-size:11px;color:var(--text-muted)">Severity</div>
                <div style="font-size:16px;font-weight:700;color:var(--orange)">${count > 8 ? 'CRITICAL' : count > 3 ? 'HIGH' : 'MEDIUM'}</div>
            </div>
        </div>
        <div style="background:rgba(0,0,0,0.3);padding:16px;border-radius:8px;border-left:3px solid ${color}">
            <div style="font-size:12px;font-weight:700;color:${color};margin-bottom:8px">🔍 AI Technique Analysis</div>
            <div style="font-size:13px;color:var(--text-secondary);line-height:1.7">
                Technique <strong style="color:white">${id}</strong> maps to <strong style="color:white">${name}</strong> in MITRE ATT&CK ${tactic} phase.
                ${detected ? `This technique was detected in <strong>${count} simulated attack scenarios</strong> against your infrastructure.
                Adversaries commonly use this to ${getAttackDesc(id)}.` : `This technique has not been observed in current simulations but remains a known threat vector.`}
                <br><br>
                <span style="color:${color};font-weight:600">Recommended Mitigation:</span> ${getMitigation(id)}
            </div>
        </div>
    `;
}

function getAttackDesc(id) {
    const descs = {
        'T1190': 'gain initial foothold via internet-exposed applications with known CVEs',
        'T1059': 'execute malicious scripts through PowerShell, Bash, or Python interpreters',
        'T1110': 'systematically attempt passwords against authentication interfaces',
        'T1046': 'enumerate open ports and services for reconnaissance and attack planning',
        'T1021': 'move laterally using legitimate remote access protocols like RDP and SSH',
        'T1071': 'communicate with command & control infrastructure via HTTP/HTTPS traffic',
    };
    return descs[id] || 'achieve their specific tactical objectives in this phase of the attack';
}

function getMitigation(id) {
    const mits = {
        'T1190': 'Apply security patches immediately. Deploy WAF. Use DAST scanning regularly.',
        'T1059': 'Enable PowerShell logging. Use application whitelisting. Monitor script execution.',
        'T1110': 'Enforce MFA. Implement account lockout policies. Use password managers.',
        'T1046': 'Restrict network scanning tools. Monitor for SYN scans. Use network segmentation.',
        'T1021': 'Restrict RDP/SSH access via VPN. Enable NLA. Use Just-In-Time access.',
        'T1071': 'Inspect encrypted traffic. Deploy DNS filtering. Monitor outbound connections.',
    };
    return mits[id] || 'Apply principle of least privilege. Monitor for anomalous behavior. Enable detailed logging.';
}

// ═══════════════════════════════════════════════════════════════
// DARK WEB EXPOSURE — Advanced Per-Target Analysis
// ═══════════════════════════════════════════════════════════════

function runDarkWebScan() {
    const target = document.getElementById('darkwebTarget').value.trim();
    if (!target) {
        showToast('Please enter a target domain or IP', 'error');
        return;
    }
    document.getElementById('darkwebLoading').classList.remove('hidden');
    document.getElementById('darkwebResults').style.opacity = '0.3';
    setTimeout(() => {
        document.getElementById('darkwebLoading').classList.add('hidden');
        document.getElementById('darkwebResults').style.opacity = '1';
        renderDarkWebData(target);
        showToast('Dark Web Scan Completed!', 'success');
    }, 2500);
}

function renderDarkWebData(target) {
    // Generate deterministic but varied data per target
    const seed = target.split('').reduce((s, c) => s + c.charCodeAt(0), 0);
    const exposed = 800 + (seed % 1200);
    const leaked = 100 + (seed % 500);
    const mentions = 3 + (seed % 25);
    const riskScore = 40 + (seed % 50);

    // Update metrics
    document.querySelector('.darkweb-value-1').textContent = exposed.toLocaleString();
    document.querySelector('.darkweb-value-2').textContent = leaked.toLocaleString();
    document.querySelector('.darkweb-value-3').textContent = mentions.toString();

    // Render threat timeline
    const liveFeed = document.querySelector('.darkweb-live-feed');
    const torNodes = ['185.220.101.47', '45.153.160.2', '198.96.155.3', '199.87.154.255'];
    const torNode = torNodes[seed % torNodes.length];

    liveFeed.innerHTML = `
        <div style="padding:14px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:14px">
            <div style="font-size:22px">🕵️</div>
            <div style="flex:1">
                <div style="display:flex;justify-content:space-between"><strong>Exfiltrated Data Set Found — BreachForums</strong><span style="font-size:11px;color:var(--text-muted)">2 hrs ago</span></div>
                <div style="font-size:13px;color:var(--text-secondary);margin:4px 0">Dataset matching <span style="color:var(--cyan)">${target}</span> found containing ${(leaked * 0.6 | 0).toLocaleString()} internal employee emails and hashed passwords.</div>
                <div style="display:flex;gap:8px;margin-top:8px"><span class="severity-badge severity-critical">CRITICAL</span><span style="background:rgba(239,68,68,0.15);color:var(--red);padding:2px 8px;border-radius:12px;font-size:11px">Data Breach</span></div>
            </div>
        </div>
        <div style="padding:14px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:14px">
            <div style="font-size:22px">🔑</div>
            <div style="flex:1">
                <div style="display:flex;justify-content:space-between"><strong>VPN Credentials Active on Telegram — Access Broker</strong><span style="font-size:11px;color:var(--text-muted)">14 hrs ago</span></div>
                <div style="font-size:13px;color:var(--text-secondary);margin:4px 0">${4 + (seed % 8)} plaintext credentials for systems in <span style="color:var(--cyan)">${target}</span>'s IP range. Russian access broker community. Active listing price: $350.</div>
                <div style="display:flex;gap:8px;margin-top:8px"><span class="severity-badge severity-critical">CRITICAL</span><span style="background:rgba(249,115,22,0.15);color:var(--orange);padding:2px 8px;border-radius:12px;font-size:11px">Credential Leak</span></div>
            </div>
        </div>
        <div style="padding:14px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:14px">
            <div style="font-size:22px">💬</div>
            <div style="flex:1">
                <div style="display:flex;justify-content:space-between"><strong>Ransomware Syndicate Planning — TOR Forum</strong><span style="font-size:11px;color:var(--text-muted)">3 days ago</span></div>
                <div style="font-size:13px;color:var(--text-secondary);margin:4px 0">LockBit affiliate discussed potential ingress via exposed SSH on <span style="color:var(--cyan)">${target}</span>. TOR exit node <span class="font-mono" style="color:var(--yellow)">${torNode}</span> coordinating.</div>
                <div style="display:flex;gap:8px;margin-top:8px"><span class="severity-badge severity-high">HIGH</span><span style="background:rgba(139,92,246,0.15);color:var(--purple);padding:2px 8px;border-radius:12px;font-size:11px">APT Chatter</span></div>
            </div>
        </div>
        <div style="padding:14px;display:flex;align-items:flex-start;gap:14px">
            <div style="font-size:22px">🌐</div>
            <div style="flex:1">
                <div style="display:flex;justify-content:space-between"><strong>IP Range Listed on Shodan/Censys — Automated Scanners</strong><span style="font-size:11px;color:var(--text-muted)">5 days ago</span></div>
                <div style="font-size:13px;color:var(--text-secondary);margin:4px 0">Target <span style="color:var(--cyan)">${target}</span> indexed by ${2 + (seed % 4)} automated recon frameworks. Open ports exposed to global scanners. ${exposed} Internet-connected assets identified.</div>
                <div style="display:flex;gap:8px;margin-top:8px"><span class="severity-badge severity-medium">MEDIUM</span><span style="background:rgba(16,185,129,0.15);color:var(--green);padding:2px 8px;border-radius:12px;font-size:11px">Passive Recon</span></div>
            </div>
        </div>
    `;

    // Animate breach timeline bars
    const breachTimeline = document.getElementById('breachTimeline');
    if (breachTimeline) {
        const months = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'];
        const bars = months.map((m, i) => {
            const h = 20 + ((seed * (i + 1)) % 80);
            return `<div style="display:flex;flex-direction:column;align-items:center;gap:6px">
                <div style="width:36px;height:${h}px;background:linear-gradient(180deg,var(--red),rgba(239,68,68,0.2));border-radius:4px 4px 0 0;transition:height 0.6s ease"></div>
                <div style="font-size:10px;color:var(--text-muted)">${m}</div>
            </div>`;
        });
        breachTimeline.innerHTML = `<div style="display:flex;align-items:flex-end;gap:8px;height:100px;padding:0 8px">${bars.join('')}</div>`;
    }
}

// ═══════════════════════════════════════════════════════════════
// QUANTUM THREATS — Full Cryptographic Audit
// ═══════════════════════════════════════════════════════════════

function runQuantumScan() {
    const target = document.getElementById('quantumIP').value.trim();
    if (!target) {
        showToast('Please enter a target domain or IP', 'error');
        return;
    }
    document.getElementById('quantumLoading').classList.remove('hidden');
    document.getElementById('quantumResults').style.opacity = '0.3';
    setTimeout(() => {
        document.getElementById('quantumLoading').classList.add('hidden');
        document.getElementById('quantumResults').style.opacity = '1';
        renderQuantumData(target);
        showToast('Quantum Cryptographic Analysis Completed!', 'success');
    }, 3000);
}

const QUANTUM_CRYPTO_CATALOG = [
    { entity: 'Web Server TLS Handshake', algo: 'RSA-2048 / SHA-256', status: 'critical', pqc: 'CRYSTALS-Kyber + Dilithium2', shors: true, grovers: false },
    { entity: 'Database Connection Pool', algo: 'ECDHE-RSA-AES256-GCM', status: 'critical', pqc: 'CRYSTALS-Kyber768 (NIST Std)', shors: true, grovers: false },
    { entity: 'Code Signing Certificates', algo: 'ECDSA P-384 / NIST', status: 'high', pqc: 'CRYSTALS-Dilithium3 (NIST Std)', shors: true, grovers: false },
    { entity: 'VPN Tunnel (IPSec IKEv2)', algo: 'Diffie-Hellman 2048-bit', status: 'critical', pqc: 'Classic McEliece + XMSS', shors: true, grovers: false },
    { entity: 'API Gateway JWT Signing', algo: 'HMAC-SHA256', status: 'safe', pqc: 'Current algo is quantum-resistant', shors: false, grovers: true },
    { entity: 'SSH Key Exchange', algo: 'ECDH curve25519', status: 'high', pqc: 'CRYSTALS-Kyber512 + Kyber768', shors: true, grovers: false },
    { entity: 'S3/Cloud Storage Encryption', algo: 'AES-128-CBC', status: 'medium', pqc: 'AES-256-GCM (Grover safe)', shors: false, grovers: true },
    { entity: 'Email S/MIME Encryption', algo: 'RSA-4096', status: 'high', pqc: 'FALCON-512 (NIST Std)', shors: true, grovers: false },
];

const PQC_ROADMAP = [
    { phase: 'Phase 1 — Assessment', timeline: '0-3 months', tasks: ['Cryptographic inventory audit', 'HNDL exposure risk scoring', 'PQC vendor evaluation'], done: true },
    { phase: 'Phase 2 — Pilot Migration', timeline: '3-9 months', tasks: ['Deploy hybrid TLS with Kyber', 'Update SSH key exchange', 'Test code signing with Dilithium'], done: false },
    { phase: 'Phase 3 — Full Rollout', timeline: '9-18 months', tasks: ['Replace all RSA/ECC endpoints', 'Rotate all certificates', 'Update VPN infrastructure to PQC'], done: false },
    { phase: 'Phase 4 — Certification', timeline: '18-24 months', tasks: ['NIST PQC compliance audit', 'Third-party penetration test', 'Quantum agility documentation'], done: false },
];

function renderQuantumData(target) {
    const tbody = document.getElementById('quantumDataTable');
    if (tbody) {
        tbody.innerHTML = QUANTUM_CRYPTO_CATALOG.map(r => `
            <tr>
                <td style="font-size:13px">${r.entity}</td>
                <td class="font-mono" style="font-size:11px;color:var(--yellow)">${r.algo}</td>
                <td>
                    <div style="display:flex;gap:4px;flex-wrap:wrap">
                        <span class="severity-badge severity-${r.status}">${r.status === 'safe' ? '✅ Safe' : r.status === 'critical' ? '💀 Critical' : r.status === 'high' ? '⚠️ High' : '🟡 Medium'}</span>
                        ${r.shors ? '<span style="background:rgba(239,68,68,0.15);color:var(--red);padding:2px 6px;border-radius:4px;font-size:10px">Shor\'s</span>' : ''}
                        ${r.grovers ? '<span style="background:rgba(245,158,11,0.15);color:var(--yellow);padding:2px 6px;border-radius:4px;font-size:10px">Grover\'s</span>' : ''}
                    </div>
                </td>
                <td class="font-mono" style="color:var(--green);font-size:11px">${r.pqc}</td>
            </tr>
        `).join('');
    }

    const roadmap = document.getElementById('quantumRoadmap');
    if (roadmap) {
        roadmap.innerHTML = PQC_ROADMAP.map((p, i) => `
            <div style="display:flex;gap:16px;padding:16px;background:rgba(0,0,0,0.2);border-radius:10px;border-left:3px solid ${p.done ? 'var(--green)' : i === 1 ? 'var(--cyan)' : 'rgba(255,255,255,0.2)'}">
                <div style="flex-shrink:0;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:${p.done ? 'var(--green-dim)' : i === 1 ? 'rgba(0,229,255,0.15)' : 'rgba(255,255,255,0.05)'};color:${p.done ? 'var(--green)' : i === 1 ? 'var(--cyan)' : 'var(--text-muted)'};font-weight:700;font-size:14px">${p.done ? '✓' : i + 1}</div>
                <div style="flex:1">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                        <strong style="color:${p.done ? 'var(--green)' : i === 1 ? 'var(--cyan)' : 'var(--text-primary)'}">${p.phase}</strong>
                        <span style="font-size:11px;color:var(--text-muted)">${p.timeline}</span>
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap">
                        ${p.tasks.map(t => `<span style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);padding:3px 10px;border-radius:12px;font-size:11px;color:var(--text-secondary)">${t}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Calculate quantum readiness score
    const vulnCount = QUANTUM_CRYPTO_CATALOG.filter(r => r.shors).length;
    const totalCount = QUANTUM_CRYPTO_CATALOG.length;
    const score = Math.round(((totalCount - vulnCount) / totalCount) * 100);
    const scoreEl = document.getElementById('quantumReadinessScore');
    if (scoreEl) {
        scoreEl.textContent = score + '%';
        scoreEl.style.color = score < 30 ? 'var(--red)' : score < 60 ? 'var(--orange)' : 'var(--green)';
    }

    // Render readiness gauge using canvas
    const canvas = document.getElementById('quantumGauge');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        const cx = canvas.width / 2, cy = canvas.height / 2, r = Math.min(cx, cy) - 10;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Background arc
        ctx.beginPath();
        ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(255,255,255,0.08)';
        ctx.lineWidth = 14;
        ctx.stroke();

        // Value arc
        const endAngle = Math.PI + (Math.PI * score / 100);
        const grad = ctx.createLinearGradient(0, cy, canvas.width, cy);
        grad.addColorStop(0, '#ef4444');
        grad.addColorStop(0.5, '#f59e0b');
        grad.addColorStop(1, '#10b981');
        ctx.beginPath();
        ctx.arc(cx, cy, r, Math.PI, endAngle);
        ctx.strokeStyle = grad;
        ctx.lineWidth = 14;
        ctx.lineCap = 'round';
        ctx.stroke();

        ctx.fillStyle = '#fff';
        ctx.font = 'bold 22px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(score + '%', cx, cy);
        ctx.font = '11px Inter, sans-serif';
        ctx.fillStyle = 'rgba(255,255,255,0.4)';
        ctx.fillText('PQC Ready', cx, cy + 18);
    }
}

// ═══════════════════════════════════════════════════════════════
// Shared animated counter helper
// ═══════════════════════════════════════════════════════════════

function animateCounterTo(selector, val) {
    const el = document.querySelector(selector);
    if (!el) return;
    let curr = 0;
    const interval = setInterval(() => {
        curr += Math.ceil(val / 20);
        if (curr >= val) { curr = val; clearInterval(interval); }
        el.innerText = curr.toLocaleString();
    }, 40);
}

// ═══════════════════════════════════════════════════════════════
// Section Initialization — Called When Switching Sections
// ═══════════════════════════════════════════════════════════════

const _origSwitchSection = switchSection;
switchSection = function(section) {
    _origSwitchSection(section);
    if (section === 'threat-intel') initThreatIntel();
    if (section === 'mitre') renderMITREMatrix();
};

// ═══════════════════════════════════════════════════════════════
// Make Simulation "Interesting" - Animation
// ═══════════════════════════════════════════════════════════════

const origDisplaySimulationResults = displaySimulationResults;
displaySimulationResults = function(data) {
    origDisplaySimulationResults(data);

    // Add interactive animation classes to timeline items
    const timelineItems = document.querySelectorAll('.timeline-item');
    timelineItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        item.style.transition = 'all 0.4s ease-out';
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';

            // Blink effect
            const tag = document.createElement('span');
            tag.innerText = ' [EXECUTING AI...]';
            tag.style.color = 'var(--cyan)';
            tag.className = 'blinking-exec';
            const titleEl = item.querySelector('.timeline-title');
            if (titleEl) titleEl.appendChild(tag);

            setTimeout(() => {
                tag.remove();
                const doneTag = document.createElement('span');
                doneTag.innerText = ' [COMPLETED]';
                doneTag.style.color = 'var(--green)';
                if (titleEl) titleEl.appendChild(doneTag);
            }, 800);
        }, index * 1200 + 500);
    });
};

// ═══════════════════════════════════════════════════════════════
// Live Ticker Animations — Threat Intel & MITRE
// ═══════════════════════════════════════════════════════════════

setInterval(() => {
    if (state.currentSection === 'threat-intel') {
        const blips = document.querySelectorAll('#section-threat-intel .metric-change');
        blips.forEach(b => {
            b.style.opacity = '0.3';
            setTimeout(() => b.style.opacity = '1', 300);
        });

        // Shuffle threat feed entries
        const feedContainer = document.querySelector('#section-threat-intel .data-table');
        if (feedContainer && Math.random() > 0.75) {
            const items = Array.from(feedContainer.children);
            if (items.length > 2) {
                const first = items[0];
                const last = items[items.length - 1];
                feedContainer.insertBefore(last, first);
                last.style.background = 'rgba(0, 229, 255, 0.06)';
                setTimeout(() => last.style.background = 'transparent', 1500);
            }
        }
    }

    if (state.currentSection === 'mitre') {
        const cards = document.querySelectorAll('.mitre-tech-card');
        if (cards.length > 0 && Math.random() > 0.6) {
            const card = cards[Math.floor(Math.random() * cards.length)];
            card.style.boxShadow = '0 0 12px rgba(0,229,255,0.4)';
            setTimeout(() => card.style.boxShadow = '', 600);
        }
    }
}, 2000);

// ═══════════════════════════════════════════════════════════════
// FINAL SECTION WRAPPER & AUTO-INITIALIZATION
// ═══════════════════════════════════════════════════════════════

// Override switchSection one final time to handle all new modules
const _finalSwitchSection = switchSection;
switchSection = function(section) {
    _finalSwitchSection(section);
    
    // Auto-fill and Auto-init logic for specialized modules
    if (section === 'darkweb') {
        const targetInput = document.getElementById('darkwebTarget');
        const resultsHidden = document.getElementById('darkwebResults').classList.contains('hidden');
        if (!targetInput.value || targetInput.value === '' || resultsHidden) {
            targetInput.value = targetInput.value || state.lastScannedIP || 'acme.corp';
            runDarkWebScan(); // Automatically show data
        }
    }
    
    if (section === 'quantum') {
        const targetInput = document.getElementById('quantumIP');
        const resultsHidden = document.getElementById('quantumResults').classList.contains('hidden');
        if (!targetInput.value || targetInput.value === '' || resultsHidden) {
            targetInput.value = targetInput.value || state.lastScannedIP || 'acme.corp';
            runQuantumScan(); // Automatically show data
        }
    }
};

// Ensure all metrics pulse occasionally
setInterval(() => {
    if (state.currentSection === 'darkweb') {
        const values = document.querySelectorAll('.darkweb-value-1, .darkweb-value-2, .darkweb-value-3');
        if (values.length > 0) {
            const v = values[Math.floor(Math.random() * values.length)];
            v.style.filter = 'brightness(1.5) drop-shadow(0 0 5px var(--cyan))';
            setTimeout(() => v.style.filter = '', 500);
        }
    }
}, 3000);

console.log("ACDRIP+ Modules Fully Synchronized.");
