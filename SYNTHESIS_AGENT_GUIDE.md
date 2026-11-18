# Synthesis Agent - Report Generation with Charts & Graphs

## 🎯 Overview

The **Synthesis Agent** aggregates findings from all three security agents and generates comprehensive reports with professional charts, graphs, and visualizations.

### Features

- ✅ Aggregates findings from Security, Quality, and Performance agents
- ✅ Calculates comprehensive metrics and statistics
- ✅ Generates ASCII charts for terminal display
- ✅ Generates SVG charts for web/PDF
- ✅ Creates professional HTML reports
- ✅ Produces executive summaries
- ✅ Prioritizes recommendations
- ✅ No external dependencies (pure Python)

---

## 📊 Reports Generated

### 1. ASCII Charts (Terminal Display)

```
Findings by Severity
==================================================================
CRITICAL         │ █████████████████████████████████████     │   18 ( 48.6%)
HIGH             │ ███████████████████████                   │   10 ( 27.0%)
MEDIUM           │ ████████████                              │    6 ( 16.2%)
LOW              │ ██                                        │    3 (  8.1%)
==================================================================

Findings by Agent
==================================================================
SECURITY         │ ██████████████████████████████            │   14 ( 37.8%)
QUALITY          │ ███████████████                           │    8 ( 21.6%)
PERFORMANCE      │ ███████████████                           │   15 ( 40.5%)
==================================================================
```

### 2. SVG Charts (HTML/Web)

- Bar charts with color-coded severity levels
- Pie charts showing distribution percentages
- Responsive design (mobile-friendly)
- Print-ready formatting
- Legend with exact counts

### 3. HTML Reports

Professional PDF-ready HTML reports featuring:
- Executive summary with key metrics
- Color-coded severity indicators
- Visual charts and graphs
- Detailed findings with evidence
- Prioritized action items
- Audit trail metadata
- Print-optimized styling

---

## 🔧 Usage

### Basic Usage

```python
from synthesis_agent import SynthesisAgent
from pathlib import Path

# Initialize agent
agent = SynthesisAgent('/tmp/workspace/security_monitor.db')

# Synthesize reports
result = agent.synthesize_reports([1, 2, 3])  # Report IDs

# Display summary
print(result['summary'])

# Display ASCII charts
print(result['charts_ascii'])

# Get HTML report
html = result['html_report']
```

### In Web Application

```python
# Via REST API
GET /api/synthesis              # JSON synthesis data with ASCII charts
GET /api/synthesis/html         # HTML report (downloadable)

# Example
curl http://localhost:8000/api/synthesis \
  -H "Cookie: session_id=YOUR_SESSION_ID"
```

### Save Reports to File

```python
from synthesis_agent import save_html_report, save_summary_text

# Save HTML report
save_html_report(result['html_report'], 
                 '/tmp/workspace/reports/report.html')

# Save text summary
save_summary_text(result['summary'],
                  '/tmp/workspace/reports/summary.txt')
```

---

## 📈 Report Components

### Executive Summary

```
╔════════════════════════════════════════════════════════════════╗
║         EXECUTIVE SUMMARY - MULTI-AGENT SYNTHESIS              ║
╚════════════════════════════════════════════════════════════════╝

OVERALL RISK LEVEL: CRITICAL

FINDINGS OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Findings: 37
• Critical Issues: 6 (16.2%)
• High Priority: 12 (32.4%)
• Medium Priority: 15 (40.5%)
• Low Priority: 4 (10.8%)
```

### Metrics Card

```json
{
  "total_findings": 37,
  "severity_breakdown": {
    "CRITICAL": 6,
    "HIGH": 12,
    "MEDIUM": 15,
    "LOW": 4
  },
  "severity_percentages": {
    "CRITICAL": 16.2,
    "HIGH": 32.4,
    "MEDIUM": 40.5,
    "LOW": 10.8
  },
  "agent_breakdown": {
    "SECURITY": 14,
    "QUALITY": 8,
    "PERFORMANCE": 15
  },
  "agents_used": ["SECURITY", "QUALITY", "PERFORMANCE"],
  "risk_assessment": "CRITICAL"
}
```

### Detailed Findings

Each finding includes:
- Title (descriptive heading)
- Type (threat category)
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Description (what it means)
- Evidence (from log file)
- Recommended Action (next steps)

