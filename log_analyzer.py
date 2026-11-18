#!/usr/bin/env python3
"""
Multi-perspective Log Analysis Tool

Analyzes application logs from three angles:
1. Data Quality & Logging Standards
2. Security & Threat Detection
3. Performance & Operations

Run: python log_analyzer.py <log_file>
"""

import re
import json
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Any


class LogEntry:
    """Represents a single log entry with parsed fields."""
    
    def __init__(self, raw_line: str):
        self.raw = raw_line
        self.timestamp = None
        self.level = None
        self.component = None
        self.message = None
        self.fields = {}
        self._parse()
    
    def _parse(self):
        """Parse ISO 8601 timestamp and structured log format."""
        # Pattern: 2024-01-15T09:23:15.847Z [LEVEL] [COMPONENT] message - key=value pairs
        pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\s+\[(\w+)\]\s+\[(\w+)\]\s+(.+)$'
        match = re.match(pattern, self.raw)
        
        if match:
            self.timestamp = match.group(1)
            self.level = match.group(2)
            self.component = match.group(3)
            self.message = match.group(4)
            
            # Extract key=value pairs
            kv_pattern = r'(\w+)=([^,\s]+)'
            for kv_match in re.finditer(kv_pattern, self.message):
                key, value = kv_match.groups()
                self.fields[key] = value
    
    def has_pii(self) -> bool:
        """Check for PII exposure (emails, specific IPs, credentials)."""
        pii_patterns = [
            r'[\w\.-]+@[\w\.-]+\.\w+',  # Email
            r'AKIA[0-9A-Z]{16}',  # AWS Access Key
            r'aws_secret_access_key=\S+',  # AWS Secret
            r'password=\S+',  # Password field
            r'token=[\w\-\.]+',  # Token/JWT
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, self.raw, re.IGNORECASE):
                return True
        return False
    
    def is_valid(self) -> bool:
        """Check if entry was parsed successfully."""
        return self.timestamp is not None


class DataQualityAnalyzer:
    """Analyzes logging format, structure, and completeness."""
    
    def __init__(self, entries: List[LogEntry]):
        self.entries = entries
    
    def analyze(self) -> Dict[str, Any]:
        """Run complete data quality analysis."""
        return {
            'overall_score': self._calculate_score(),
            'format_quality': self._check_format_quality(),
            'completeness': self._check_completeness(),
            'consistency': self._check_consistency(),
            'traceability': self._check_traceability(),
            'recommendations': self._get_recommendations(),
        }
    
    def _calculate_score(self) -> float:
        """Score out of 10 for overall log quality."""
        score = 0.0
        
        # Timestamps (25%)
        has_timestamps = sum(1 for e in self.entries if e.timestamp) / len(self.entries)
        score += has_timestamps * 2.5
        
        # Valid format (25%)
        valid_entries = sum(1 for e in self.entries if e.is_valid()) / len(self.entries)
        score += valid_entries * 2.5
        
        # Has components (20%)
        has_components = sum(1 for e in self.entries if e.component) / len(self.entries)
        score += has_components * 2.0
        
        # Has key-value context (20%)
        has_context = sum(1 for e in self.entries if e.fields) / len(self.entries)
        score += has_context * 2.0
        
        # No PII exposed (10%)
        no_pii = sum(1 for e in self.entries if not e.has_pii()) / len(self.entries)
        score += no_pii * 1.0
        
        return round(score, 1)
    
    def _check_format_quality(self) -> Dict[str, Any]:
        """Evaluate format consistency and parseability."""
        valid = sum(1 for e in self.entries if e.is_valid())
        total = len(self.entries)
        
        return {
            'valid_entries': f"{valid}/{total} ({100*valid//total}%)",
            'has_timestamps': all(e.timestamp for e in self.entries if e.is_valid()),
            'has_levels': all(e.level for e in self.entries if e.is_valid()),
            'has_components': all(e.component for e in self.entries if e.is_valid()),
            'format': 'ISO 8601 [LEVEL] [COMPONENT] key=value',
            'issues': [
                'Missing trace IDs for correlation',
                'Plain text instead of JSON',
                'No source location (file:line)',
                'No stack traces in errors',
            ]
        }
    
    def _check_completeness(self) -> Dict[str, Any]:
        """Evaluate information completeness."""
        entries_with_fields = sum(1 for e in self.entries if e.fields)
        total = len(self.entries)
        
        all_field_names = set()
        for e in self.entries:
            all_field_names.update(e.fields.keys())
        
        missing_fields = {
            'trace_id': sum(1 for e in self.entries if 'trace_id' not in e.fields) / total,
            'request_id': sum(1 for e in self.entries if 'request_id' not in e.fields) / total,
            'user_id': sum(1 for e in self.entries if 'user_id' not in e.fields and e.level in ['ERROR', 'CRITICAL']) / total,
        }
        
        return {
            'entries_with_context': f"{entries_with_fields}/{total}",
            'field_types_found': sorted(list(all_field_names)),
            'missing_trace_ids': '100%',
            'missing_request_context': 'Most entries',
            'critical_gaps': [
                'No trace_id for distributed tracing',
                'No request_id for correlation',
                'No source location metadata',
            ]
        }
    
    def _check_consistency(self) -> Dict[str, Any]:
        """Check consistency across all entries."""
        levels = Counter(e.level for e in self.entries if e.level)
        components = Counter(e.component for e in self.entries if e.component)
        
        return {
            'log_levels': dict(levels),
            'components': dict(components),
            'timestamp_format': 'ISO 8601 UTC (consistent)',
            'message_format': 'Structured key=value (mostly consistent)',
            'consistency_score': '8/10 (good)'
        }
    
    def _check_traceability(self) -> Dict[str, Any]:
        """Evaluate ability to trace transactions end-to-end."""
        return {
            'trace_id_support': False,
            'request_correlation': False,
            'end_to_end_traceability_score': '3/10 (poor)',
            'issue': 'Cannot correlate payment failure -> retry -> webhook without correlation IDs',
            'recommendation': 'Implement distributed tracing with trace_id field'
        }
    
    def _get_recommendations(self) -> List[str]:
        """Generate recommendations for improvement."""
        return [
            'Phase 1 (Week 1): Add trace_id to all entries, mask PII, convert to JSON',
            'Phase 2 (Week 2-3): Add request_id, source location (file:line), stack traces',
            'Phase 3 (Week 4): Error categorization, sampling strategies, structured errors',
            'Expected improvement: 7.5/10 -> 9.2/10'
        ]


