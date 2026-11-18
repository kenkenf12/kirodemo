# Log Analyzer - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Step 1: Access the Login Page
```
https://your-username.github.io/agent_code_review/login.html
```

### Step 2: Login with Demo Credentials
```
Username: admin
Password: security123
```

### Step 3: Upload & Analyze
1. Drag your log file into the upload area (or click to browse)
2. Click "Analyze"
3. View results in the dashboard

---

## 📋 Demo Credentials

Use any of these to login:

| Username | Password |
|----------|----------|
| admin | security123 |
| analyst | analysis456 |
| reviewer | review789 |

---

## 📊 Understanding Your Analysis Results

### Stats Cards
- **Total Lines**: Number of log entries processed
- **Errors**: Lines containing error messages
- **Warnings**: Lines containing warning messages
- **Unique IPs**: Number of different IP addresses found

### Four Analysis Tabs

#### 1. Overview
General file statistics:
- File name and size
- Number of lines
- Error/warning/info/debug counts
- Analysis timestamp

#### 2. Security
Security findings detected:
- Authentication failures
- Unauthorized access
- Attack patterns (SQL injection, XSS)
- Access violations

Each finding shows:
- **Severity**: HIGH, MEDIUM, or LOW
- **Type**: Category of issue
- **Line**: Where it was found
- **Message**: Description

#### 3. Patterns
Common patterns found in your logs:
- Frequency of each pattern
- Pattern categories:
  - `error` - Error occurrences
  - `warning` - Warning occurrences
  - `failed` - Failed operations
  - `timeout` - Connection timeouts
  - `unauthorized` - Access denials
  - `success` - Successful operations

#### 4. Raw Data
Complete analysis in JSON format:
- Full statistics
- All detected security issues
- Complete pattern counts
- Metadata

---

## 🎯 Example Workflows

### Scenario 1: Analyze Application Logs
```
1. Login with: admin / security123
2. Drag your app.log file to upload area
3. Click Analyze
4. Check "Security" tab for issues
5. Review "Patterns" tab for trends
```

### Scenario 2: Review Web Server Logs
```
1. Login as: analyst
2. Upload nginx.log or apache.log
3. Check "Overview" for statistics
4. Export "Raw Data" for processing
5. Share dashboard link with team
```

### Scenario 3: Security Audit
```
1. Login as: reviewer
2. Upload security audit log
3. Navigate to "Security" tab
4. Document findings
5. Export JSON for report
```

---

## 🔍 What Gets Analyzed

### Log Level Counting
Automatically counts:
- ERROR and FATAL messages
- WARNING and WARN messages
- INFO messages
- DEBUG messages

### Security Detection
Automatically flags:
- Failed login attempts
- Authentication errors
- Unauthorized access
- SQL injection patterns
- XSS attack attempts
- Connection issues

### IP Extraction
Automatically extracts:
- All IPv4 addresses in logs
- Unique IP count
- IP frequency

---

## ⚡ Tips & Tricks

### Upload Multiple Files Sequentially
1. Upload and analyze first file
2. Review results
3. Click "← Back to Upload"
4. Upload next file
5. Repeat

### Copy Credentials Easily
On login page:
- Hover over credentials
- Click "copy" button
- Paste into login form

### Export Analysis Data
1. Go to "Raw Data" tab
2. Copy the JSON content
3. Save to file or share
4. Use for further processing

### Search Logs Locally
Use your browser's search (Ctrl+F or Cmd+F):
- In "Security" tab to find specific threat types
- In "Patterns" tab for pattern frequencies
- In "Raw Data" for specific values

---

## 🛠️ Troubleshooting

**Can't login?**
- Use exact credentials (case-sensitive)
- Try: `admin` / `security123`
- Check browser console for errors (F12)

**File won't upload?**
- Check file extension (.log or .txt only)
- Verify file size (max 50MB)
- Ensure file is readable text format

**Analysis not showing?**
- Try with sample-log.txt (provided in repo)
- Check browser console for errors
- Refresh page and try again

**Lost login session?**
- Reload page (you'll be redirected to login)
- Click "Logout" button in navbar
- Clear browser cache and login again

---

## 📁 File Support

**Supported Formats:**
- `.log` files
- `.txt` files

**File Size Limits:**
- Maximum: 50MB
- Recommended: < 10MB for faster analysis

**File Examples:**
- Application logs: `app.log`
- Web server logs: `apache.log`, `nginx.log`
- Security logs: `security.log`
- System logs: `syslog.txt`

---

## 🔐 Security & Privacy

**Important Notes:**
- ✅ All analysis happens in your browser
- ✅ No files are uploaded to servers
- ✅ No data is stored or shared
- ✅ Refresh clears all analysis from memory
- ✅ Demo credentials are for testing only

---

## 📞 Need Help?

1. **Read LOG_ANALYZER_SETUP.md** - Full documentation
2. **Check GitHub Issues** - Known problems and solutions
3. **Review sample-log.txt** - Example log format
4. **Check browser console** - Error messages (F12)

---

## 🎓 Learn More

- Main Dashboard: `index.html`
- Coverage Reports: `coverage/index.html`
- Analysis Reports: `analysis/report.html`

---

## 🚀 Ready?

**Start now:** https://your-username.github.io/agent_code_review/login.html

Use credentials:
- Username: **admin**
- Password: **security123**
