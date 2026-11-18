# Multi-Perspective Log Analyzer

A Python script that analyzes application logs from three specialized perspectives:
1. **Data Quality & Logging Standards** - Evaluates logging infrastructure and standards compliance
2. **Security & Threat Detection** - Identifies security threats, vulnerabilities, and compliance issues
3. **Performance & Operations** - Assesses system health, resources, and performance bottlenecks

## Features

### 🎯 Three Independent Analysis Modules

#### Data Quality Analyzer
- Evaluates log format, structure, and completeness
- Scores logging infrastructure 1-10
- Detects missing trace IDs, correlation IDs, and context
- Provides structured improvement roadmap
- Checks for PII exposure

#### Security Analyzer
- Detects brute force attacks
- Identifies privilege escalation attempts
- Finds cascading infrastructure failures
- Scans for PII exposure (emails, credentials, IPs)
- Assesses compliance against GDPR, CCPA, SOC 2, HIPAA
- Generates immediate action items

#### Performance Analyzer
- Assesses overall system health
- Analyzes resource utilization (memory, CPU, disk, database)
- Identifies performance bottlenecks
- Extracts performance metrics from logs
- Performs root cause analysis of failures
- Provides phase-based remediation roadmap

## Installation

### Requirements
- Python 3.7+
- No external dependencies (uses only standard library)

### Setup
```bash
# No installation needed, just run:
python log_analyzer.py <log_file>
```

## Usage

### Basic Usage
```bash
python log_analyzer.py complex-application.log
```

### Output
The script generates a comprehensive report with three sections:

1. **Data Quality Analysis**
   - Quality score (0-10)
   - Format quality assessment
   - Completeness evaluation
   - Consistency check
   - Traceability assessment
   - Improvement recommendations

2. **Security Analysis**
   - Risk level assessment
   - Threats detected (with severity levels)
   - Sensitive data exposure inventory
   - Anomaly patterns
   - Compliance status
   - Immediate actions required

3. **Performance Analysis**
   - System health status
   - Resource utilization breakdown
   - Extracted performance metrics
   - Bottleneck identification
   - Root cause analysis
   - Remediation roadmap (4 phases)

## Log Format Requirements

The analyzer expects logs in this format:

```
2024-01-15T09:23:15.847Z [LEVEL] [COMPONENT] message - key=value pairs
```

### Example:
```
2024-01-15T09:23:15.847Z [INFO] [AuthService] User login attempt - user_id=usr_001 email=john.doe@company.com ip=192.168.1.105
2024-01-15T09:24:02.156Z [ERROR] [PaymentGateway] Payment processing failed - order_id=ord_12345 amount=USD_1500.00 error_code=GATEWAY_TIMEOUT reason="Connection timeout after 30s"
```

### Fields
- **Timestamp**: ISO 8601 format with milliseconds (UTC)
- **Level**: INFO, WARN, ERROR, or CRITICAL
- **Component**: Service/module name
- **Message**: Description with key=value fields

## Architecture

### LogEntry Class
Parses individual log entries and extracts structured data.

```python
entry = LogEntry("2024-01-15T09:23:15.847Z [INFO] [AuthService] User login...")
entry.timestamp  # "2024-01-15T09:23:15.847Z"
entry.level      # "INFO"
entry.component  # "AuthService"
entry.fields     # {"user_id": "usr_001", "email": "john.doe@company.com", ...}
```

### DataQualityAnalyzer
Evaluates logging infrastructure and standards.

```python
analyzer = DataQualityAnalyzer(entries)
results = analyzer.analyze()
# Returns: overall_score, format_quality, completeness, consistency, 
#          traceability, recommendations
```

### SecurityAnalyzer
Detects security threats and compliance issues.

```python
analyzer = SecurityAnalyzer(entries)
results = analyzer.analyze()
# Returns: risk_level, threats_detected, sensitive_data_exposure,
#          anomaly_patterns, compliance_status, immediate_actions
```

### PerformanceAnalyzer
Analyzes system health and performance.

