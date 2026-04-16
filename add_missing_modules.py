import os
import re

html_injection = """
        <!-- ===== 8. DARK WEB EXPOSURE ===== -->
        <div class="section" id="section-darkweb">
            <div class="page-header">
                <h1 class="page-title">🕸️ Dark Web Exposure Tracker</h1>
                <p class="page-subtitle">OSINT Analysis, Credential Leaks, and Breach Activity</p>
            </div>
            
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div class="card-title">Run Exposure Audit</div>
                </div>
                <div style="display:flex; gap:10px;">
                    <input type="text" id="dwInput" class="form-input" placeholder="Enter Domain or IP (e.g., example.com)" style="flex:1;">
                    <button class="btn btn-primary" onclick="initDarkWeb()">Scan OSINT</button>
                </div>
            </div>

            <div id="dwResults" class="hidden">
                <div class="metrics-grid" style="margin-bottom: 20px;">
                    <div class="metric-card">
                        <div class="metric-label">Breach Mentions</div>
                        <div class="metric-value" id="dwMentions" style="color:var(--red)">0</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Leaked Credentials</div>
                        <div class="metric-value" id="dwCreds" style="color:var(--orange)">0</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Ransomware Chatter</div>
                        <div class="metric-value" id="dwChatter" style="color:var(--purple)">0</div>
                    </div>
                </div>

                <div class="card" style="margin-bottom:20px;">
                    <div class="card-header"><div class="card-title">6-Month Breach Timeline</div></div>
                    <div style="height:250px;">
                        <canvas id="dwChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header"><div class="card-title">Recent Intelligence</div></div>
                    <div id="dwFeed" class="data-table"></div>
                </div>
            </div>
        </div>

        <!-- ===== 9. QUANTUM THREAT INTEL ===== -->
        <div class="section" id="section-quantum">
            <div class="page-header">
                <h1 class="page-title">⚛️ Post-Quantum Cryptographic Audit</h1>
                <p class="page-subtitle">Evaluate risk against Shor's and Grover's Algorithms & NIST PQC Migration</p>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:20px;">
                <div class="card" style="display:flex; flex-direction:column; align-items:center;">
                    <div class="card-header" style="width:100%; border:none;"><div class="card-title">Quantum Readiness</div></div>
                    <canvas id="quantumCanvas" width="300" height="150" style="margin-top:20px;"></canvas>
                    <div id="qScoreText" style="font-size:32px; font-weight:bold; color:var(--cyan); margin-top:10px;">--%</div>
                    <p style="color:var(--text-secondary); margin-top:10px;">Overall PQC Resilience</p>
                </div>

                <div class="card">
                    <div class="card-header"><div class="card-title">NIST Migration Roadmap</div></div>
                    <ul style="list-style:none; padding:10px 0;">
                        <li style="margin-bottom:15px; display:flex; align-items:center; gap:10px;">
                            <span style="color:var(--green)">✅</span> 1. Asset Discovery & Inventory
                        </li>
                        <li style="margin-bottom:15px; display:flex; align-items:center; gap:10px;">
                            <span style="color:var(--orange)">⏳</span> 2. Identify Vulnerable Algorithms (In Progress)
                        </li>
                        <li style="margin-bottom:15px; display:flex; align-items:center; gap:10px;">
                            <span style="color:var(--text-muted)">○</span> 3. Pilot Deployment (Kyber, Dilithium)
                        </li>
                        <li style="display:flex; align-items:center; gap:10px;">
                            <span style="color:var(--text-muted)">○</span> 4. Full Enterprise Rollout
                        </li>
                    </ul>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Cryptographic Asset Audit</div>
                    <button class="btn btn-secondary btn-sm" onclick="initQuantum()">Run Audit</button>
                </div>
                <table class="data-table">
                    <thead><tr><th>Subsystem</th><th>Current Algorithm</th><th>Q-Day Vulnerability</th><th>NIST Recommendation</th></tr></thead>
                    <tbody id="qAuditTable">
                        <tr><td colspan="4" style="text-align:center; padding:20px;">Click 'Run Audit' to begin evaluation.</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
"""

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'id="section-darkweb"' not in html:
    html = html.replace('</main>', html_injection + '\n    </main>')
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added Dark Web and Quantum to HTML.")
else:
    print("HTML sections already exist.")

