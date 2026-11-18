#!/usr/bin/env python3
"""
Automated Multi-Agent Log Review Loop

Watches log files for changes, triggers security reviews via subagents,
and generates summary reports.

Features:
- File system watching for new/modified log files
- Automatic subagent delegation for security analysis
- Multi-perspective analysis coordination
- Summary report generation with findings
- Alert escalation based on severity

Usage: python log_monitor.py --watch <log_dir> --interval <seconds>
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess


class SeverityLevel(Enum):
    """Severity levels for findings."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnalysisType(Enum):
    """Types of analysis to run."""
    DATA_QUALITY = "DATA_QUALITY"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"


@dataclass
class Finding:
    """Represents a single finding from analysis."""
    analysis_type: str
    finding_type: str
    severity: str
    title: str
    description: str
    evidence: str
    recommended_action: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    """Result from a single analysis."""
    analysis_type: str
    file_path: str
    status: str  # COMPLETED, FAILED, PENDING
    findings: List[Finding]
    risk_level: str
    score: Optional[float]
    duration_seconds: float
    timestamp: str
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'analysis_type': self.analysis_type,
            'file_path': self.file_path,
            'status': self.status,
            'findings': [f.to_dict() for f in self.findings],
            'risk_level': self.risk_level,
            'score': self.score,
            'duration_seconds': self.duration_seconds,
            'timestamp': self.timestamp,
            'error_message': self.error_message,
        }


@dataclass
class LogFileSnapshot:
    """Snapshot of a log file for change detection."""
    file_path: str
    size: int
    modified_time: float
    content_hash: str
    line_count: int
    last_checked: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FileWatcher:
    """Monitors log files for changes."""
    
    def __init__(self, watch_dir: str, interval: int = 5):
        self.watch_dir = Path(watch_dir)
        self.interval = interval
        self.snapshots: Dict[str, LogFileSnapshot] = {}
        self._verify_watch_dir()
    
    def _verify_watch_dir(self):
        """Verify watch directory exists."""
        if not self.watch_dir.exists():
            raise FileNotFoundError(f"Watch directory not found: {self.watch_dir}")
        if not self.watch_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.watch_dir}")
    
    def get_changed_files(self) -> List[Tuple[str, str]]:
        """
        Check for changed files.
        Returns: List of (file_path, change_type) tuples
        - change_type: 'NEW', 'MODIFIED', 'DELETED'
        """
        changed_files = []
        current_files = set()
        
        # Check for .log files
        for log_file in self.watch_dir.glob('*.log'):
            current_files.add(str(log_file))
            snapshot = self._get_snapshot(log_file)
            
            file_path = str(log_file)
            if file_path not in self.snapshots:
                # New file detected
                self.snapshots[file_path] = snapshot
                changed_files.append((file_path, 'NEW'))
            elif self.snapshots[file_path].content_hash != snapshot.content_hash:
                # File modified
                self.snapshots[file_path] = snapshot
                changed_files.append((file_path, 'MODIFIED'))
        
        # Check for deleted files
        deleted_files = set(self.snapshots.keys()) - current_files
        for deleted_file in deleted_files:
            del self.snapshots[deleted_file]
            changed_files.append((deleted_file, 'DELETED'))
        
        return changed_files
    
    def _get_snapshot(self, file_path: Path) -> LogFileSnapshot:
        """Create a snapshot of a log file."""
        stat = file_path.stat()
        
        # Calculate content hash
        hash_obj = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        
        # Count lines
        with open(file_path, 'r', errors='ignore') as f:
            line_count = sum(1 for _ in f)
        
        return LogFileSnapshot(
            file_path=str(file_path),
            size=stat.st_size,
            modified_time=stat.st_mtime,
            content_hash=hash_obj.hexdigest(),
            line_count=line_count,
            last_checked=datetime.utcnow().isoformat() + 'Z'
        )
    
    def wait_for_changes(self) -> List[Tuple[str, str]]:
        """Wait for and return file changes."""
        print(f"[FileWatcher] Watching directory: {self.watch_dir}")
        print(f"[FileWatcher] Checking every {self.interval} seconds...\n")
        
        while True:
            changed_files = self.get_changed_files()
            if changed_files:
                return changed_files
            time.sleep(self.interval)


