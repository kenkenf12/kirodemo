#!/usr/bin/env python3
"""
Synthesis Agent - Summarizes findings and generates visual reports with charts

This agent:
1. Aggregates findings from all three agents
2. Creates executive summaries
3. Generates charts and visualizations
4. Produces comprehensive PDF/HTML reports
5. Calculates metrics and trends
"""

import json
import base64
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3


# ============================================================================
# ASCII Chart Generator (No External Dependencies)
# ============================================================================

class AsciiCharts:
    """Generate ASCII charts for terminal and text display."""
    
    @staticmethod
    def bar_chart(title: str, data: Dict[str, int], max_width: int = 40) -> str:
        """Generate horizontal bar chart."""
        if not data:
            return f"{title}\n(No data)"
        
        max_value = max(data.values()) if data.values() else 1
        
        chart = f"\n{title}\n"
        chart += "=" * (max_width + 20) + "\n"
        
        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            percentage = (value / max_value * 100) if max_value > 0 else 0
            bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
            bar = "█" * bar_length
            chart += f"{label:20} │ {bar:40} │ {value:4} ({percentage:5.1f}%)\n"
        
        chart += "=" * (max_width + 20) + "\n"
        return chart
    
    @staticmethod
    def pie_chart_text(title: str, data: Dict[str, int]) -> str:
        """Generate text-based pie chart representation."""
        if not data:
            return f"{title}\n(No data)"
        
        total = sum(data.values())
        if total == 0:
            return f"{title}\n(No data)"
        
        chart = f"\n{title}\n"
        chart += "=" * 50 + "\n"
        
        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            percentage = (value / total) * 100
            # Create simple pie representation
            pie_chars = int(percentage / 5)
            pie_visual = "●" * pie_chars + "○" * (20 - pie_chars)
            chart += f"{label:15} │ {pie_visual:20} │ {percentage:5.1f}% ({value})\n"
        
        chart += "=" * 50 + "\n"
        return chart
    
    @staticmethod
    def severity_distribution(findings: List[Dict]) -> str:
        """Generate severity distribution chart."""
        severity_count = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            if severity in severity_count:
                severity_count[severity] += 1
        
        return AsciiCharts.bar_chart("Severity Distribution", severity_count)
    
    @staticmethod
    def agent_findings_chart(findings: List[Dict]) -> str:
        """Generate findings by agent type."""
        agent_count = {}
        
        for finding in findings:
            agent = finding.get('analysis_type', 'UNKNOWN')
            agent_count[agent] = agent_count.get(agent, 0) + 1
        
        return AsciiCharts.bar_chart("Findings by Agent", agent_count)


# ============================================================================
# HTML Report Generator
# ============================================================================