js_injection = """
// ═══════════════════════════════════════════════════════════════
// DARK WEB EXPOSURE LOGIC
// ═══════════════════════════════════════════════════════════════
let dwChartInstance = null;

function initDarkWeb() {
    const input = document.getElementById('dwInput').value.trim();
    if(!input) {
        showToast('Please enter a domain or IP address', 'error');
        return;
    }
    
    document.getElementById('dwResults').classList.remove('hidden');
    
    // Deterministic simulation based on string length
    const score = input.length * 7;
    const mentions = (score % 42) + 5;
    const creds = (score % 115) * 3;
    const chatter = (score % 8);
    
    animateValue(document.getElementById('dwMentions'), 0, mentions, 1000);
    animateValue(document.getElementById('dwCreds'), 0, creds, 1500);
    animateValue(document.getElementById('dwChatter'), 0, chatter, 800);
    
    renderDwChart();
    renderDwFeed(input);
}

function renderDwChart() {
    const ctx = document.getElementById('dwChart').getContext('2d');
    if(dwChartInstance) dwChartInstance.destroy();
    
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const data = Array.from({length:6}, () => Math.floor(Math.random() * 50) + 10);
    
    dwChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Breach Indicators',
                data: data,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks:{color:'#64748b'} },
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks:{color:'#64748b'} }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function renderDwFeed(target) {
    const feed = document.getElementById('dwFeed');
    feed.innerHTML = `
        <div style="padding:15px; border-bottom:1px solid rgba(255,255,255,0.05);">
            <strong style="color:var(--red);">[BreachForums]</strong> Mention of database dump potentially related to ${target}.
            <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">2 days ago</div>
        </div>
        <div style="padding:15px; border-bottom:1px solid rgba(255,255,255,0.05);">
            <strong style="color:var(--orange);">[Telegram]</strong> Credential combo-list containing ${target} references shared in private group.
            <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">1 week ago</div>
        </div>
        <div style="padding:15px;">
            <strong style="color:var(--purple);">[TOR Exit Node]</strong> Traffic matching ${target} detected exiting via known bad actor infrastructure.
            <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">3 weeks ago</div>
        </div>
    `;
}

// ═══════════════════════════════════════════════════════════════
// QUANTUM THREAT INTEL LOGIC
// ═══════════════════════════════════════════════════════════════
function initQuantum() {
    const table = document.getElementById('qAuditTable');
    table.innerHTML = `
        <tr><td>Web TLS Endpoints</td><td class="font-mono">RSA-2048</td><td><span class="severity-badge severity-critical">Vulnerable (Shor's)</span></td><td class="font-mono" style="color:var(--green)">CRYSTALS-Kyber</td></tr>
        <tr><td>Database Connect</td><td class="font-mono">AES-128-GCM</td><td><span class="severity-badge severity-medium">Medium (Grover's)</span></td><td class="font-mono" style="color:var(--green)">AES-256 (Upgrade keys)</td></tr>
        <tr><td>Auth JWT Signing</td><td class="font-mono">RS256</td><td><span class="severity-badge severity-critical">Vulnerable (Shor's)</span></td><td class="font-mono" style="color:var(--green)">CRYSTALS-Dilithium</td></tr>
        <tr><td>SSH Host Keys</td><td class="font-mono">ECDSA (nistp256)</td><td><span class="severity-badge severity-critical">Vulnerable (Shor's)</span></td><td class="font-mono" style="color:var(--green)">SPHINCS+</td></tr>
        <tr><td>Internal VPN</td><td class="font-mono">Diffie-Hellman</td><td><span class="severity-badge severity-high">Vulnerable (Shor's)</span></td><td class="font-mono" style="color:var(--green)">BIKE or HQC</td></tr>
        <tr><td>Cold Storage Data</td><td class="font-mono">AES-256</td><td><span class="severity-badge severity-safe" style="color:var(--green)">Quantum Resistant</span></td><td class="font-mono" style="color:var(--green)">No Change Required</td></tr>
    `;
    
    // Animate canvas score
    const targetScore = 25; // 25% ready
    let currentScore = 0;
    
    const intv = setInterval(() => {
        currentScore++;
        renderQuantumGauge(currentScore);
        document.getElementById('qScoreText').innerText = currentScore + '%';
        if(currentScore >= targetScore) clearInterval(intv);
    }, 20);
}

function renderQuantumGauge(score) {
    const canvas = document.getElementById('quantumCanvas');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const cx = canvas.width / 2;
    const cy = canvas.height - 10;
    const radius = 100;
    
    // Draw background arc
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, 0, false);
    ctx.lineWidth = 20;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.stroke();
    
    // Draw color arc
    const endAngle = Math.PI + (Math.PI * (score / 100));
    
    // Gradient
    const gradient = ctx.createLinearGradient(0, cy, canvas.width, cy);
    gradient.addColorStop(0, '#ef4444');  // Red
    gradient.addColorStop(0.5, '#f59e0b'); // Amber
    gradient.addColorStop(1, '#10b981');   // Green
    
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, endAngle, false);
    ctx.lineWidth = 20;
    ctx.strokeStyle = gradient;
    ctx.stroke();
}

// Ensure switchSection handles these if necessary by overriding it if it hasn't been already
if (typeof _origSwitchSection_v2 === 'undefined') {
    const _origSwitchSection_v2 = switchSection;
    switchSection = function(section) {
        _origSwitchSection_v2(section);
        // Add any auto-loading logic here if required
        if (section === 'quantum' && document.getElementById('qScoreText').innerText === '--%') {
            renderQuantumGauge(0);
        }
    };
}
"""

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

if 'initDarkWeb()' not in js:
    with open('frontend/js/app.js', 'a', encoding='utf-8') as f:
        f.write('\n' + js_injection)
    print("Added Dark Web and Quantum logic to JS.")
else:
    print("JS logic already exists.")
