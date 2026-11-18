#!/usr/bin/env python3
"""
Multi-Agent Security Monitoring Dashboard
Complete end-to-end web application with authentication, file watching, 
agent delegation, and automated report generation.

Run: python3 web_app.py
Access: http://localhost:8000
"""

import os
import sys
import json
import time
import threading
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, unquote
import sqlite3
import base64


# ============================================================================
# Configuration
# ============================================================================

PORT = 8000
HOST = 'localhost'
WATCH_DIR = Path('/tmp/logs')
WORKSPACE_DIR = Path('/tmp/workspace')
DB_PATH = WORKSPACE_DIR / 'security_monitor.db'
LOGS_DIR = WORKSPACE_DIR / 'logs'
REPORTS_DIR = WORKSPACE_DIR / 'reports'

# Create directories
for d in [WATCH_DIR, WORKSPACE_DIR, LOGS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class User:
    """User account."""
    id: int
    username: str
    email: str
    password_hash: str
    created_at: str
    last_login: str = None


@dataclass
class Session:
    """Active user session."""
    session_id: str
    user_id: int
    created_at: str
    expires_at: str


@dataclass
class LogEntry:
    """Application log entry."""
    timestamp: str
    level: str
    component: str
    message: str
    data: Dict[str, Any]


@dataclass
class Finding:
    """Security analysis finding."""
    id: int
    analysis_type: str
    finding_type: str
    severity: str
    title: str
    description: str
    evidence: str
    recommended_action: str
    report_id: int
    timestamp: str


@dataclass
class Report:
    """Security analysis report."""
    id: int
    log_file: str
    analysis_type: str
    risk_level: str
    status: str
    created_at: str
    findings_count: int = 0


# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                component TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT
            )
        ''')
        
        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY,
                log_file TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                findings_count INTEGER DEFAULT 0
            )
        ''')
        
        # Findings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY,
                analysis_type TEXT NOT NULL,
                finding_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                evidence TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                report_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default user if not exists
        self.get_or_create_user('admin', 'admin@monitor.local', 'admin123')
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, hash_str: str) -> bool:
        """Verify password against hash."""
        salt, hash_hex = hash_str.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_hex
    
    def get_or_create_user(self, username: str, email: str, password: str) -> User:
        """Get existing user or create new one."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        if row:
            conn.close()
            return User(*row)
        
        # Create new user
        now = datetime.utcnow().isoformat() + 'Z'
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, now))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return User(user_id, username, email, password_hash, now)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user and return session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        user = User(*row)
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def create_session(self, user_id: int) -> str:
        """Create new session for user."""
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow().isoformat() + 'Z'
        expires_at = datetime.utcnow().timestamp() + 86400  # 24 hours
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (session_id, user_id, now, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session if valid."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now_ts = datetime.utcnow().timestamp()
        cursor.execute('''
            SELECT session_id, user_id, created_at, expires_at FROM sessions
            WHERE session_id = ? AND expires_at > ?
        ''', (session_id, now_ts))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Session(*row)
    
    def log_event(self, level: str, component: str, message: str, data: Dict = None):
        """Log an event."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (timestamp, level, component, message, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.utcnow().isoformat() + 'Z', level, component, message, json.dumps(data or {})))
        
        conn.commit()
        conn.close()
    
    def create_report(self, log_file: str, analysis_type: str) -> int:
        """Create analysis report."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (log_file, analysis_type, risk_level, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (log_file, analysis_type, 'PENDING', 'PENDING', datetime.utcnow().isoformat() + 'Z'))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    def add_finding(self, report_id: int, finding: Finding):
        """Add finding to report."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO findings 
            (analysis_type, finding_type, severity, title, description, evidence, 
             recommended_action, report_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (finding.analysis_type, finding.finding_type, finding.severity, 
              finding.title, finding.description, finding.evidence, 
              finding.recommended_action, report_id, datetime.utcnow().isoformat() + 'Z'))
        
        conn.commit()
        conn.close()
    
    def get_reports(self, limit: int = 10) -> List[Dict]:
        """Get recent reports."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, log_file, analysis_type, risk_level, status, created_at, findings_count
            FROM reports ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(['id', 'log_file', 'analysis_type', 'risk_level', 'status', 'created_at', 'findings_count'], row)) for row in rows]
    
    def get_report(self, report_id: int) -> Dict:
        """Get specific report with findings."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, log_file, analysis_type, risk_level, status, created_at, findings_count
            FROM reports WHERE id = ?
        ''', (report_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        report = dict(zip(['id', 'log_file', 'analysis_type', 'risk_level', 'status', 'created_at', 'findings_count'], row))
        
        cursor.execute('SELECT * FROM findings WHERE report_id = ?', (report_id,))
        findings = cursor.fetchall()
        conn.close()
        
        report['findings'] = [dict(zip(['id', 'analysis_type', 'finding_type', 'severity', 'title', 'description', 'evidence', 'recommended_action', 'report_id', 'timestamp'], f)) for f in findings]
        
        return report


# ============================================================================
# Agent Manager - Simulated Agent Delegation
# ============================================================================

class AgentManager:
    """Manages analysis agent delegation."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def analyze_security(self, log_file: str, content: str, report_id: int) -> List[Finding]:
        """Delegate security analysis (simulated agent call)."""
        findings = []
        
        if 'brute force' in content.lower() or 'failed login' in content.lower():
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='SECURITY',
                finding_type='BruteForceAttack',
                severity='CRITICAL',
                title='Brute Force Attack Detected',
                description='Multiple failed login attempts from suspicious IP',
                evidence='15+ failures in 60 seconds',
                recommended_action='Block source IP, enforce MFA',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        if 'unauthorized access' in content.lower() or 'privilege escalation' in content.lower():
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='SECURITY',
                finding_type='PrivilegeEscalation',
                severity='CRITICAL',
                title='Privilege Escalation Attempt',
                description='User attempted to access resources beyond privilege level',
                evidence='ROOT level access by USER account',
                recommended_action='Revoke sessions, force password reset',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        if 'aws' in content.lower() or 'credentials' in content.lower():
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='SECURITY',
                finding_type='CredentialExposure',
                severity='CRITICAL',
                title='Sensitive Credentials Exposed',
                description='AWS keys, passwords, or tokens found in logs',
                evidence='AKIA key prefix detected',
                recommended_action='Rotate credentials immediately',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        if 'error' in content.lower() or 'failed' in content.lower():
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='SECURITY',
                finding_type='HighErrorRate',
                severity='HIGH',
                title='Elevated Error Rate',
                description='Unusual number of errors detected in logs',
                evidence='Multiple ERROR entries',
                recommended_action='Investigate error causes',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        return findings
    
    def analyze_data_quality(self, log_file: str, content: str, report_id: int) -> List[Finding]:
        """Delegate data quality analysis (simulated agent call)."""
        findings = []
        
        lines = content.split('\n')
        iso_count = sum(1 for line in lines if 'T' in line and 'Z' in line)
        
        if iso_count < len(lines) * 0.8:
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='DATA_QUALITY',
                finding_type='MissingTimestamps',
                severity='MEDIUM',
                title='Incomplete ISO 8601 Timestamps',
                description='Not all log entries have proper timestamps',
                evidence=f'{iso_count}/{len(lines)} entries with timestamps',
                recommended_action='Add ISO 8601 timestamps to all entries',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        trace_count = sum(1 for line in lines if 'trace_id' in line.lower())
        if trace_count == 0:
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='DATA_QUALITY',
                finding_type='MissingTraceIds',
                severity='HIGH',
                title='No Distributed Tracing Support',
                description='Log entries lack trace_id for correlation',
                evidence='0 entries with trace_id',
                recommended_action='Implement distributed tracing',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        return findings
    
    def analyze_performance(self, log_file: str, content: str, report_id: int) -> List[Finding]:
        """Delegate performance analysis (simulated agent call)."""
        findings = []
        
        error_count = content.count('[ERROR]') + content.count('[CRITICAL]')
        
        if error_count > 5:
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='PERFORMANCE',
                finding_type='HighErrorRate',
                severity='HIGH',
                title='High Error Rate Detected',
                description=f'{error_count} error events found',
                evidence=f'{error_count} ERROR/CRITICAL entries',
                recommended_action='Investigate performance bottlenecks',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        if 'timeout' in content.lower():
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='PERFORMANCE',
                finding_type='ServiceTimeouts',
                severity='HIGH',
                title='Service Timeout Detected',
                description='Services timing out, indicating performance degradation',
                evidence='Timeout entries in logs',
                recommended_action='Optimize services or increase timeouts',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        critical_count = content.count('[CRITICAL]')
        if critical_count >= 2:
            findings.append(Finding(
                id=len(findings) + 1,
                analysis_type='PERFORMANCE',
                finding_type='CascadingFailure',
                severity='CRITICAL',
                title='Cascading Infrastructure Failure',
                description='Multiple critical events detected',
                evidence=f'{critical_count} CRITICAL events',
                recommended_action='Activate incident response',
                report_id=report_id,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        return findings


# ============================================================================
# File Watcher
# ============================================================================

class FileWatcher:
    """Watches for new/modified log files."""
    
    def __init__(self, watch_dir: Path, callback):
        self.watch_dir = watch_dir
        self.callback = callback
        self.snapshots: Dict[str, str] = {}
    
    def check_changes(self) -> List[Tuple[str, str]]:
        """Check for file changes."""
        changed = []
        current_files = set()
        
        for log_file in self.watch_dir.glob('*.log'):
            current_files.add(str(log_file))
            
            try:
                with open(log_file, 'r', errors='ignore') as f:
                    content = f.read()
                
                file_hash = hashlib.sha256(content.encode()).hexdigest()
                file_str = str(log_file)
                
                if file_str not in self.snapshots:
                    changed.append((file_str, 'NEW'))
                    self.snapshots[file_str] = file_hash
                elif self.snapshots[file_str] != file_hash:
                    changed.append((file_str, 'MODIFIED'))
                    self.snapshots[file_str] = file_hash
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
        
        # Check for deleted files
        deleted = set(self.snapshots.keys()) - current_files
        for deleted_file in deleted:
            changed.append((deleted_file, 'DELETED'))
            del self.snapshots[deleted_file]
        
        return changed


# ============================================================================
# HTTP Request Handler
# ============================================================================

class SecurityMonitorHandler(BaseHTTPRequestHandler):
    """HTTP request handler for security monitoring dashboard."""
    
    # Class variables (shared across all instances)
    db: DatabaseManager = None
    agent_manager: AgentManager = None
    watcher: FileWatcher = None
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_GET(self):
        """Handle GET requests."""
        path = unquote(self.path.split('?')[0])
        
        # Public routes
        if path == '/':
            self.serve_login_page()
        elif path == '/login':
            self.serve_login_page()
        elif path == '/api/status':
            self.api_status()
        # Protected routes
        elif path == '/dashboard':
            self.serve_dashboard()
        elif path == '/api/reports':
            self.api_reports()
        elif path == '/api/report':
            self.api_report_detail()
        elif path == '/api/synthesis':
            self.api_synthesis_report()
        elif path == '/api/synthesis/html':
            self.api_synthesis_html()
        elif path == '/api/refresh':
            self.api_refresh()
        elif path == '/logout':
            self.api_logout()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        path = self.path.split('?')[0]
        
        if path == '/api/login':
            self.api_login(body)
        elif path == '/api/upload':
            self.api_upload(body)
        else:
            self.send_error(404)
    
    def serve_login_page(self):
        """Serve login page."""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Monitor - Login</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                .login-container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
                h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
                .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
                input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; transition: border-color 0.3s; }
                input:focus { outline: none; border-color: #667eea; }
                button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 5px; font-size: 14px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
                button:hover { transform: translateY(-2px); }
                .demo-creds { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #666; }
                .demo-creds strong { display: block; color: #333; margin-bottom: 5px; }
                .error { color: #e74c3c; margin-bottom: 15px; padding: 10px; background: #fadbd8; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🔒 Security Monitor</h1>
                <p class="subtitle">Multi-Agent Log Analysis Platform</p>
                <form onsubmit="handleLogin(event); return false;">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" id="username" required autofocus>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="password" required>
                    </div>
                    <button type="submit">Login</button>
                    <div class="demo-creds">
                        <strong>Demo Credentials:</strong>
                        Username: admin<br>
                        Password: admin123
                    </div>
                </form>
            </div>
            <script>
                async function handleLogin(e) {
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username, password})
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        document.cookie = `session_id=${data.session_id}; path=/; max-age=86400`;
                        window.location.href = '/dashboard';
                    } else {
                        alert('Login failed: ' + data.message);
                    }
                }
            </script>
        </body>
        </html>
        '''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_dashboard(self):
        """Serve main dashboard."""
        if not self.check_auth():
            self.redirect('/login')
            return
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Monitor - Dashboard</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
                .header h1 { font-size: 24px; }
                .header a { color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 5px; cursor: pointer; }
                .header-btn { color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 5px; cursor: pointer; border: none; font-size: 14px; font-weight: 600; transition: all 0.3s; }
                .header-btn:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
                .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
                .section { background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
                h2 { margin-bottom: 20px; color: #333; }
                .upload-area { border: 2px dashed #667eea; border-radius: 8px; padding: 30px; text-align: center; cursor: pointer; transition: all 0.3s; }
                .upload-area:hover { border-color: #764ba2; background: #f9f9ff; }
                .upload-area input { display: none; }
                .button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: 600; }
                .button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
                table { width: 100%; border-collapse: collapse; }
                th { background: #f5f5f5; padding: 15px; text-align: left; font-weight: 600; color: #333; border-bottom: 2px solid #ddd; }
                td { padding: 15px; border-bottom: 1px solid #eee; }
                tr:hover { background: #f9f9f9; }
                .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
                .badge.critical { background: #e74c3c; color: white; }
                .badge.high { background: #f39c12; color: white; }
                .badge.medium { background: #f1c40f; color: #333; }
                .badge.low { background: #27ae60; color: white; }
                .refresh-btn { float: right; }
                .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
                .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
                .stat-number { font-size: 32px; font-weight: bold; }
                .stat-label { font-size: 12px; opacity: 0.9; margin-top: 10px; }
                .tab-btn { background: #f5f5f5; border: none; padding: 12px 24px; margin-right: 10px; cursor: pointer; border-bottom: 3px solid transparent; font-weight: 600; color: #666; transition: all 0.3s; }
                .tab-btn:hover { background: #e8e8e8; }
                .tab-btn.active { border-bottom-color: #667eea; color: #667eea; background: white; }
                .tab-content { display: none; }
                .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
                .metric-box { background: #f9f9f9; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
                .metric-value { font-size: 28px; font-weight: bold; color: #667eea; }
                .metric-label { font-size: 12px; color: #666; margin-top: 5px; text-transform: uppercase; }
                .chart-container { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .chart-title { font-weight: 600; color: #333; margin-bottom: 15px; }
                .chart-bars { display: flex; align-items: flex-end; gap: 15px; height: 200px; }
                .bar-group { display: flex; flex-direction: column; align-items: center; flex: 1; }
                .bar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px 4px 0 0; min-width: 40px; transition: all 0.3s; }
                .bar:hover { filter: brightness(1.1); }
                .bar-label { font-size: 12px; color: #666; margin-top: 10px; font-weight: 500; }
                .bar-value { font-size: 14px; font-weight: bold; color: #333; margin-top: 5px; }
                .synthesis-summary { background: white; border-left: 4px solid #667eea; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .synthesis-summary h3 { color: #333; margin-bottom: 10px; }
                .synthesis-summary p { color: #666; line-height: 1.6; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 Security Monitor Dashboard</h1>
                <div style="display: flex; gap: 10px;">
                    <button class="header-btn" onclick="refreshSystem()" title="Clear all analysis and start fresh">🔄 Refresh</button>
                    <a class="header-btn" onclick="logout()">Logout</a>
                </div>
            </div>
            <div class="container">
                <div class="stats" id="stats"></div>
                
                <div style="margin-bottom: 20px; border-bottom: 2px solid #ddd;">
                    <button class="tab-btn active" onclick="showTab('reports')">📋 Reports</button>
                    <button class="tab-btn" onclick="showTab('synthesis')">📊 Synthesis Report</button>
                </div>
                
                <div id="reports-tab" class="tab-content" style="display: block;">
                    <div class="section">
                        <h2>📤 Upload Log File</h2>
                        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                            <p>Click to upload log file or drag and drop</p>
                            <small>Supported: .log files</small>
                            <input type="file" id="fileInput" accept=".log" onchange="handleFileUpload(event)">
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>📋 Recent Analysis Reports</h2>
                        <button class="button refresh-btn" onclick="loadReports()">🔄 Refresh</button>
                        <table>
                            <thead>
                                <tr>
                                    <th>Log File</th>
                                    <th>Analysis Type</th>
                                    <th>Risk Level</th>
                                    <th>Status</th>
                                    <th>Findings</th>
                                    <th>Created</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="reports"></tbody>
                        </table>
                    </div>
                </div>
                
                <div id="synthesis-tab" class="tab-content" style="display: none;">
                    <div class="section">
                        <h2>📊 Synthesis Report</h2>
                        <button class="button refresh-btn" onclick="loadSynthesisReport()">🔄 Refresh</button>
                        <button class="button" onclick="downloadSynthesisReport()" style="float: right; margin-right: 10px;">⬇️ Download HTML</button>
                        
                        <div id="synthesis-metrics" style="margin-top: 20px;"></div>
                        <div id="synthesis-content" style="margin-top: 30px;"></div>
                    </div>
                </div>
            </div>
            
            <script>
                function checkAuth() {
                    fetch('/api/status').then(r => r.json()).then(d => {
                        if (!d.authenticated) window.location.href = '/login';
                    });
                }
                
                function showTab(tabName) {
                    // Hide all tabs
                    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
                    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                    
                    // Show selected tab
                    const tab = document.getElementById(tabName + '-tab');
                    if (tab) {
                        tab.style.display = 'block';
                    }
                    
                    // Set active button
                    event.target.classList.add('active');
                    
                    // Load synthesis report when tab is shown
                    if (tabName === 'synthesis') {
                        loadSynthesisReport();
                    }
                }
                
                function loadReports() {
                    fetch('/api/reports').then(r => r.json()).then(data => {
                        const tbody = document.getElementById('reports');
                        tbody.innerHTML = '';
                        
                        if (!data.reports || data.reports.length === 0) {
                            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">No reports yet</td></tr>';
                            return;
                        }
                        
                        data.reports.forEach(r => {
                            const riskBadge = `<span class="badge ${r.risk_level.toLowerCase()}">${r.risk_level}</span>`;
                            const row = `
                                <tr>
                                    <td>${r.log_file.split('/').pop()}</td>
                                    <td>${r.analysis_type}</td>
                                    <td>${riskBadge}</td>
                                    <td>${r.status}</td>
                                    <td>${r.findings_count}</td>
                                    <td>${new Date(r.created_at).toLocaleString()}</td>
                                    <td><a href="javascript:viewReport(${r.id})" style="color: #667eea; cursor: pointer;">View</a></td>
                                </tr>
                            `;
                            tbody.innerHTML += row;
                        });
                        
                        updateStats(data.stats);
                    });
                }
                
                function updateStats(stats) {
                    const html = `
                        <div class="stat-card">
                            <div class="stat-number">${stats.total_reports}</div>
                            <div class="stat-label">Total Reports</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" style="color: #e74c3c;">${stats.critical_findings}</div>
                            <div class="stat-label">Critical Findings</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" style="color: #f39c12;">${stats.high_findings}</div>
                            <div class="stat-label">High Priority</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" style="color: #27ae60;">${stats.analyses_run}</div>
                            <div class="stat-label">Analyses Run</div>
                        </div>
                    `;
                    document.getElementById('stats').innerHTML = html;
                }
                
                function loadSynthesisReport() {
                    fetch('/api/synthesis').then(r => r.json()).then(data => {
                        if (data.error) {
                            document.getElementById('synthesis-content').innerHTML = `<p style="color: #e74c3c;">Error loading synthesis report: ${data.error}</p>`;
                            return;
                        }
                        
                        // Render metrics
                        const metrics = data.metrics || {};
                        const metricsHtml = `
                            <div class="metrics-grid">
                                <div class="metric-box">
                                    <div class="metric-value">${metrics.total_findings || 0}</div>
                                    <div class="metric-label">Total Findings</div>
                                </div>
                                <div class="metric-box" style="border-left-color: #e74c3c;">
                                    <div class="metric-value" style="color: #e74c3c;">${metrics.severity_breakdown?.CRITICAL || 0}</div>
                                    <div class="metric-label">Critical</div>
                                </div>
                                <div class="metric-box" style="border-left-color: #f39c12;">
                                    <div class="metric-value" style="color: #f39c12;">${metrics.severity_breakdown?.HIGH || 0}</div>
                                    <div class="metric-label">High</div>
                                </div>
                                <div class="metric-box" style="border-left-color: #27ae60;">
                                    <div class="metric-value" style="color: #27ae60;">${metrics.severity_breakdown?.MEDIUM || 0}</div>
                                    <div class="metric-label">Medium</div>
                                </div>
                            </div>
                        `;
                        document.getElementById('synthesis-metrics').innerHTML = metricsHtml;
                        
                        // Render severity distribution chart
                        let chartHtml = `
                            <div class="chart-container">
                                <div class="chart-title">📊 Severity Distribution</div>
                                <div class="chart-bars" id="severity-chart"></div>
                            </div>
                        `;
                        
                        // Add summary text
                        if (data.summary) {
                            chartHtml += `
                                <div class="synthesis-summary">
                                    <h3>📝 Summary</h3>
                                    <p>${data.summary}</p>
                                </div>
                            `;
                        }
                        
                        document.getElementById('synthesis-content').innerHTML = chartHtml;
                        
                        // Render severity chart
                        setTimeout(() => {
                            generateSeverityChart(metrics.severity_breakdown || {});
                        }, 100);
                    }).catch(e => {
                        document.getElementById('synthesis-content').innerHTML = `<p style="color: #e74c3c;">Failed to load synthesis report: ${e.message}</p>`;
                    });
                }
                
                function generateSeverityChart(breakdown) {
                    const severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
                    const colors = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60'];
                    const maxValue = Math.max(...severities.map(s => breakdown[s] || 0), 1);
                    
                    const chart = document.getElementById('severity-chart');
                    if (!chart) return;
                    
                    chart.innerHTML = '';
                    severities.forEach((severity, idx) => {
                        const count = breakdown[severity] || 0;
                        const height = (count / maxValue) * 150;
                        
                        const barHtml = `
                            <div class="bar-group">
                                <div class="bar" style="background: linear-gradient(135deg, ${colors[idx]} 0%, ${colors[idx]}dd 100%); height: ${height}px;" title="${count} findings"></div>
                                <div class="bar-label">${severity}</div>
                                <div class="bar-value">${count}</div>
                            </div>
                        `;
                        chart.innerHTML += barHtml;
                    });
                }
                
                function downloadSynthesisReport() {
                    fetch('/api/synthesis/html').then(r => {
                        if (r.ok) {
                            r.blob().then(blob => {
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = 'security_synthesis_report.html';
                                document.body.appendChild(a);
                                a.click();
                                window.URL.revokeObjectURL(url);
                                document.body.removeChild(a);
                            });
                        } else {
                            alert('Failed to download report');
                        }
                    }).catch(e => alert('Error downloading report: ' + e.message));
                }
                
                async function handleFileUpload(e) {
                    const file = e.target.files[0];
                    if (!file) return;
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    alert(data.message || 'File uploaded successfully');
                    loadReports();
                }
                
                function viewReport(reportId) {
                    fetch(`/api/report?id=${reportId}`).then(r => r.json()).then(data => {
                        let html = `<h3>${data.log_file}</h3>`;
                        html += `<p>Risk Level: <span class="badge ${data.risk_level.toLowerCase()}">${data.risk_level}</span></p>`;
                        html += '<ul>';
                        data.findings.forEach(f => {
                            html += `<li><strong>${f.title}</strong> (${f.severity})<br><small>${f.description}</small></li>`;
                        });
                        html += '</ul>';
                        alert(html);
                    });
                }
                
                function logout() {
                    fetch('/logout').then(() => {
                        document.cookie = 'session_id=; max-age=0';
                        window.location.href = '/login';
                    });
                }
                
                function refreshSystem() {
                    if (!confirm('Are you sure you want to clear all analysis data and start fresh? This cannot be undone.')) {
                        return;
                    }
                    
                    fetch('/api/refresh', {method: 'GET'}).then(r => r.json()).then(data => {
                        if (data.success) {
                            alert('System reset complete. All reports and findings cleared.');
                            location.reload();
                        } else {
                            alert('Error: ' + (data.error || 'Unknown error'));
                        }
                    }).catch(e => alert('Error refreshing system: ' + e.message));
                }
                
                checkAuth();
                loadReports();
                setInterval(loadReports, 5000);
            </script>
        </body>
        </html>
        '''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def api_login(self, body):
        """Handle login request."""
        try:
            data = json.loads(body)
            user = self.db.authenticate(data.get('username'), data.get('password'))
            
            if not user:
                self.send_json({'success': False, 'message': 'Invalid credentials'}, 401)
                return
            
            session_id = self.db.create_session(user.id)
            self.db.log_event('INFO', 'AUTH', f'User {user.username} logged in', {'user_id': user.id})
            
            self.send_json({'success': True, 'session_id': session_id})
        except Exception as e:
            self.send_json({'success': False, 'message': str(e)}, 500)
    
    def api_status(self):
        """Check authentication status."""
        session_id = self.get_session_id()
        session = self.db.get_session(session_id) if session_id else None
        self.send_json({'authenticated': session is not None})
    
    def api_logout(self):
        """Handle logout."""
        self.redirect('/login')
    
    def api_refresh(self):
        """Clear all analysis data and reset system."""
        if not self.check_auth():
            self.send_json({'error': 'Unauthorized'}, 401)
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Clear reports and findings (keep users and sessions)
            cursor.execute('DELETE FROM findings')
            cursor.execute('DELETE FROM reports')
            cursor.execute('DELETE FROM logs')
            
            conn.commit()
            conn.close()
            
            # Clear uploaded log files
            for log_file in LOGS_DIR.glob('*.log'):
                try:
                    log_file.unlink()
                except:
                    pass
            
            self.db.log_event('INFO', 'SYSTEM', 'System reset - all analysis cleared', {})
            
            self.send_json({
                'success': True,
                'message': 'System reset complete. All reports and findings cleared.',
                'reports_cleared': True,
                'logs_cleared': True
            })
        
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def api_reports(self):
        """Get reports list."""
        if not self.check_auth():
            self.send_json({'error': 'Unauthorized'}, 401)
            return
        
        reports = self.db.get_reports()
        
        # Calculate stats
        critical_count = sum(1 for r in reports if r['risk_level'] == 'CRITICAL')
        high_count = sum(1 for r in reports if r['risk_level'] == 'HIGH')
        
        self.send_json({
            'reports': reports,
            'stats': {
                'total_reports': len(reports),
                'critical_findings': critical_count,
                'high_findings': high_count,
                'analyses_run': len(reports),
            }
        })
    
    def api_report_detail(self):
        """Get single report details."""
        if not self.check_auth():
            self.send_json({'error': 'Unauthorized'}, 401)
            return
        
        report_id = int(self.get_param('id') or 0)
        report = self.db.get_report(report_id)
        
        if not report:
            self.send_json({'error': 'Not found'}, 404)
            return
        
        self.send_json(report)
    
    def api_synthesis_report(self):
        """Get synthesis report with charts (JSON)."""
        if not self.check_auth():
            self.send_json({'error': 'Unauthorized'}, 401)
            return
        
        try:
            # Get recent report IDs
            reports = self.db.get_reports(limit=20)
            report_ids = [r['id'] for r in reports]
            
            if not report_ids:
                self.send_json({'error': 'No reports found'}, 404)
                return
            
            # Use synthesis agent (if available)
            try:
                from synthesis_agent import SynthesisAgent
                synthesis = SynthesisAgent(str(DB_PATH))
                result = synthesis.synthesize_reports(report_ids)
                
                self.send_json({
                    'success': True,
                    'summary': result['summary'],
                    'metrics': result['metrics'],
                    'charts_ascii': result['charts_ascii'],
                    'findings_count': result['findings_count'],
                    'timestamp': result['timestamp']
                })
            except ImportError:
                # Fallback if synthesis agent not available
                all_findings = []
                for report_id in report_ids:
                    report = self.db.get_report(report_id)
                    all_findings.extend(report.get('findings', []))
                
                severity_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                for finding in all_findings:
                    severity = finding.get('severity', 'UNKNOWN')
                    if severity in severity_count:
                        severity_count[severity] += 1
                
                self.send_json({
                    'success': True,
                    'metrics': {
                        'total_findings': len(all_findings),
                        'severity_breakdown': severity_count
                    }
                })
        
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def api_synthesis_html(self):
        """Get synthesis report as HTML (downloadable)."""
        if not self.check_auth():
            self.send_error(401)
            return
        
        try:
            from synthesis_agent import SynthesisAgent, HtmlReportGenerator
            
            # Get recent report IDs
            reports = self.db.get_reports(limit=20)
            report_ids = [r['id'] for r in reports]
            
            if not report_ids:
                self.send_error(404)
                return
            
            # Generate synthesis
            synthesis = SynthesisAgent(str(DB_PATH))
            result = synthesis.synthesize_reports(report_ids)
            
            # Send HTML report
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="security_report.html"')
            self.end_headers()
            self.wfile.write(result['html_report'].encode('utf-8'))
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def api_upload(self, body):
        """Handle file upload."""
        if not self.check_auth():
            self.send_json({'error': 'Unauthorized'}, 401)
            return
        
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_json({'error': 'Invalid content type'}, 400)
                return
            
            # Extract file from body
            boundary = content_type.split('boundary=')[1].encode()
            parts = body.split(f'--{boundary.decode()}')
            
            content = None
            filename = None
            
            for part in parts:
                if 'filename=' in part:
                    lines = part.split('\r\n')
                    for line in lines:
                        if 'filename=' in line:
                            filename = line.split('filename="')[1].split('"')[0]
                    
                    # Get file content
                    for i, line in enumerate(lines):
                        if line == '':
                            content = '\r\n'.join(lines[i+1:-1])
                            break
            
            if not filename or not content:
                self.send_json({'error': 'No file uploaded'}, 400)
                return
            
            # Save uploaded file
            log_path = LOGS_DIR / filename
            with open(log_path, 'w') as f:
                f.write(content)
            
            # Create analysis reports
            report_ids = []
            
            for analysis_type in ['DATA_QUALITY', 'SECURITY', 'PERFORMANCE']:
                report_id = self.db.create_report(str(log_path), analysis_type)
                report_ids.append(report_id)
                
                # Run analysis
                if analysis_type == 'SECURITY':
                    findings = self.agent_manager.analyze_security(str(log_path), content, report_id)
                elif analysis_type == 'DATA_QUALITY':
                    findings = self.agent_manager.analyze_data_quality(str(log_path), content, report_id)
                else:  # PERFORMANCE
                    findings = self.agent_manager.analyze_performance(str(log_path), content, report_id)
                
                # Save findings
                for finding in findings:
                    self.db.add_finding(report_id, finding)
                
                # Update report status
                conn = self.db.get_connection()
                cursor = conn.cursor()
                risk_level = max([f.severity for f in findings]) if findings else 'LOW'
                cursor.execute('''
                    UPDATE reports SET status = 'COMPLETED', risk_level = ?, findings_count = ?
                    WHERE id = ?
                ''', (risk_level, len(findings), report_id))
                conn.commit()
                conn.close()
            
            self.db.log_event('INFO', 'UPLOAD', f'Log file uploaded: {filename}', {'filename': filename, 'analyses': 3})
            
            self.send_json({'success': True, 'message': f'Analyzed {filename} with 3 agent perspectives', 'report_ids': report_ids})
        
        except Exception as e:
            self.db.log_event('ERROR', 'UPLOAD', f'Upload failed: {str(e)}', {'error': str(e)})
            self.send_json({'error': str(e)}, 500)
    
    def check_auth(self) -> bool:
        """Check if user is authenticated."""
        session_id = self.get_session_id()
        if not session_id:
            return False
        session = self.db.get_session(session_id)
        return session is not None
    
    def get_session_id(self) -> Optional[str]:
        """Get session ID from cookies."""
        cookies = self.headers.get('Cookie', '')
        for cookie in cookies.split(';'):
            if 'session_id=' in cookie:
                return cookie.split('session_id=')[1].strip()
        return None
    
    def get_param(self, name: str) -> Optional[str]:
        """Get URL parameter."""
        params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        return params.get(name, [None])[0]
    
    def send_json(self, data: Dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def redirect(self, path: str):
        """Redirect to another path."""
        self.send_response(302)
        self.send_header('Location', path)
        self.end_headers()


def run_server():
    """Start HTTP server."""
    handler = SecurityMonitorHandler
    handler.db = DatabaseManager(DB_PATH)
    handler.agent_manager = AgentManager(handler.db)
    handler.watcher = FileWatcher(WATCH_DIR, lambda x, y, z: None)
    
    server = HTTPServer((HOST, PORT), handler)
    
    print("\n" + "="*70)
    print("Security Monitor - Multi-Agent Analysis Platform")
    print("="*70)
    print(f"Server running on http://{HOST}:{PORT}")
    print(f"Database: {DB_PATH}")
    print(f"Watch directory: {WATCH_DIR}")
    print(f"Reports directory: {REPORTS_DIR}")
    print(f"\nDemo Credentials:")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"\nFeatures:")
    print(f"   * Multi-agent log analysis (Data Quality, Security, Performance)")
    print(f"   * User authentication with sessions")
    print(f"   * Real-time file monitoring")
    print(f"   * Automated finding detection")
    print(f"   * Report generation and storage")
    print("="*70 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.server_close()


if __name__ == '__main__':
    run_server()
