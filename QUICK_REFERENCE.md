# Quick Reference Card

## Launch System
```bash
cd c:\Users\kenke\agent_code_review
python web_app.py
```

## Access Dashboard
- **URL**: http://localhost:8000
- **Username**: admin
- **Password**: admin123

## Main Features

### Dashboard Tabs
| Tab | Purpose | Features |
|-----|---------|----------|
| Reports | Manage uploads | Upload files, view report list |
| Synthesis Report | View analysis | Metrics, charts, summary |

### Key Buttons
| Button | Location | Action |
|--------|----------|--------|
| Upload | Reports tab | Select .log file to analyze |
| Refresh | Reports tab | Reload report list |
| Refresh | Header | Clear all data & start fresh |
| Download | Synthesis tab | Export HTML report |
| Logout | Header | End session |

## Analysis Workflow

```
1. Click "Reports" tab
   ↓
2. Upload .log file
   ↓
3. Wait 2-3 seconds (3 agents analyze)
   ↓
4. Click "Synthesis Report" tab
   ↓
5. View metrics cards & charts
   ↓
6. Click "Download HTML" to save
   ↓
7. Click "Refresh" to start over
```

## API Endpoints

### Authentication
```
POST /api/login
{username: "admin", password: "admin123"}
```

### Data Operations
```
GET  /api/reports          - List reports
GET  /api/synthesis        - JSON synthesis
GET  /api/synthesis/html   - Download HTML
GET  /api/refresh          - Reset system
```

## Database Files
- **Location**: `C:\tmp\workspace\security_monitor.db`
- **Type**: SQLite
- **Tables**: users, sessions, reports, findings, logs

## Log Files
- **Location**: `C:\tmp\logs\`
- **Format**: .log files
- **Sample**: `test_security.log` (14 test findings)

## Common Commands

### Check if server running
```powershell
Get-Process python
```

### Stop server
```powershell
Get-Process python | Stop-Process -Force
```

### Restart server
```powershell
python web_app.py
```

### View database
```bash
# Clear all data
python
>>> import sqlite3
>>> conn = sqlite3.connect('C:\\tmp\\workspace\\security_monitor.db')
>>> cursor = conn.cursor()
>>> cursor.execute('SELECT COUNT(*) FROM reports')
>>> print(cursor.fetchone())
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F12 | Developer console (troubleshooting) |
| F5 | Refresh page |
| Ctrl+Shift+Del | Clear cache |

## Color Codes

| Color | Severity | Meaning |
|-------|----------|---------|
| 🔴 Red | CRITICAL | Immediate action required |
| 🟠 Orange | HIGH | High priority issue |
| 🟡 Yellow | MEDIUM | Medium priority |
| 🟢 Green | LOW | Low priority |

## Metrics Explained

| Metric | Definition |
|--------|-----------|
| Total Findings | Sum of all issues across agents |
| CRITICAL | Severe security/performance issues |
| HIGH | Important issues requiring attention |
| MEDIUM | Moderate issues worth addressing |
| Risk Level | Overall system risk (CRITICAL/HIGH/MEDIUM/LOW) |

## Troubleshooting

### Server won't start
- Kill existing process: `taskkill /PID <pid> /F`
- Verify port 8000 free: `netstat -ano \| findstr :8000`
- Restart: `python web_app.py`

### No data showing
- Upload log file first
- Wait 2-3 seconds for analysis
- Refresh page (F5)
- Check console (F12) for errors

### Charts blank
- Verify reports have findings
- Try different browser
- Clear cache (Ctrl+Shift+Del)
- Check JavaScript enabled

### Refresh stuck
- Wait 30 seconds
- Close and reopen browser
- Restart server

## File Structure

```
agent_code_review/
├── web_app.py                      Main application
├── synthesis_agent.py              Report generator
├── log_analyzer.py                 CLI analyzer
├── log_monitor.py                  File watcher
│
├── README.md                        Main guide
├── QUICK_START.md                  Getting started
├── QUICK_REFERENCE.md              This file
├── TESTING_GUIDE.md                Test procedures
├── FEATURES_COMPLETED.md           Feature list
├── PROJECT_SUMMARY.md              Project overview
│
└── database/
    └── security_monitor.db         SQLite database
```

## Performance Targets

| Operation | Target | Actual |
|-----------|--------|--------|
| Page load | <2s | ✓ Met |
| File upload | <3s | ✓ Met |
| Agent analysis | <1s | ✓ Met |
| Chart render | <100ms | ✓ Met |
| Synthesis | <500ms | ✓ Met |

## Demo Data

**File**: `C:\tmp\logs\test_security.log`

**Contains**:
- Brute force patterns
- Credential exposure
- Privilege escalation
- Service timeouts
- High error rates
- Cascading failures

**Results**:
- 14 total findings
- 6 CRITICAL
- 8 HIGH

## Reset System

1. Click 🔄 **Refresh** button
2. Click **OK** in confirmation
3. System clears all data
4. Page reloads
5. Ready for new analysis

## Get Help

1. Read `QUICK_START.md` (quick answers)
2. Check `TESTING_GUIDE.md` (how to use)
3. Review `README.md` (full docs)
4. Check browser console (F12)
5. Verify database exists

## System Status Indicators

| Status | Meaning |
|--------|---------|
| ✓ | Working normally |
| ⚠ | Warning (check console) |
| ✗ | Error (restart server) |
| 🔄 | Loading/Processing |

## Quick Test

```
1. Open http://localhost:8000
2. Login: admin/admin123
3. Click "Reports" tab
4. Upload test_security.log
5. Click "Synthesis Report" tab
6. See 14 findings, 6 CRITICAL
7. Click "Download HTML"
8. Save report
✓ System working!
```

## Support Resources

- **README.md**: Complete overview
- **QUICK_START.md**: Getting started
- **TESTING_GUIDE.md**: How to test
- **PROJECT_SUMMARY.md**: Technical details
- **FEATURES_COMPLETED.md**: What's included

---

**Keep this handy for quick reference!**