```python
analyzer = PerformanceAnalyzer(entries)
results = analyzer.analyze()
# Returns: system_health, resource_utilization, performance_metrics,
#          bottlenecks, root_cause, remediation_roadmap
```

### LogAnalyzerCLI
Command-line interface for running all analyses.

```python
cli = LogAnalyzerCLI('complex-application.log')
cli.run_full_analysis()
```

## Example Output

```
================================================================================
MULTI-PERSPECTIVE LOG ANALYSIS
================================================================================

📋 DATA QUALITY & LOGGING STANDARDS ANALYSIS
⭐ Overall Quality Score: 7.5/10
📊 Format Quality:
  valid_entries: 37/37 (100%)
  has_timestamps: True
  format: ISO 8601 [LEVEL] [COMPONENT] key=value
  
🚨 SECURITY & THREAT DETECTION ANALYSIS
Risk Level: CRITICAL
⚠️ Threats Detected (4):
  Type: Brute Force Attack
  Severity: CRITICAL
  Details: 15 failed login attempts in 60s targeting admin/root accounts

📊 PERFORMANCE & OPERATIONS ANALYSIS
🏥 System Health:
  status: CRITICAL OUTAGE
  critical_events: 5
  error_events: 9
```

## Key Metrics

### Data Quality
- Quality Score: 0-10 (10 = production-ready)
- Traceability: 0-10 (measures ability to trace transactions)
- Format Consistency: 0-100% (valid entry parsing rate)

### Security
- Risk Level: Low, Medium, High, Critical
- Threats: Categorized by type and severity
- Compliance Status: GDPR, CCPA, SOC 2, HIPAA

### Performance
- System Health: Operational, Degraded, Critical Outage
- Resource Utilization: % or status for each resource
- Bottleneck Impact: Direct metrics and business impact

## Extensibility

### Adding Custom Analyzers

```python
class CustomAnalyzer:
    def __init__(self, entries: List[LogEntry]):
        self.entries = entries
    
    def analyze(self) -> Dict[str, Any]:
        # Your analysis logic
        return results

# Integrate into CLI
analyzer = CustomAnalyzer(entries)
results = analyzer.analyze()
```

### Adding Custom Threat Detection

```python
# In SecurityAnalyzer._detect_threats()
def _detect_custom_threat(self) -> Dict[str, str]:
    for e in self.entries:
        if 'your_pattern' in e.raw:
            return {
                'type': 'Custom Threat',
                'severity': 'HIGH',
                'evidence': e.raw,
                'action': 'Recommended action'
            }
```

## Performance

- **Time Complexity**: O(n) where n = number of log entries
- **Space Complexity**: O(n) for storing parsed entries
- **Typical Execution**: < 1 second for 1000 entries

## Limitations

1. **Log Format**: Expects specific ISO 8601 [LEVEL] [COMPONENT] format
2. **PII Detection**: Basic patterns (emails, AWS keys, IPs)
3. **Threat Detection**: Pattern-based, not ML-based anomaly detection
4. **Baseline**: No historical baseline comparison for anomalies

## Future Enhancements

- [ ] ML-based anomaly detection
- [ ] Historical comparison with baselines
- [ ] Advanced NLP for threat detection
- [ ] JSON output format option
- [ ] Custom rule configuration file
- [ ] Integration with SIEM tools
- [ ] Real-time streaming log analysis
- [ ] Distributed tracing correlation

## Usage Examples

### Analyze production logs
```bash
python log_analyzer.py /var/log/application.log
```

### Export to file
```bash
python log_analyzer.py complex-application.log > analysis_report.txt
```

### Integrate with CI/CD
```bash
# Fail pipeline if risk level is CRITICAL
python log_analyzer.py logs.txt | grep -q "CRITICAL" && exit 1
```

## License

MIT

## Contributing

Contributions welcome! Areas:
- Additional threat detection patterns
- Custom analyzer implementations
- Performance optimizations
- PII detection improvements

---

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**Python Version**: 3.7+