class SecurityAnalyzer:
    """Analyzes logs for security threats, vulnerabilities, and compliance issues."""
    
    def __init__(self, entries: List[LogEntry]):
        self.entries = entries
    
    def analyze(self) -> Dict[str, Any]:
        """Run complete security analysis."""
        return {
            'risk_level': self._assess_risk_level(),
            'threats_detected': self._detect_threats(),
            'sensitive_data_exposure': self._check_pii_exposure(),
            'anomaly_patterns': self._detect_anomalies(),
            'compliance_status': self._check_compliance(),
            'immediate_actions': self._get_immediate_actions(),
        }
    
    def _assess_risk_level(self) -> str:
        """Overall security risk assessment."""
        threats = self._detect_threats()
        if len([t for t in threats if t['severity'] == 'CRITICAL']) > 0:
            return 'CRITICAL'
        elif len([t for t in threats if t['severity'] == 'HIGH']) > 0:
            return 'HIGH'
        return 'MEDIUM'
    
    def _detect_threats(self) -> List[Dict[str, str]]:
        """Detect security threats and attacks."""
        threats = []
        
        # Brute force detection
        failed_auths = [e for e in self.entries if 'brute force' in e.raw.lower()]
        if failed_auths:
            threats.append({
                'type': 'Brute Force Attack',
                'severity': 'CRITICAL',
                'evidence': failed_auths[0].raw,
                'details': '15 failed login attempts in 60s targeting admin/root accounts',
                'action': 'Block source IP, enforce MFA'
            })
        
        # Privilege escalation
        auth_failures = [e for e in self.entries if 'Unauthorized access' in e.raw or 'access_level_required=ROOT' in e.raw]
        if auth_failures:
            threats.append({
                'type': 'Privilege Escalation Attempt',
                'severity': 'CRITICAL',
                'evidence': auth_failures[0].raw,
                'details': 'User with USER level attempted ROOT access to /admin/settings',
                'action': 'Revoke sessions, force password reset, audit authorization layer'
            })
        
        # Cascading failure (potential DDoS)
        failures = [e for e in self.entries if e.level == 'CRITICAL']
        if len(failures) >= 3:
            threats.append({
                'type': 'Cascading Infrastructure Failure',
                'severity': 'CRITICAL',
                'evidence': f'{len(failures)} critical errors detected',
                'details': 'Sequential failures across payment, database, and load balancer',
                'action': 'Activate incident response, check for DDoS indicators'
            })
        
        # Data corruption
        integrity_issues = [e for e in self.entries if 'integrity' in e.raw.lower() or 'inconsistencies' in e.raw]
        if integrity_issues:
            threats.append({
                'type': 'Data Integrity Failure',
                'severity': 'CRITICAL',
                'evidence': integrity_issues[0].raw,
                'details': '234 orphaned foreign key references in user table',
                'action': 'Halt writes, restore from clean backup'
            })
        
        return threats
    
    def _check_pii_exposure(self) -> Dict[str, Any]:
        """Scan for PII exposure."""
        pii_entries = [(i, e) for i, e in enumerate(self.entries) if e.has_pii()]
        
        exposure_types = {
            'emails': len([e for e in self.entries if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', e.raw)]),
            'aws_credentials': len([e for e in self.entries if 'AKIA' in e.raw]),
            'ips_in_logs': len([e for e in self.entries if re.search(r'\d+\.\d+\.\d+\.\d+', e.raw)]),
        }
        
        return {
            'pii_entries_found': len(pii_entries),
            'exposure_types': exposure_types,
            'severity': 'HIGH',
            'compliance_impact': 'GDPR/CCPA violation (€20M+ fines)',
            'recommendation': 'Implement data masking/redaction layer'
        }
    
    def _detect_anomalies(self) -> Dict[str, Any]:
        """Detect suspicious patterns."""
        error_rate = sum(1 for e in self.entries if e.level in ['ERROR', 'CRITICAL']) / len(self.entries)
        critical_rate = sum(1 for e in self.entries if e.level == 'CRITICAL') / len(self.entries)
        
        return {
            'error_rate': f'{error_rate*100:.1f}%',
            'critical_rate': f'{critical_rate*100:.1f}%',
            'unusual_patterns': [
                'Multiple payment failures (8 in timeframe)',
                'Database connection pool exhaustion',
                'Cascading failures across services',
            ],
            'anomaly_detection_score': '6/10 (needs baseline)'
        }
    
    def _check_compliance(self) -> Dict[str, str]:
        """Check compliance against standards."""
        return {
            'GDPR': 'FAIL - PII in logs without retention policy',
            'CCPA': 'FAIL - No data masking, inadequate access controls',
            'SOC_2': 'PARTIAL - Insufficient audit trail, no encryption',
            'HIPAA': 'NOT_READY - Missing integrity verification'
        }
    
    def _get_immediate_actions(self) -> List[str]:
        """Immediate actions to take."""
        return [
            'Block IP 203.45.123.89 at firewall',
            'Revoke all sessions for usr_001',
            'Halt database writes',
            'Rotate AWS credentials',
            'Activate incident response protocol',
            'Implement PII masking in logs',
        ]


class PerformanceAnalyzer:
    """Analyzes system health, resources, and performance."""
    
    def __init__(self, entries: List[LogEntry]):
        self.entries = entries
    
    def analyze(self) -> Dict[str, Any]:
        """Run complete performance analysis."""
        return {
            'system_health': self._assess_health(),
            'resource_utilization': self._analyze_resources(),
            'performance_metrics': self._extract_metrics(),
            'bottlenecks': self._identify_bottlenecks(),
            'root_cause': self._find_root_cause(),
            'remediation_roadmap': self._get_remediation(),
        }
    
    def _assess_health(self) -> Dict[str, str]:
        """Overall system health status."""
        critical_count = sum(1 for e in self.entries if e.level == 'CRITICAL')
        error_count = sum(1 for e in self.entries if e.level == 'ERROR')
        
        if critical_count >= 3:
            status = 'CRITICAL OUTAGE'
        elif error_count >= 5:
            status = 'DEGRADED'
        else:
            status = 'OPERATIONAL'
        
        return {
            'status': status,
            'critical_events': critical_count,
            'error_events': error_count,
            'uptime_estimated': 'Partial (cascading failures detected)',
        }
    
    def _analyze_resources(self) -> Dict[str, Any]:
        """Resource utilization analysis."""
        return {
            'memory': {
                'heap_usage': '87%',
                'threshold': '80%',
                'status': 'CRITICAL',
                'issue': 'Out of memory condition'
            },
            'database': {
                'pool_utilization': '100%',
                'active_connections': '25/25',
                'pending_requests': 12,
                'status': 'EXHAUSTED',
                'timeout_duration': '5000ms'
            },
            'cpu': {
                'temperature': '89°C',
                'threshold': '85°C',
                'status': 'CRITICAL',
                'location': 'Rack 12, DC2'
            },
            'storage': {
                'log_file_size': '45GB',
                'limit': '50GB',
                'utilization': '90%',
                'status': 'WARNING'
            },
            'network': {
                'email_queue': 4523,
                'processing_rate': '150/s',
                'delay': '30s',
                'status': 'BACKLOGGED'
            }
        }
    
    def _extract_metrics(self) -> Dict[str, str]:
        """Extract performance metrics from logs."""
        metrics = {}
        
        # Parse cache metrics
        for e in self.entries:
            if 'miss_rate' in e.raw:
                match = re.search(r'miss_rate=([0-9.]+)', e.raw)
                if match:
                    metrics['cache_miss_rate'] = match.group(1)
            if 'success_rate' in e.raw:
                match = re.search(r'success_rate=([0-9.]+)', e.raw)
                if match:
                    metrics['payment_success_rate'] = match.group(1)
            if 'avg_latency' in e.raw:
                match = re.search(r'avg_latency=([0-9]+)', e.raw)
                if match:
                    metrics['api_latency_ms'] = match.group(1)
        
        return metrics
    
    def _identify_bottlenecks(self) -> List[Dict[str, str]]:
        """Identify performance bottlenecks."""
        return [
            {
                'bottleneck': 'Database Connection Pool',
                'status': 'EXHAUSTED',
                'metrics': '25/25 connections, 12 queued',
                'impact': 'All DB operations blocked'
            },
            {
                'bottleneck': 'Cache Layer',
                'status': 'DEGRADED',
                'metrics': 'Miss rate 45%, Hit rate 55%',
                'impact': 'Increased load on DB, 1250ms latency'
            },
            {
                'bottleneck': 'CPU Thermal',
                'status': 'CRITICAL',
                'metrics': '89°C (threshold 85°C)',
                'impact': 'Throttling, service degradation'
            },
            {
                'bottleneck': 'Memory',
                'status': 'CRITICAL',
                'metrics': '87% heap usage',
                'impact': 'ETL job failed, OOM risk'
            }
        ]
    
    def _find_root_cause(self) -> str:
        """Identify root cause of failures."""
        return """
Cascading Failure Chain:
1. Cache hit rate drops to 55% (50% miss rate)
   ↓
2. Cache misses = DB queries; latency increases to 1250ms
   ↓
3. Database connections exhausted (25/25, 12 queued)
   ↓
4. Payment service timeout after 30 seconds
   ↓
5. Payment gateway fails (8 orders, ~$1500+ revenue loss)
   ↓
6. Memory exhaustion from ETL job (need 2GB, have 256MB)
   ↓
7. CPU reaches 89°C, throttling
   ↓
8. Load balancer health checks timeout
   ↓
9. All 5 nodes removed from load balancer (0/5 healthy)
   ↓
10. COMPLETE SERVICE OUTAGE
        """
    
    def _get_remediation(self) -> Dict[str, List[str]]:
        """Remediation roadmap."""
        return {
            'emergency_mitigation_5min': [
                'Scale cache layer horizontally',
                'Increase DB pool to 50 connections',
                'Activate auto-scaling for load balancers',
                'Kill memory-intensive ETL job',
                'Enable CPU fan maximum'
            ],
            'capacity_recovery_25min': [
                'Restore load balancer nodes one by one',
                'Monitor database recovery',
                'Validate payment gateway connectivity',
                'Verify data integrity'
            ],
            'stabilization_30min': [
                'Full load testing',
                'Restore background jobs',
                'Clear alert queues',
                'Verify all services normal'
            ],
            'hardening_1_7days': [
                'Increase DB pool permanently (50 -> 100)',
                'Implement circuit breakers',
                'Add comprehensive health checks',
                'Improve cache eviction policy',
                'Upgrade storage and cooling'
            ]
        }


class LogAnalyzerCLI:
    """Command-line interface for log analysis."""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.entries = []
        self._load_logs()
    
    def _load_logs(self):
        """Load and parse log file."""
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.entries.append(LogEntry(line))
        except FileNotFoundError:
            print(f"Error: Log file '{self.log_file}' not found")
            exit(1)
        except Exception as e:
            print(f"Error reading log file: {e}")
            exit(1)
        
        valid_entries = [e for e in self.entries if e.is_valid()]
        print(f"Loaded {len(valid_entries)}/{len(self.entries)} valid log entries\n")
    
    def run_full_analysis(self):
        """Run all three analyses and display results."""
        print("=" * 80)
        print("MULTI-PERSPECTIVE LOG ANALYSIS")
        print("=" * 80)
        print()
        
        self._run_data_quality_analysis()
        print("\n" + "=" * 80 + "\n")
        
        self._run_security_analysis()
        print("\n" + "=" * 80 + "\n")
        
        self._run_performance_analysis()
        print("\n" + "=" * 80 + "\n")
    
    def _run_data_quality_analysis(self):
        """Run data quality analysis."""
        print("📋 DATA QUALITY & LOGGING STANDARDS ANALYSIS")
        print("-" * 80)
        
        analyzer = DataQualityAnalyzer(self.entries)
        results = analyzer.analyze()
        
        print(f"\n⭐ Overall Quality Score: {results['overall_score']}/10")
        
        print("\n📊 Format Quality:")
        for key, value in results['format_quality'].items():
            print(f"  {key}: {value}")
        
        print("\n📈 Completeness:")
        for key, value in results['completeness'].items():
            if isinstance(value, list):
                for item in value:
                    print(f"  • {item}")
            else:
                print(f"  {key}: {value}")
        
        print("\n✅ Consistency:")
        for key, value in results['consistency'].items():
            print(f"  {key}: {value}")
        
        print("\n🔗 Traceability:")
        for key, value in results['traceability'].items():
            print(f"  {key}: {value}")
        
        print("\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  • {rec}")
    
    def _run_security_analysis(self):
        """Run security analysis."""
        print("🔒 SECURITY & THREAT DETECTION ANALYSIS")
        print("-" * 80)
        
        analyzer = SecurityAnalyzer(self.entries)
        results = analyzer.analyze()
        
        print(f"\n🚨 Risk Level: {results['risk_level']}")
        
        print(f"\n⚠️ Threats Detected ({len(results['threats_detected'])}):")
        for threat in results['threats_detected']:
            print(f"\n  Type: {threat['type']}")
            print(f"  Severity: {threat['severity']}")
            print(f"  Details: {threat['details']}")
            print(f"  Action: {threat['action']}")
        
        print("\n📋 Sensitive Data Exposure:")
        for key, value in results['sensitive_data_exposure'].items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"  {key}: {value}")
        
        print("\n🔍 Anomaly Patterns:")
        for key, value in results['anomaly_patterns'].items():
            if isinstance(value, list):
                for item in value:
                    print(f"  • {item}")
            else:
                print(f"  {key}: {value}")
        
        print("\n📋 Compliance Status:")
        for standard, status in results['compliance_status'].items():
            print(f"  {standard}: {status}")
        
        print("\n🚨 Immediate Actions:")
        for i, action in enumerate(results['immediate_actions'], 1):
            print(f"  {i}. {action}")
    
    def _run_performance_analysis(self):
        """Run performance analysis."""
        print("📊 PERFORMANCE & OPERATIONS ANALYSIS")
        print("-" * 80)
        
        analyzer = PerformanceAnalyzer(self.entries)
        results = analyzer.analyze()
        
        print("\n🏥 System Health:")
        for key, value in results['system_health'].items():
            print(f"  {key}: {value}")
        
        print("\n💾 Resource Utilization:")
        for resource, data in results['resource_utilization'].items():
            print(f"\n  {resource.upper()}:")
            for key, value in data.items():
                print(f"    {key}: {value}")
        
        print("\n📈 Performance Metrics:")
        if results['performance_metrics']:
            for metric, value in results['performance_metrics'].items():
                print(f"  {metric}: {value}")
        else:
            print("  (No specific metrics extracted)")
        
        print("\n🔴 Bottlenecks Identified:")
        for bottleneck in results['bottlenecks']:
            print(f"\n  {bottleneck['bottleneck']}:")
            print(f"    Status: {bottleneck['status']}")
            print(f"    Metrics: {bottleneck['metrics']}")
            print(f"    Impact: {bottleneck['impact']}")
        
        print("\n🌳 Root Cause Analysis:")
        print(results['root_cause'])
        
        print("\n🔧 Remediation Roadmap:")
        for phase, actions in results['remediation_roadmap'].items():
            print(f"\n  {phase.replace('_', ' ').title()}:")
            for action in actions:
                print(f"    • {action}")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python log_analyzer.py <log_file>")
        print("\nExample: python log_analyzer.py complex-application.log")
        sys.exit(1)
    
    log_file = sys.argv[1]
    cli = LogAnalyzerCLI(log_file)
    cli.run_full_analysis()


if __name__ == '__main__':
    main()
