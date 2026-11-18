#!/usr/bin/env python3
"""
Test script for log monitor - demonstrates the monitoring loop with one file check.
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from log_monitor import LogMonitoringLoop


def main():
    """Run one iteration of the monitoring loop."""
    workspace_root = str(Path(__file__).parent)
    
    print("\n" + "=" * 80)
    print("LOG MONITOR TEST - Single Iteration")
    print("=" * 80 + "\n")
    
    # Create monitor
    monitor = LogMonitoringLoop(
        watch_dir=workspace_root,
        workspace_root=workspace_root,
        interval=2
    )
    
    print(f"Workspace: {workspace_root}")
    print(f"Watch Directory: {workspace_root}")
    print(f"Check Interval: 2 seconds\n")
    
    # Check for changes once
    print("[Test] Checking for log files...\n")
    changed_files = monitor.watcher.get_changed_files()
    
    if changed_files:
        print(f"[Test] Found {len(changed_files)} file(s):\n")
        
        for file_path, change_type in changed_files:
            print(f"  File: {file_path}")
            print(f"  Change Type: {change_type}\n")
            
            # Process each file
            monitor._process_log_file(file_path, change_type, 1)
    else:
        print("[Test] No log files found in workspace")
        print("[Test] Creating test scenario...\n")
        
        # Create a sample log file for testing
        test_log_path = Path(workspace_root) / "test_application.log"
        
        print(f"Creating test log file: {test_log_path}\n")
        
        with open(test_log_path, 'w') as f:
            f.write("""2024-01-15T09:23:15.847Z [INFO] [AuthService] User login attempt - user_id=usr_001 email=john.doe@company.com ip=192.168.1.105
2024-01-15T09:24:02.156Z [ERROR] [PaymentGateway] Payment processing failed - order_id=ord_12345 amount=USD_1500.00 error_code=GATEWAY_TIMEOUT
2024-01-15T09:24:06.234Z [CRITICAL] [PaymentGateway] Multiple payment failures - failures_in_5min=8 success_rate=0.12
2024-01-15T09:24:18.901Z [WARN] [SecurityAudit] Suspicious login attempts detected - source_ip=203.45.123.89 attempt_count=15 brute force
2024-01-15T09:24:20.567Z [ERROR] [APIGateway] Rate limit exceeded - client_id=api_key_5f4d9e2a calls_per_minute=5001
2024-01-15T09:24:30.345Z [ERROR] [AnalyticsEngine] ETL job failed - error="Out of memory"
2024-01-15T09:24:31.678Z [CRITICAL] [SystemMonitor] Server CPU temperature critical - temp_celsius=89 threshold=85
2024-01-15T09:24:38.789Z [CRITICAL] [DataIntegrity] Database integrity check failed - inconsistencies_found=234
2024-01-15T09:24:46.123Z [ERROR] [LoadBalancer] All nodes unhealthy - healthy_nodes=0 total_nodes=5
""")
        
        print("[Test] Test log file created!\n")
        print("[Test] Re-checking for changes...\n")
        
        # Clear snapshot cache and check again
        monitor.watcher.snapshots.clear()
        changed_files = monitor.watcher.get_changed_files()
        
        if changed_files:
            for file_path, change_type in changed_files:
                print(f"[Test] Detected: {file_path} ({change_type})\n")
                monitor._process_log_file(file_path, change_type, 1)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