### Prioritized Recommendations

```
ACTION ITEMS (Prioritized)

🔴 CRITICAL
1. Block source IP, enforce MFA (2 findings)
2. Rotate credentials immediately (1 finding)
3. Halt database writes, restore backup (1 finding)

🟠 HIGH
4. Add trace_id to all entries (3 findings)
5. Implement PII masking layer (2 findings)
6. Investigate error root causes (4 findings)

🟡 MEDIUM
7. Convert to structured JSON logging (2 findings)
8. Increase timeout thresholds (1 finding)
```

---

## 🎨 Chart Types

### Bar Chart (Horizontal)

```
████████████████████ Value 1 (50%)
████████████         Value 2 (30%)
████                 Value 3 (10%)
██                   Value 4 (5%)
██                   Value 5 (5%)
```

Features:
- Color-coded bars
- Percentage display
- Exact values shown
- Sorted by value (descending)
- Responsive width

### Pie Chart (Text)

```
Value 1  │ ●●●●●●●●●●●●●●●●●●●● │ 50.0% (20)
Value 2  │ ●●●●●●●●●●●●          │ 30.0% (12)
Value 3  │ ●●●●                  │ 15.0% (6)
Value 4  │ ●●                    │  5.0% (2)
```

Features:
- Circle symbols for visual representation
- Percentage and count display
- Easy to scan

### HTML SVG Charts

- Responsive design
- Color-coded by severity
- Legend with values
- Print-ready
- Interactive hover (future)

---

## 📋 HTML Report Structure

```
┌─────────────────────────────────────┐
│         HEADER (Gradient)           │
│  Title + Logo + Generation Date     │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│         METRICS CARDS               │
│  4 cards with key numbers           │
│  • Total Findings                   │
│  • Critical Count                   │
│  • High Priority Count              │
│  • Critical Percentage              │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│         CHARTS SECTION              │
│  • Severity Distribution Chart      │
│  • Agent Contribution Chart         │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│    EXECUTIVE SUMMARY                │
│  • Overview of findings             │
│  • Agent descriptions               │
│  • Key metrics recap                │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│    DETAILED FINDINGS                │
│  Grouped by severity:               │
│  • CRITICAL findings                │
│  • HIGH findings                    │
│  • MEDIUM findings                  │
│  • LOW findings                     │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│    ACTION ITEMS (Prioritized)       │
│  Sorted by severity & frequency     │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│    METADATA                         │
│  • Log file analyzed                │
│  • Report generation time           │
│  • Agents deployed                  │
│  • Total findings count             │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│         FOOTER                      │
│  Generated by Security Platform     │
└─────────────────────────────────────┘
```

---

## 🚀 Integration with Web App

### API Endpoints

#### 1. GET /api/synthesis
Returns synthesis report data in JSON format

```json
{
  "summary": "Executive summary text...",
  "metrics": { ... },
  "charts_ascii": "ASCII charts...",
  "findings_count": 37,
  "timestamp": "2026-11-17T12:30:45Z"
}
```

**Response:** JSON with text and ASCII charts

#### 2. GET /api/synthesis/html
Returns HTML report for download

```
Content-Type: text/html; charset=utf-8
Content-Disposition: attachment; filename="security_report.html"
```

**Response:** HTML file (downloadable as security_report.html)

### Dashboard Integration

In `web_app.py`:
```javascript
// Fetch synthesis report
async function loadSynthesisReport() {
  const response = await fetch('/api/synthesis');
  const data = await response.json();
  
  // Display metrics
  updateMetricsCards(data.metrics);
  
  // Display charts
  displayAsciiCharts(data.charts_ascii);
}

// Download HTML report
function downloadReport() {
  window.location.href = '/api/synthesis/html';
}
```

---

## 📊 Example Output

### Terminal ASCII Output