class HtmlReportGenerator:
    """Generate professional HTML reports with embedded charts."""
    
    @staticmethod
    def generate_chart_svg(title: str, data: Dict[str, int], chart_type: str = 'bar') -> str:
        """Generate SVG chart."""
        if chart_type == 'bar':
            return HtmlReportGenerator._bar_chart_svg(title, data)
        elif chart_type == 'pie':
            return HtmlReportGenerator._pie_chart_svg(title, data)
        return ""
    
    @staticmethod
    def _bar_chart_svg(title: str, data: Dict[str, int]) -> str:
        """Generate SVG bar chart."""
        if not data:
            return ""
        
        items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        max_value = max([v for k, v in items]) if items else 1
        
        bar_height = 40
        spacing = 10
        height = len(items) * (bar_height + spacing) + 60
        width = 600
        
        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <style>
                .chart-title {{ font-size: 18px; font-weight: bold; fill: #333; }}
                .bar-label {{ font-size: 12px; fill: #666; }}
                .bar-value {{ font-size: 11px; fill: #999; }}
            </style>
            <rect width="{width}" height="{height}" fill="#f9f9f9"/>
            <text x="20" y="30" class="chart-title">{title}</text>'''
        
        colors = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60', '#3498db', '#9b59b6']
        
        for idx, (label, value) in enumerate(items):
            y = 50 + idx * (bar_height + spacing)
            bar_width = (value / max_value) * 400 if max_value > 0 else 0
            color = colors[idx % len(colors)]
            
            svg += f'''
            <rect x="150" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="3"/>
            <text x="10" y="{y + 25}" class="bar-label">{label}</text>
            <text x="{155 + bar_width}" y="{y + 25}" class="bar-value">{value}</text>'''
        
        svg += '''
        </svg>'''
        
        return svg
    
    @staticmethod
    def _pie_chart_svg(title: str, data: Dict[str, int]) -> str:
        """Generate SVG pie chart."""
        if not data:
            return ""
        
        total = sum(data.values())
        if total == 0:
            return ""
        
        svg = '''<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
            <style>
                .pie-title { font-size: 16px; font-weight: bold; fill: #333; }
                .pie-label { font-size: 12px; fill: #666; }
                .pie-legend { font-size: 11px; }
            </style>
            <rect width="500" height="500" fill="#f9f9f9"/>
            <text x="250" y="25" text-anchor="middle" class="pie-title">''' + title + '''</text>'''
        
        colors = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60', '#3498db', '#9b59b6']
        current_angle = -90
        legend_x = 280
        legend_y = 150
        
        for idx, (label, value) in enumerate(sorted(data.items(), key=lambda x: x[1], reverse=True)):
            percentage = (value / total) * 100
            slice_angle = (value / total) * 360
            
            # Draw pie slice
            svg += HtmlReportGenerator._pie_slice_svg(
                cx=150, cy=150, r=100,
                start_angle=current_angle,
                angle=slice_angle,
                color=colors[idx % len(colors)]
            )
            
            # Add legend
            svg += f'''
            <rect x="{legend_x}" y="{legend_y}" width="15" height="15" fill="{colors[idx % len(colors)]}"/>
            <text x="{legend_x + 20}" y="{legend_y + 12}" class="pie-legend">{label}: {percentage:.1f}% ({value})</text>'''
            
            legend_y += 25
            current_angle += slice_angle
        
        svg += '''
        </svg>'''
        
        return svg
    
    @staticmethod
    def _pie_slice_svg(cx: int, cy: int, r: int, start_angle: float, angle: float, color: str) -> str:
        """Generate a single pie slice."""
        import math
        
        start_rad = math.radians(start_angle)
        end_rad = math.radians(start_angle + angle)
        
        x1 = cx + r * math.cos(start_rad)
        y1 = cy + r * math.sin(start_rad)
        x2 = cx + r * math.cos(end_rad)
        y2 = cy + r * math.sin(end_rad)
        
        large_arc = 1 if angle > 180 else 0
        
        path = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z"
        
        return f'<path d="{path}" fill="{color}" stroke="white" stroke-width="2"/>'
    
    @staticmethod
    def generate_html_report(reports: List[Dict], log_file: str) -> str:
        """Generate complete HTML report."""
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Aggregate findings
        all_findings = []
        severity_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        agent_count = {}
        
        for report in reports:
            for finding in report.get('findings', []):
                all_findings.append(finding)
                severity = finding.get('severity', 'UNKNOWN')
                if severity in severity_count:
                    severity_count[severity] += 1
                
                agent = finding.get('analysis_type', 'UNKNOWN')
                agent_count[agent] = agent_count.get(agent, 0) + 1
        
        # Generate charts
        severity_chart = HtmlReportGenerator.generate_chart_svg(
            'Findings by Severity',
            severity_count,
            'bar'
        )
        
        agent_chart = HtmlReportGenerator.generate_chart_svg(
            'Findings by Agent',
            agent_count,
            'bar'
        )
        
        # Calculate metrics
        total_findings = len(all_findings)
        critical_pct = (severity_count['CRITICAL'] / total_findings * 100) if total_findings > 0 else 0
        
        # Generate findings HTML
        findings_html = ""
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            severity_findings = [f for f in all_findings if f.get('severity') == severity]
            if severity_findings:
                severity_color = {'CRITICAL': '#e74c3c', 'HIGH': '#f39c12', 'MEDIUM': '#f1c40f', 'LOW': '#27ae60'}
                color = severity_color.get(severity, '#999')
                
                findings_html += f'''
                <div class="severity-section">
                    <h3 style="color: {color}; border-bottom: 3px solid {color}; padding-bottom: 10px;">
                        {severity} ({len(severity_findings)} findings)
                    </h3>'''
                
                for finding in severity_findings:
                    findings_html += f'''
                    <div class="finding-card">
                        <h4>{finding.get('title', 'Unknown')}</h4>
                        <p><strong>Type:</strong> {finding.get('finding_type', 'N/A')}</p>
                        <p><strong>Description:</strong> {finding.get('description', 'N/A')}</p>
                        <p><strong>Evidence:</strong> <code>{finding.get('evidence', 'N/A')}</code></p>
                        <p style="color: #27ae60; font-weight: bold;">
                            <strong>Action:</strong> {finding.get('recommended_action', 'N/A')}
                        </p>
                    </div>'''
                
                findings_html += '</div>'
        
        # Generate full HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .metric-number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
        }}
        
        .charts {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-container {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #eee;
            text-align: center;
        }}
        
        .chart-container svg {{
            max-width: 100%;
            height: auto;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        
        .severity-section {{
            margin-bottom: 30px;
        }}
        
        .severity-section h3 {{
            margin-bottom: 15px;
        }}
        
        .finding-card {{
            background: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        
        .finding-card h4 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .finding-card p {{
            margin: 8px 0;
            font-size: 13px;
            color: #555;
        }}
        
        .finding-card code {{
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        .footer {{
            background: #f9f9f9;
            padding: 20px;
            text-align: center;
            color: #999;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        
        @media (max-width: 768px) {{
            .metrics {{ grid-template-columns: repeat(2, 1fr); }}
            .charts {{ grid-template-columns: 1fr; }}
        }}
        
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; }}
            .header {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Analysis Report</h1>
            <p>Multi-Agent Log Analysis & Synthesis</p>
            <p>{log_file} | Generated: {now}</p>
        </div>
        
        <div class="content">
            <!-- Executive Summary Metrics -->
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-number">{total_findings}</div>
                    <div class="metric-label">Total Findings</div>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
                    <div class="metric-number">{severity_count['CRITICAL']}</div>
                    <div class="metric-label">Critical</div>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);">
                    <div class="metric-number">{severity_count['HIGH']}</div>
                    <div class="metric-label">High</div>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%);">
                    <div class="metric-number">{critical_pct:.1f}%</div>
                    <div class="metric-label">Critical Rate</div>
                </div>
            </div>
            
            <!-- Charts Section -->
            <div class="charts">
                <div class="chart-container">
                    {severity_chart}
                </div>
                <div class="chart-container">
                    {agent_chart}
                </div>
            </div>
            
            <!-- Executive Summary -->
            <div class="section">
                <h2>Executive Summary</h2>
                <p>This report presents a comprehensive multi-perspective analysis of the provided log file 
                using three specialized security agents:</p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li><strong>Security Agent:</strong> Detects threats, vulnerabilities, and compliance issues</li>
                    <li><strong>Data Quality Agent:</strong> Validates log format, timestamps, and structure</li>
                    <li><strong>Performance Agent:</strong> Analyzes system health, bottlenecks, and failures</li>
                </ul>
                
                <h3 style="margin-top: 20px; color: #667eea;">Key Findings</h3>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li>Total findings identified: <strong>{total_findings}</strong></li>
                    <li>Critical severity issues: <strong>{severity_count['CRITICAL']}</strong></li>
                    <li>High priority issues: <strong>{severity_count['HIGH']}</strong></li>
                    <li>Agents participating: <strong>{len(agent_count)}</strong></li>
                </ul>
            </div>
            
            <!-- Detailed Findings -->
            <div class="section">
                <h2>Detailed Findings</h2>
                {findings_html}
            </div>
            
            <!-- Recommendations Summary -->
            <div class="section">
                <h2>Action Items (Prioritized)</h2>
                <ol style="margin-left: 20px;">
'''
        
        # Add prioritized actions
        action_items = {}
        for finding in all_findings:
            action = finding.get('recommended_action', 'N/A')
            severity = finding.get('severity', 'LOW')
            if action not in action_items:
                action_items[action] = {'severity': severity, 'count': 0}
            action_items[action]['count'] += 1
        
        for idx, (action, details) in enumerate(sorted(action_items.items(), 
                                                       key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                                                                    .get(x[1]['severity'], 4)), 1):
            severity_color = {'CRITICAL': '#e74c3c', 'HIGH': '#f39c12', 'MEDIUM': '#f1c40f', 'LOW': '#27ae60'}
            color = severity_color.get(details['severity'], '#999')
            html += f'''
                    <li style="margin-bottom: 10px;">
                        <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">
                            {details['severity']}
                        </span>
                        {action} <em>({details['count']} finding(s))</em>
                    </li>'''
        
        html += '''
                </ol>
            </div>
            
            <!-- Analysis Metadata -->
            <div class="section">
                <h2>Analysis Metadata</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 10px; border: 1px solid #eee;"><strong>Log File</strong></td>
                        <td style="padding: 10px; border: 1px solid #eee;">''' + log_file + '''</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #eee;"><strong>Report Generated</strong></td>
                        <td style="padding: 10px; border: 1px solid #eee;">''' + now + '''</td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 10px; border: 1px solid #eee;"><strong>Agents Deployed</strong></td>
                        <td style="padding: 10px; border: 1px solid #eee;">''' + ', '.join(agent_count.keys()) + '''</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #eee;"><strong>Total Findings</strong></td>
                        <td style="padding: 10px; border: 1px solid #eee;">''' + str(total_findings) + '''</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>This report was generated by Multi-Agent Security Analysis Platform</p>
            <p>For more information, contact your security team</p>
        </div>
    </div>
</body>
</html>'''
        
        return html


# ============================================================================
# Synthesis Agent (Main)
# ============================================================================

class SynthesisAgent:
    """
    Synthesis Agent
    Aggregates findings from all agents and generates comprehensive reports.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def synthesize_reports(self, report_ids: List[int]) -> Dict[str, Any]:
        """
        Synthesize multiple reports into comprehensive analysis.
        
        Returns:
            Dict with:
            - summary: Executive summary
            - metrics: Aggregated metrics
            - charts_ascii: ASCII charts for terminal
            - charts_svg: SVG charts for HTML
            - html_report: Full HTML report
        """
        
        # Fetch all reports and findings
        reports = self._fetch_reports(report_ids)
        all_findings = self._aggregate_findings(reports)
        
        # Calculate metrics
        metrics = self._calculate_metrics(all_findings, reports)
        
        # Generate summary
        summary = self._generate_summary(all_findings, metrics)
        
        # Generate ASCII charts
        charts_ascii = self._generate_ascii_charts(all_findings)
        
        # Generate HTML report
        log_file = reports[0].get('log_file', 'Unknown') if reports else 'Unknown'
        html_report = HtmlReportGenerator.generate_html_report(reports, log_file)
        
        return {
            'summary': summary,
            'metrics': metrics,
            'charts_ascii': charts_ascii,
            'html_report': html_report,
            'findings_count': len(all_findings),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _fetch_reports(self, report_ids: List[int]) -> List[Dict]:
        """Fetch reports from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        reports = []
        for report_id in report_ids:
            cursor.execute('''
                SELECT id, log_file, analysis_type, risk_level, created_at
                FROM reports WHERE id = ?
            ''', (report_id,))
            
            report_row = cursor.fetchone()
            if report_row:
                report = {
                    'id': report_row[0],
                    'log_file': report_row[1],
                    'analysis_type': report_row[2],
                    'risk_level': report_row[3],
                    'created_at': report_row[4],
                    'findings': []
                }
                
                # Get findings for this report
                cursor.execute('''
                    SELECT id, analysis_type, finding_type, severity, title, description, evidence, recommended_action
                    FROM findings WHERE report_id = ?
                    ORDER BY severity DESC
                ''', (report_id,))
                
                for finding_row in cursor.fetchall():
                    report['findings'].append({
                        'id': finding_row[0],
                        'analysis_type': finding_row[1],
                        'finding_type': finding_row[2],
                        'severity': finding_row[3],
                        'title': finding_row[4],
                        'description': finding_row[5],
                        'evidence': finding_row[6],
                        'recommended_action': finding_row[7]
                    })
                
                reports.append(report)
        
        conn.close()
        return reports
    
    def _aggregate_findings(self, reports: List[Dict]) -> List[Dict]:
        """Combine all findings from all reports."""
        all_findings = []
        for report in reports:
            all_findings.extend(report.get('findings', []))
        return all_findings
    
    def _calculate_metrics(self, findings: List[Dict], reports: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive metrics."""
        
        # Severity breakdown
        severity_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            if severity in severity_count:
                severity_count[severity] += 1
        
        # Agent breakdown
        agent_count = {}
        for finding in findings:
            agent = finding.get('analysis_type', 'UNKNOWN')
            agent_count[agent] = agent_count.get(agent, 0) + 1
        
        # Finding type breakdown
        finding_type_count = {}
        for finding in findings:
            ftype = finding.get('finding_type', 'UNKNOWN')
            finding_type_count[ftype] = finding_type_count.get(ftype, 0) + 1
        
        # Calculate percentages
        total = len(findings)
        critical_pct = (severity_count['CRITICAL'] / total * 100) if total > 0 else 0
        high_pct = (severity_count['HIGH'] / total * 100) if total > 0 else 0
        
        return {
            'total_findings': total,
            'severity_breakdown': severity_count,
            'severity_percentages': {
                'CRITICAL': critical_pct,
                'HIGH': high_pct,
                'MEDIUM': (severity_count['MEDIUM'] / total * 100) if total > 0 else 0,
                'LOW': (severity_count['LOW'] / total * 100) if total > 0 else 0,
            },
            'agent_breakdown': agent_count,
            'finding_type_breakdown': finding_type_count,
            'total_reports': len(reports),
            'agents_used': list(agent_count.keys()),
            'risk_assessment': self._assess_overall_risk(severity_count),
        }
    
    def _assess_overall_risk(self, severity_count: Dict) -> str:
        """Assess overall risk level."""
        if severity_count['CRITICAL'] > 0:
            return 'CRITICAL'
        elif severity_count['HIGH'] > 3:
            return 'HIGH'
        elif severity_count['HIGH'] > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_summary(self, findings: List[Dict], metrics: Dict) -> str:
        """Generate executive summary text."""
        
        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║         EXECUTIVE SUMMARY - MULTI-AGENT SYNTHESIS              ║
╚════════════════════════════════════════════════════════════════╝

OVERALL RISK LEVEL: {metrics['risk_assessment']}

FINDINGS OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Findings: {metrics['total_findings']}
• Critical Issues: {metrics['severity_breakdown']['CRITICAL']} ({metrics['severity_percentages']['CRITICAL']:.1f}%)
• High Priority: {metrics['severity_breakdown']['HIGH']} ({metrics['severity_percentages']['HIGH']:.1f}%)
• Medium Priority: {metrics['severity_breakdown']['MEDIUM']} ({metrics['severity_percentages']['MEDIUM']:.1f}%)
• Low Priority: {metrics['severity_breakdown']['LOW']} ({metrics['severity_percentages']['LOW']:.1f}%)

AGENT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agents Deployed: {', '.join(metrics['agents_used'])}
Total Reports Generated: {metrics['total_reports']}

Agent Contribution:
"""
        
        for agent, count in metrics['agent_breakdown'].items():
            pct = (count / metrics['total_findings'] * 100) if metrics['total_findings'] > 0 else 0
            summary += f"  • {agent}: {count} findings ({pct:.1f}%)\n"
        
        summary += f"""
FINDING TYPES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for ftype, count in sorted(metrics['finding_type_breakdown'].items(), 
                                   key=lambda x: x[1], reverse=True):
            summary += f"  • {ftype}: {count}\n"
        
        summary += f"""
RECOMMENDATIONS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Issues require immediate action:
"""
        
        # Extract top recommendations
        recommendations = {}
        for finding in findings:
            if finding.get('severity') == 'CRITICAL':
                rec = finding.get('recommended_action', 'N/A')
                recommendations[rec] = recommendations.get(rec, 0) + 1
        
        for rec, count in sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary += f"  → {rec} ({count})\n"
        
        summary += f"""
REPORT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Format: Multi-Agent Synthesis Report
Status: Ready for distribution

╚════════════════════════════════════════════════════════════════╝
"""
        
        return summary
    
    def _generate_ascii_charts(self, findings: List[Dict]) -> str:
        """Generate ASCII charts."""
        
        # Severity distribution
        severity_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        agent_count = {}
        
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            if severity in severity_count:
                severity_count[severity] += 1
            
            agent = finding.get('analysis_type', 'UNKNOWN')
            agent_count[agent] = agent_count.get(agent, 0) + 1
        
        charts = AsciiCharts.bar_chart("Findings by Severity", severity_count)
        charts += AsciiCharts.bar_chart("Findings by Agent", agent_count)
        charts += AsciiCharts.pie_chart_text("Severity Distribution (Pie)", severity_count)
        
        return charts


# ============================================================================
# Export Functions
# ============================================================================

def save_html_report(html_content: str, output_path: str) -> str:
    """Save HTML report to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(path)


def save_summary_text(summary: str, output_path: str) -> str:
    """Save text summary to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    return str(path)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════╗
║            Synthesis Agent - Report Generation                 ║
╚════════════════════════════════════════════════════════════════╝

This agent synthesizes findings from multiple security agents
and generates comprehensive reports with charts and visualizations.

FEATURES:
  ✓ Aggregates findings from all agents
  ✓ Generates ASCII charts for terminal
  ✓ Generates SVG charts for HTML
  ✓ Creates professional HTML reports
  ✓ Calculates comprehensive metrics
  ✓ Provides executive summaries
  ✓ Prioritizes recommendations
  ✓ Ready for distribution

USAGE:
    from synthesis_agent import SynthesisAgent
    
    agent = SynthesisAgent('/tmp/workspace/security_monitor.db')
    result = agent.synthesize_reports([1, 2, 3])  # Report IDs
    
    # Display summary
    print(result['summary'])
    
    # Display ASCII charts
    print(result['charts_ascii'])
    
    # Save HTML report
    from synthesis_agent import save_html_report
    save_html_report(result['html_report'], '/tmp/workspace/report.html')

INTEGRATION:
    The Synthesis Agent integrates with:
    • web_app.py (database connection)
    • All three security agents (finding aggregation)
    • Report generation pipeline

    """)
