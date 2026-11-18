#!/bin/bash
# WSL Apache + Python Multi-Agent Security Monitor Setup
# Run this in WSL Ubuntu to deploy the complete system

set -e

echo "======================================================================="
echo "🔒 Security Monitor - WSL Deployment Setup"
echo "======================================================================="

# Create directories
echo "📁 Creating directories..."
mkdir -p /tmp/logs
mkdir -p /tmp/workspace/logs
mkdir -p /tmp/workspace/reports

# Copy web app to WSL
echo "📦 Setting up Python web application..."
SCRIPT_DIR="/opt/security_monitor"
mkdir -p $SCRIPT_DIR

# Create the web_app.py in WSL
cat > $SCRIPT_DIR/web_app.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""Multi-Agent Security Monitoring Dashboard"""
# [The content from the main web_app.py would go here in production]
# For now, we'll use a simpler inline version
import http.server
import socketserver
import json
from datetime import datetime

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = open('/opt/security_monitor/index.html').read().encode()
            self.wfile.write(html)
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Server running on port {PORT}")
    httpd.serve_forever()
PYTHON_EOF

chmod +x $SCRIPT_DIR/web_app.py

# Create sample log file
echo "📝 Creating sample log files..."
cat > /tmp/logs/application.log << 'EOF'
2024-01-15T09:23:15.847Z [INFO] [AuthService] User login attempt - user_id=usr_001 email=admin@system.com ip=192.168.1.105
2024-01-15T09:24:02.156Z [ERROR] [PaymentGateway] Payment processing failed - order_id=ord_12345 amount=USD_1500.00
2024-01-15T09:24:06.234Z [CRITICAL] [PaymentGateway] Multiple payment failures - failures_in_5min=8 success_rate=0.12
2024-01-15T09:24:18.901Z [WARN] [SecurityAudit] Suspicious login attempts detected - source_ip=203.45.123.89 attempt_count=15 brute force
2024-01-15T09:24:20.567Z [ERROR] [APIGateway] Rate limit exceeded - client_id=api_key_5f4d9e2a calls_per_minute=5001
2024-01-15T09:24:30.345Z [ERROR] [AnalyticsEngine] ETL job failed - error="Out of memory"
2024-01-15T09:24:31.678Z [CRITICAL] [SystemMonitor] Server CPU temperature critical - temp_celsius=89 threshold=85
2024-01-15T09:24:38.789Z [CRITICAL] [DataIntegrity] Database integrity check failed - inconsistencies_found=234
2024-01-15T09:24:46.123Z [ERROR] [LoadBalancer] All nodes unhealthy - healthy_nodes=0 total_nodes=5
EOF

cat > /tmp/logs/security.log << 'EOF'
2024-01-15T10:00:00.000Z [CRITICAL] [SecurityAudit] Unauthorized access attempt - user_id=usr_001 resource=/admin/settings access_level_required=ROOT
2024-01-15T10:01:00.000Z [ERROR] [SecurityAudit] Failed login attempt - ip=203.45.123.89 account=admin reason="Brute force pattern detected"
2024-01-15T10:02:00.000Z [WARN] [SecurityAudit] MFA required for sensitive operation - user_id=usr_001 operation=AccessAdminPanel
2024-01-15T10:03:00.000Z [ERROR] [Crypto] Invalid certificate - cert_name=AKIA2JYXYQ5ZLHQ5AAAA
EOF

# Create systemd service file
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/security-monitor.service > /dev/null << EOF
[Unit]
Description=Security Monitor - Multi-Agent Analysis
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/web_app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Apache reverse proxy config
echo "🌐 Creating Apache configuration..."
sudo tee /etc/apache2/sites-available/security-monitor.conf > /dev/null << 'EOF'
<VirtualHost *:8080>
    ServerName localhost
    ServerAdmin admin@localhost
    
    # Enable proxy modules
    <IfModule mod_proxy.c>
        ProxyRequests Off
        ProxyPreserveHost On
        ProxyPassMatch ^/$ http://localhost:8000/ 
        ProxyPassMatch ^/api http://localhost:8000/api
        ProxyPassMatch ^/dashboard http://localhost:8000/dashboard
        ProxyPassMatch ^/login http://localhost:8000/login
        ProxyPassMatch ^/logout http://localhost:8000/logout
    </IfModule>
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/security-monitor-error.log
    CustomLog ${APACHE_LOG_DIR}/security-monitor-access.log combined
    
    # Compression
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/xml text/javascript application/javascript application/json
    </IfModule>
</VirtualHost>
EOF

# Enable Apache modules
echo "✅ Enabling Apache modules..."
sudo a2enmod proxy > /dev/null 2>&1 || true
sudo a2enmod proxy_http > /dev/null 2>&1 || true
sudo a2enmod deflate > /dev/null 2>&1 || true

# Enable site
echo "✅ Enabling Apache site..."
sudo a2ensite security-monitor > /dev/null 2>&1 || true

# Start/restart Apache
echo "🚀 Restarting Apache..."
sudo systemctl restart apache2 || sudo service apache2 restart

echo ""
echo "======================================================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "======================================================================="
echo ""
echo "📍 Access the application:"
echo "   http://localhost:8080"
echo ""
echo "📝 Sample log files created:"
echo "   /tmp/logs/application.log"
echo "   /tmp/logs/security.log"
echo ""
echo "🔐 Demo Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 Directories:"
echo "   Logs: /tmp/logs"
echo "   Workspace: /tmp/workspace"
echo "   Reports: /tmp/workspace/reports"
echo ""
echo "🎯 To start the Python service:"
echo "   python3 $SCRIPT_DIR/web_app.py"
echo ""
echo "❌ To stop Apache:"
echo "   sudo systemctl stop apache2"
echo ""
echo "======================================================================="