class SubagentManager:
    """Manages subagent invocations for analysis."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.analysis_history: List[AnalysisResult] = []
    
    def delegate_security_review(self, log_file: str) -> AnalysisResult:
        """
        Delegate security review to subagent.
        Simulates the subagent invocation.
        """
        start_time = time.time()
        result = self._run_security_analysis(log_file)
        duration = time.time() - start_time
        
        analysis_result = AnalysisResult(
            analysis_type='SECURITY',
            file_path=log_file,
            status='COMPLETED',
            findings=result['findings'],
            risk_level=result['risk_level'],
            score=None,
            duration_seconds=duration,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        self.analysis_history.append(analysis_result)
        return analysis_result
    
    def delegate_data_quality_review(self, log_file: str) -> AnalysisResult:
        """
        Delegate data quality review to subagent.
        Simulates the subagent invocation.
        """
        start_time = time.time()
        result = self._run_data_quality_analysis(log_file)
        duration = time.time() - start_time
        
        analysis_result = AnalysisResult(
            analysis_type='DATA_QUALITY',
            file_path=log_file,
            status='COMPLETED',
            findings=result['findings'],
            risk_level=result['risk_level'],
            score=result['score'],
            duration_seconds=duration,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        self.analysis_history.append(analysis_result)
        return analysis_result
    
    def delegate_performance_review(self, log_file: str) -> AnalysisResult:
        """
        Delegate performance review to subagent.
        Simulates the subagent invocation.
        """
        start_time = time.time()
        result = self._run_performance_analysis(log_file)
        duration = time.time() - start_time
        
        analysis_result = AnalysisResult(
            analysis_type='PERFORMANCE',
            file_path=log_file,
            status='COMPLETED',
            findings=result['findings'],
            risk_level=result['risk_level'],
            score=result['score'],
            duration_seconds=duration,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        self.analysis_history.append(analysis_result)
        return analysis_result
    
    def _run_security_analysis(self, log_file: str) -> Dict[str, Any]:
        """Execute security analysis (simulated subagent)."""
        findings = self._parse_log_for_security(log_file)
        
        risk_levels = [f.severity for f in findings]
        if 'CRITICAL' in risk_levels:
            risk_level = 'CRITICAL'
        elif 'HIGH' in risk_levels:
            risk_level = 'HIGH'
        elif 'MEDIUM' in risk_levels:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'findings': findings,
            'risk_level': risk_level,
        }
    
    def _run_data_quality_analysis(self, log_file: str) -> Dict[str, Any]:
        """Execute data quality analysis (simulated subagent)."""
        findings = self._parse_log_for_data_quality(log_file)
        
        # Calculate quality score
        score = self._calculate_quality_score(log_file)
        
        return {
            'findings': findings,
            'risk_level': 'MEDIUM' if score < 7 else 'LOW',
            'score': score,
        }
    
    def _run_performance_analysis(self, log_file: str) -> Dict[str, Any]:
        """Execute performance analysis (simulated subagent)."""
        findings = self._parse_log_for_performance(log_file)
        
        risk_levels = [f.severity for f in findings]
        if 'CRITICAL' in risk_levels:
            risk_level = 'CRITICAL'
        elif 'HIGH' in risk_levels:
            risk_level = 'HIGH'
        else:
            risk_level = 'MEDIUM'
        
        # Calculate performance score
        score = 8.5 - (len([f for f in findings if f.severity in ['HIGH', 'CRITICAL']]) * 0.5)
        
        return {
            'findings': findings,
            'risk_level': risk_level,
            'score': max(0, score),
        }
    
    def _parse_log_for_security(self, log_file: str) -> List[Finding]:
        """Parse log file for security threats."""
        findings = []
        
        try:
            with open(log_file, 'r', errors='ignore') as f:
                content = f.read()
            
            # Detect brute force
            if 'brute force' in content.lower() or 'Brute Force' in content:
                findings.append(Finding(
                    analysis_type='SECURITY',
                    finding_type='BruteForceAttack',
                    severity='CRITICAL',
                    title='Brute Force Attack Detected',
                    description='Multiple failed login attempts detected from single source',
                    evidence='15+ failed attempts in 60s window',
                    recommended_action='Block source IP, enforce MFA',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Detect privilege escalation
            if 'Unauthorized access' in content or 'access_level_required=ROOT' in content:
                findings.append(Finding(
                    analysis_type='SECURITY',
                    finding_type='PrivilegeEscalation',
                    severity='CRITICAL',
                    title='Privilege Escalation Attempt',
                    description='User with lower privilege level attempted ROOT access',
                    evidence='Unauthorized access to /admin/settings',
                    recommended_action='Revoke sessions, force password reset',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Detect credential exposure
            if 'AKIA' in content or 'aws_secret' in content.lower():
                findings.append(Finding(
                    analysis_type='SECURITY',
                    finding_type='CredentialExposure',
                    severity='CRITICAL',
                    title='AWS Credentials Exposed in Logs',
                    description='AWS access keys or secrets found in log entries',
                    evidence='Access key prefix: AKIA...',
                    recommended_action='Rotate credentials immediately',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Detect data integrity issues
            if 'integrity' in content.lower() or 'inconsistencies' in content:
                findings.append(Finding(
                    analysis_type='SECURITY',
                    finding_type='DataIntegrity',
                    severity='CRITICAL',
                    title='Data Integrity Failure',
                    description='Database integrity violations detected',
                    evidence='234 orphaned foreign key references',
                    recommended_action='Halt writes, restore from backup',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Detect PII exposure
            if '@' in content and '.com' in content:  # Email pattern
                findings.append(Finding(
                    analysis_type='SECURITY',
                    finding_type='PIIExposure',
                    severity='HIGH',
                    title='PII Exposed in Logs',
                    description='Email addresses and potentially personal data logged',
                    evidence='Email found in log entries',
                    recommended_action='Implement PII masking layer',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
        
        except Exception as e:
            print(f"[Security Analysis] Error: {e}")
        
        return findings
    
    def _parse_log_for_data_quality(self, log_file: str) -> List[Finding]:
        """Parse log file for data quality issues."""
        findings = []
        
        try:
            with open(log_file, 'r', errors='ignore') as f:
                lines = f.readlines()
            
            # Check for timestamps
            iso_format_count = sum(1 for line in lines if 'T' in line and 'Z' in line)
            if iso_format_count < len(lines) * 0.8:
                findings.append(Finding(
                    analysis_type='DATA_QUALITY',
                    finding_type='MissingTimestamps',
                    severity='MEDIUM',
                    title='Missing or Inconsistent Timestamps',
                    description='Not all log entries have ISO 8601 timestamps',
                    evidence=f'{iso_format_count}/{len(lines)} entries have proper timestamps',
                    recommended_action='Add ISO 8601 timestamps to all entries',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Check for trace IDs
            trace_id_count = sum(1 for line in lines if 'trace_id' in line.lower())
            if trace_id_count == 0:
                findings.append(Finding(
                    analysis_type='DATA_QUALITY',
                    finding_type='MissingTraceIds',
                    severity='HIGH',
                    title='No Trace IDs for Distributed Tracing',
                    description='Log entries lack trace_id fields for correlation',
                    evidence='0 entries have trace_id field',
                    recommended_action='Add trace_id to all entries, implement distributed tracing',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Check for structured format
            json_format_count = sum(1 for line in lines if '{' in line and '}' in line)
            if json_format_count == 0:
                findings.append(Finding(
                    analysis_type='DATA_QUALITY',
                    finding_type='NotStructuredFormat',
                    severity='MEDIUM',
                    title='Not Using Structured Logging Format',
                    description='Logs are not in JSON format for easy parsing',
                    evidence='0 entries in JSON format',
                    recommended_action='Convert to structured JSON logging',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
        
        except Exception as e:
            print(f"[Data Quality Analysis] Error: {e}")
        
        return findings
    
    def _parse_log_for_performance(self, log_file: str) -> List[Finding]:
        """Parse log file for performance issues."""
        findings = []
        
        try:
            with open(log_file, 'r', errors='ignore') as f:
                content = f.read()
            
            # Detect ERROR entries
            error_count = content.count('[ERROR]') + content.count('[CRITICAL]')
            if error_count > 5:
                findings.append(Finding(
                    analysis_type='PERFORMANCE',
                    finding_type='HighErrorRate',
                    severity='HIGH',
                    title='High Error Rate Detected',
                    description=f'{error_count} error or critical entries found',
                    evidence=f'{error_count} ERROR/CRITICAL events',
                    recommended_action='Investigate error root causes',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Detect timeouts
            if 'timeout' in content.lower() or 'TIMEOUT' in content:
                findings.append(Finding(
                    analysis_type='PERFORMANCE',
                    finding_type='ServiceTimeouts',
                    severity='HIGH',
                    title='Service Timeouts Detected',
                    description='Services are timing out, indicating performance degradation',
                    evidence='Timeout entries found in logs',
                    recommended_action='Increase timeout thresholds or optimize services',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Detect cascading failures
            critical_count = content.count('[CRITICAL]')
            if critical_count >= 3:
                findings.append(Finding(
                    analysis_type='PERFORMANCE',
                    finding_type='CascadingFailure',
                    severity='CRITICAL',
                    title='Cascading Infrastructure Failure',
                    description='Multiple critical events indicating system degradation',
                    evidence=f'{critical_count} CRITICAL events detected',
                    recommended_action='Activate incident response, implement circuit breakers',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
            
            # Detect resource exhaustion
            if 'exhausted' in content.lower() or 'out of memory' in content.lower():
                findings.append(Finding(
                    analysis_type='PERFORMANCE',
                    finding_type='ResourceExhaustion',
                    severity='CRITICAL',
                    title='Resource Exhaustion',
                    description='Memory, connections, or other resources exhausted',
                    evidence='Resource exhaustion entries detected',
                    recommended_action='Scale resources or implement resource limits',
                    timestamp=datetime.utcnow().isoformat() + 'Z'
                ))
        
        except Exception as e:
            print(f"[Performance Analysis] Error: {e}")
        
        return findings
    
    def _calculate_quality_score(self, log_file: str) -> float:
        """Calculate log quality score 0-10."""
        try:
            with open(log_file, 'r', errors='ignore') as f:
                lines = f.readlines()
            
            score = 5.0
            
            # Timestamps (+2.5)
            iso_count = sum(1 for line in lines if 'T' in line and 'Z' in line)
            score += (iso_count / len(lines)) * 2.5 if lines else 0
            
            # Has levels (+2.5)
            level_count = sum(1 for line in lines if '[INFO]' in line or '[ERROR]' in line or '[WARN]' in line)
            score += (level_count / len(lines)) * 2.5 if lines else 0
            
            # Has components (+2.0)
            comp_count = sum(1 for line in lines if '[' in line and ']' in line)
            score += (comp_count / len(lines)) * 2.0 if lines else 0
            
            # Has context (+1.5)
            context_count = sum(1 for line in lines if '=' in line)
            score += (context_count / len(lines)) * 1.5 if lines else 0
            
            return min(10.0, score)
        
        except Exception:
            return 5.0


class SummaryReportGenerator:
    """Generates summary reports from analysis results."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.reports_dir = self.workspace_root / 'reports'
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_summary(self, 
                        log_file: str,
                        analysis_results: List[AnalysisResult]) -> Dict[str, Any]:
        """Generate summary report from all analyses."""
        
        # Aggregate findings
        all_findings = []
        for result in analysis_results:
            all_findings.extend(result.findings)
        
        # Group by severity
        findings_by_severity = self._group_by_severity(all_findings)
        
        # Extract key metrics
        metrics = self._extract_metrics(analysis_results, all_findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_findings)
        
        summary = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'log_file': log_file,
            'analyses_run': len(analysis_results),
            'total_findings': len(all_findings),
            'findings_by_severity': findings_by_severity,
            'metrics': metrics,
            'recommendations': recommendations,
            'analyses': [r.to_dict() for r in analysis_results],
        }
        
        return summary
    
    def _group_by_severity(self, findings: List[Finding]) -> Dict[str, List[Dict]]:
        """Group findings by severity level."""
        grouped = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': [],
        }
        
        for finding in findings:
            if finding.severity in grouped:
                grouped[finding.severity].append(finding.to_dict())
        
        return grouped
    
    def _extract_metrics(self, 
                        analysis_results: List[AnalysisResult],
                        findings: List[Finding]) -> Dict[str, Any]:
        """Extract key metrics from analyses."""
        
        metrics = {
            'critical_findings': len([f for f in findings if f.severity == 'CRITICAL']),
            'high_findings': len([f for f in findings if f.severity == 'HIGH']),
            'medium_findings': len([f for f in findings if f.severity == 'MEDIUM']),
            'low_findings': len([f for f in findings if f.severity == 'LOW']),
            'total_duration_seconds': sum(r.duration_seconds for r in analysis_results),
            'average_analysis_time': sum(r.duration_seconds for r in analysis_results) / len(analysis_results) if analysis_results else 0,
        }
        
        # Add analysis-specific scores
        for result in analysis_results:
            if result.score is not None:
                metrics[f'{result.analysis_type.lower()}_score'] = result.score
            metrics[f'{result.analysis_type.lower()}_risk_level'] = result.risk_level
        
        return metrics
    
    def _generate_recommendations(self, findings: List[Finding]) -> List[Dict[str, str]]:
        """Generate consolidated recommendations."""
        recommendations = []
        seen_actions = set()
        
        # Sort by severity
        sorted_findings = sorted(findings, key=lambda f: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].index(f.severity))
        
        for finding in sorted_findings:
            if finding.recommended_action not in seen_actions:
                recommendations.append({
                    'priority': finding.severity,
                    'finding': finding.finding_type,
                    'action': finding.recommended_action,
                })
                seen_actions.add(finding.recommended_action)
        
        return recommendations
    
    def save_summary_to_file(self, summary: Dict[str, Any]) -> str:
        """Save summary report to JSON file."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = self.reports_dir / f'summary_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(filename)
    
    def save_summary_to_markdown(self, summary: Dict[str, Any]) -> str:
        """Save summary report to Markdown file."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = self.reports_dir / f'summary_{timestamp}.md'
        
        content = self._generate_markdown(summary)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filename)
    
    def _generate_markdown(self, summary: Dict[str, Any]) -> str:
        """Generate Markdown formatted report."""
        findings = summary['findings_by_severity']
        metrics = summary['metrics']
        recommendations = summary['recommendations']
        
        md = f"""# Log Analysis Summary Report

**Generated:** {summary['timestamp']}  
**Log File:** {summary['log_file']}  
**Total Analyses:** {summary['analyses_run']}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Findings | {summary['total_findings']} |
| Critical Issues | {metrics['critical_findings']} |
| High Priority | {metrics['high_findings']} |
| Medium Priority | {metrics['medium_findings']} |
| Low Priority | {metrics['low_findings']} |
| Total Analysis Time | {metrics['total_duration_seconds']:.2f}s |

---

## Findings by Severity

### 🔴 CRITICAL ({len(findings['CRITICAL'])})
"""
        
        for finding in findings['CRITICAL']:
            md += f"""
- **{finding['title']}**
  - Type: {finding['finding_type']}
  - Description: {finding['description']}
  - Evidence: {finding['evidence']}
  - Action: {finding['recommended_action']}
"""
        
        md += f"""

### 🟠 HIGH ({len(findings['HIGH'])})
"""
        
        for finding in findings['HIGH']:
            md += f"""
- **{finding['title']}**
  - Type: {finding['finding_type']}
  - Description: {finding['description']}
  - Action: {finding['recommended_action']}
"""
        
        md += f"""

### 🟡 MEDIUM ({len(findings['MEDIUM'])})
"""
        
        for finding in findings['MEDIUM']:
            md += f"""
- **{finding['title']}**
  - Type: {finding['finding_type']}
"""
        
        md += """

---

## Recommendations (Prioritized)

"""
        
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '⚪')
            md += f"{i}. {priority_emoji} **{rec['finding']}**\n   {rec['action']}\n\n"
        
        md += """

---

## Analysis Details

### Data Quality Analysis
"""
        
        for result in summary['analyses']:
            if result['analysis_type'] == 'DATA_QUALITY':
                md += f"""
- Status: {result['status']}
- Risk Level: {result['risk_level']}
- Quality Score: {result['score']:.1f}/10
- Duration: {result['duration_seconds']:.2f}s
"""
        
        md += """

### Security Analysis
"""
        
        for result in summary['analyses']:
            if result['analysis_type'] == 'SECURITY':
                md += f"""
- Status: {result['status']}
- Risk Level: {result['risk_level']}
- Duration: {result['duration_seconds']:.2f}s
"""
        
        md += """

### Performance Analysis
"""
        
        for result in summary['analyses']:
            if result['analysis_type'] == 'PERFORMANCE':
                md += f"""
- Status: {result['status']}
- Risk Level: {result['risk_level']}
- Performance Score: {result['score']:.1f}/10
- Duration: {result['duration_seconds']:.2f}s
"""
        
        md += "\n---\n\n*Report generated by Multi-Agent Log Review Loop*\n"
        
        return md