```
╔════════════════════════════════════════════════════════════════╗
║         EXECUTIVE SUMMARY - MULTI-AGENT SYNTHESIS              ║
╚════════════════════════════════════════════════════════════════╝

OVERALL RISK LEVEL: CRITICAL

FINDINGS OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Findings: 37
• Critical Issues: 6 (16.2%)
• High Priority: 12 (32.4%)
• Medium Priority: 15 (40.5%)
• Low Priority: 4 (10.8%)

Findings by Severity
==================================================================
CRITICAL         │ ███████████████████████████ │    6 ( 16.2%)
HIGH             │ ████████████████████████ │   12 ( 32.4%)
MEDIUM           │ ███████████████████████████ │   15 ( 40.5%)
LOW              │ ████               │    4 ( 10.8%)
==================================================================

Findings by Agent
==================================================================
SECURITY         │ ████████████████████████ │   14 ( 37.8%)
QUALITY          │ ███████████           │    8 ( 21.6%)
PERFORMANCE      │ ███████████████████████ │   15 ( 40.5%)
==================================================================
```

---

## 🔄 Data Flow

```
Database (SQLite)
    ├─ Reports (1, 2, 3, ...)
    └─ Findings (multiple per report)
         ↓
  Synthesis Agent
    ├─ Fetch all reports
    ├─ Aggregate findings
    ├─ Calculate metrics
    └─ Generate outputs
         ├─ Text summary
         ├─ ASCII charts
         ├─ SVG charts
         └─ HTML report
         ↓
Output Formats
    ├─ Console display (ASCII)
    ├─ JSON API response
    ├─ HTML download
    └─ Email/Slack (future)
```

---

## 💡 Use Cases

### 1. Executive Briefing
- Print HTML report
- Show metrics cards
- Display severity charts
- Highlight critical findings

### 2. Incident Response
- Generate synthesis immediately
- View prioritized actions
- Share report with team
- Export to compliance system

### 3. Compliance Audit
- Generate comprehensive report
- Preserve findings with timestamps
- Document agent analyses
- Archive for future reference

### 4. Trending Analysis
- Compare synthesis reports over time
- Track severity trends
- Monitor agent effectiveness
- Measure security improvements

---

## 🔐 Security Features

- ✅ Authentication required (session-based)
- ✅ Database isolation
- ✅ No external API calls
- ✅ Local chart generation (no external services)
- ✅ PDF-safe HTML (no JavaScript execution)
- ✅ Content-Security-Policy ready

---

## 📦 Dependencies

**None!** Synthesis agent uses only Python standard library:
- sqlite3 (database queries)
- dataclasses (data structures)
- datetime (timestamps)
- math (pie chart calculations)
- base64 (future image encoding)

---

## 🎯 Metrics Explained

### Severity Distribution
Shows count and percentage of findings by severity level:
- **CRITICAL:** Immediate action required
- **HIGH:** Action needed soon
- **MEDIUM:** Should be addressed
- **LOW:** Monitor for now

### Agent Contribution
Shows which agents detected most findings:
- Security Agent: Threat & compliance detection
- Quality Agent: Format & structure issues
- Performance Agent: Health & bottleneck issues

### Overall Risk Assessment
Calculated as:
- **CRITICAL:** Any CRITICAL findings present
- **HIGH:** More than 3 HIGH findings
- **MEDIUM:** Some HIGH findings (≤ 3)
- **LOW:** No CRITICAL or HIGH findings

---

## 🚀 Future Enhancements

- [ ] PDF export (via HTML)
- [ ] Email delivery of reports
- [ ] Scheduled report generation
- [ ] Slack integration
- [ ] Historical comparison charts
- [ ] Trend analysis over time
- [ ] Custom branding for reports
- [ ] Multi-language support
- [ ] Interactive dashboard with React
- [ ] Real-time metric updates

---

## 📞 Support

### Common Questions

**Q: How are metrics calculated?**
A: Metrics are aggregated from all findings:
- Total = sum of all findings
- Severity = grouped by CRITICAL/HIGH/MEDIUM/LOW
- Agents = grouped by agent type
- Risk = assessed based on severity distribution

**Q: Can I customize the reports?**
A: Yes! Modify:
- Colors in HtmlReportGenerator
- Chart types in AsciiCharts
- Summary text format
- Finding display order

**Q: What if there are no findings?**
A: System handles gracefully:
- Shows "No data" for empty categories
- Risk level = LOW
- Report still generates with empty sections

**Q: How often should I run synthesis?**
A: Recommended:
- After each security scan
- Daily for monitoring systems
- Before compliance audits
- When investigating incidents

---

**Status:** ✅ PRODUCTION READY  
**Created:** 2026-11-17  
**Version:** 1.0  

Your synthesis agent is ready to generate comprehensive reports! 🎉