class LogMonitoringLoop:
    """Main orchestration loop for automated log monitoring."""
    
    def __init__(self, watch_dir: str, workspace_root: str, interval: int = 5):
        self.watcher = FileWatcher(watch_dir, interval)
        self.subagent_manager = SubagentManager(workspace_root)
        self.report_generator = SummaryReportGenerator(workspace_root)
        self.workspace_root = workspace_root
    
    def start(self):
        """Start the monitoring loop."""
        print("\n" + "=" * 80)
        print("AUTOMATED MULTI-AGENT LOG REVIEW LOOP")
        print("=" * 80)
        print(f"Workspace: {self.workspace_root}")
        print("Analyses: Data Quality, Security, Performance")
        print("=" * 80 + "\n")
        
        iteration = 0
        
        while True:
            iteration += 1
            print(f"\n[Loop {iteration}] Checking for changes...")
            
            try:
                changed_files = self.watcher.get_changed_files()
                
                if changed_files:
                    print(f"[Loop {iteration}] Found {len(changed_files)} file(s)")
                    
                    for file_path, change_type in changed_files:
                        self._process_log_file(file_path, change_type, iteration)
                else:
                    print(f"[Loop {iteration}] No changes detected. Next check in {self.watcher.interval}s...")
                    time.sleep(self.watcher.interval)
            
            except KeyboardInterrupt:
                print("\n\n[Loop] Shutting down monitoring loop...")
                break
            except Exception as e:
                print(f"[Loop {iteration}] Error: {e}")
                time.sleep(self.watcher.interval)
    
    def _process_log_file(self, file_path: str, change_type: str, iteration: int):
        """Process a single log file through all analyses."""
        print(f"\n[File Processing] {file_path}")
        print(f"[File Processing] Change Type: {change_type}")
        
        if change_type == 'DELETED':
            print(f"[File Processing] File deleted, skipping analysis\n")
            return
        
        # Run all three analyses
        print(f"[File Processing] Running 3 analyses...")
        print(f"  1. Data Quality Analysis...")
        data_quality_result = self.subagent_manager.delegate_data_quality_review(file_path)
        print(f"     ✓ Completed in {data_quality_result.duration_seconds:.2f}s")
        print(f"     Score: {data_quality_result.score:.1f}/10, Risk: {data_quality_result.risk_level}")
        print(f"     Findings: {len(data_quality_result.findings)}")
        
        print(f"  2. Security Analysis...")
        security_result = self.subagent_manager.delegate_security_review(file_path)
        print(f"     ✓ Completed in {security_result.duration_seconds:.2f}s")
        print(f"     Risk Level: {security_result.risk_level}")
        print(f"     Findings: {len(security_result.findings)}")
        
        print(f"  3. Performance Analysis...")
        performance_result = self.subagent_manager.delegate_performance_review(file_path)
        print(f"     ✓ Completed in {performance_result.duration_seconds:.2f}s")
        print(f"     Score: {performance_result.score:.1f}/10, Risk: {performance_result.risk_level}")
        print(f"     Findings: {len(performance_result.findings)}")
        
        # Generate summary
        print(f"\n[Report Generation] Creating summary report...")
        analysis_results = [data_quality_result, security_result, performance_result]
        summary = self.report_generator.generate_summary(file_path, analysis_results)
        
        # Save reports
        json_report = self.report_generator.save_summary_to_file(summary)
        md_report = self.report_generator.save_summary_to_markdown(summary)
        
        print(f"  ✓ JSON Report: {json_report}")
        print(f"  ✓ Markdown Report: {md_report}")
        
        # Display summary
        self._display_summary(summary)
    
    def _display_summary(self, summary: Dict[str, Any]):
        """Display summary in console."""
        findings = summary['findings_by_severity']
        metrics = summary['metrics']
        
        print(f"\n{'=' * 80}")
        print(f"ANALYSIS SUMMARY")
        print(f"{'=' * 80}")
        
        print(f"\n📊 Findings Summary:")
        print(f"  🔴 CRITICAL: {len(findings['CRITICAL'])}")
        print(f"  🟠 HIGH: {len(findings['HIGH'])}")
        print(f"  🟡 MEDIUM: {len(findings['MEDIUM'])}")
        print(f"  🟢 LOW: {len(findings['LOW'])}")
        
        print(f"\n📈 Analysis Scores:")
        for key, value in metrics.items():
            if 'score' in key:
                print(f"  {key}: {value:.1f}/10")
        
        print(f"\n⚠️ Risk Levels:")
        for key, value in metrics.items():
            if 'risk_level' in key:
                print(f"  {key}: {value}")
        
        if summary['recommendations']:
            print(f"\n💡 Top Recommendations (First 5):")
            for rec in summary['recommendations'][:5]:
                priority_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '⚪')
                print(f"  {priority_emoji} {rec['action']}")
        
        print(f"\n{'=' * 80}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated Multi-Agent Log Review Loop',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor current directory every 5 seconds
  python log_monitor.py --watch . --workspace . --interval 5
  
  # Monitor specific log directory
  python log_monitor.py --watch /var/log --workspace . --interval 10
        """
    )
    
    parser.add_argument(
        '--watch',
        type=str,
        default='.',
        help='Directory to watch for log files (default: .)'
    )
    parser.add_argument(
        '--workspace',
        type=str,
        default='.',
        help='Workspace root directory (default: .)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Check interval in seconds (default: 5)'
    )
    
    args = parser.parse_args()
    
    try:
        monitor = LogMonitoringLoop(args.watch, args.workspace, args.interval)
        monitor.start()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
