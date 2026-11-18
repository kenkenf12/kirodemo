# Remediation Runbook: Critical System Outage Recovery

**Last Updated:** 2024-01-15T09:24:47Z  
**Incident ID:** inc_001  
**Severity:** P0 - CRITICAL  

---

## Quick Reference: Action Priority Matrix

```
┌─────────────────────────────────────────────────────────┐
│ TIMELINE │ ACTION                      │ TIME    │ WHO  │
├─────────────────────────────────────────────────────────┤
│ NOW      │ Shed load (emergency)       │ <1 min  │ Ops  │
│ NOW      │ Stop background jobs        │ <1 min  │ Ops  │
│ 0-5 min  │ Restart app server          │ 3 min   │ Ops  │
│ 0-5 min  │ Force GC, free memory       │ 1 min   │ Ops  │
│ 5-15 min │ Increase DB pool size       │ 10 min  │ DBA  │
│ 5-15 min │ Check Payment failover      │ 5 min   │ Ops  │
│ 15-30 min│ Database integrity check    │ 15 min  │ DBA  │
│ 30+ min  │ Expand cache infrastructure │ 30+ min │ Arch │
└─────────────────────────────────────────────────────────┘
```

---

## PHASE 1: EMERGENCY MITIGATION (0-5 Minutes)

### Step 1.1: Activate Emergency Load Shedding
**Purpose:** Stop cascading failures by reducing load  
**Estimated Time:** 1 minute  
**Responsible:** DevOps/SRE Lead

**Actions:**
```
1. Enable API rate limiting (aggressive mode)
   - Set all endpoints to 1000 req/min (from current 5000)
   - Whitelist critical payment endpoints only
   - Block: analytics, exports, admin operations

2. Shutdown non-critical services
   - Stop ETL pipeline (etl_daily_001)
   - Stop backup service (backup already failed)
   - Stop large data exports
   - Stop email service (queue delayed anyway)

3. Switch to degraded mode
   - Reduce returned data sets (limit query results to 1000 rows)
   - Disable non-critical monitoring
   - Enable priority traffic mode (payments > auth > core > everything else)

4. Notify customers (if possible)
   - Status page: "Experiencing temporary payment processing delays"
   - Estimated recovery: 15-30 minutes
```

**Verification:**
```
$ curl https://api.company.com/health
Status: Check response time (should improve within 30s)

$ curl https://api.company.com/status
Check for rate limit responses (429 status codes expected)

Monitor: System load average should drop within 1 minute
```

---

### Step 1.2: Stop Non-Essential Background Jobs
**Purpose:** Free memory and CPU resources  
**Estimated Time:** 2 minutes  
**Responsible:** DevOps/Application Team

**Actions:**
```
# Kill ETL process
$ kill <etl_job_pid>    # Job: etl_daily_001

# Stop email delivery (gracefully)
$ curl -X POST https://internal-api/services/email/pause
Response expected: {"status": "paused", "queue_retained": true}

# Stop backup service (already failed, but ensure stopped)
$ kill <backup_job_pid>  # Job: job_bkp_001

# Disable non-critical monitoring
$ curl -X POST https://internal-monitoring/disable-collection \
  -d '{"services": ["analytics", "non_critical_metrics"]}'
```

**Verification:**
```
$ ps aux | grep -E 'etl_daily|backup|email'
Result: No running processes found (or graceful shutdown confirmed)

$ free -h
Check: Memory usage should decrease by 10-15% within 2 minutes
```

---

### Step 1.3: Force Java Garbage Collection
**Purpose:** Immediately free memory (currently 87% heap utilization)  
**Estimated Time:** 1-2 minutes  
**Responsible:** DevOps

**Actions:**
```
# Trigger full garbage collection on JVM process
$ jcmd <java_pid> GC.run

# Alternative if jcmd unavailable (restart application)
$ systemctl restart app-server
# Wait for service to come back online (typically 30-60 seconds)

# Monitor heap during/after GC
$ jps -lm | grep java
$ jcmd <java_pid> GC.heap_dump_on_out_of_memory_error
```

**Expected Outcome:**
- Heap usage drops from 87% to 40-60% range
- Response times improve
- No new OutOfMemoryError exceptions

**Verification:**
```
$ jcmd <java_pid> VM.heap_dump_on_out_of_memory_error
$ curl https://api.company.com/metrics/jvm/memory
Expected: heap_usage < 70% within 2 minutes
```

---

### Step 1.4: Initial Resource Status Check
**Purpose:** Baseline current state after initial mitigation  
**Estimated Time:** 1 minute  
**Responsible:** DevOps/SRE

**Check:**
```bash
# System Resources
$ top -bn1 | head -20
Expected: CPU < 80%, Load average decreasing

# Memory
$ free -h
Expected: Used < 70%, Heap < 60%

# Disk
$ df -h /
Expected: Available > 5GB (currently 5GB free)

# Network
$ ss -s | grep -E "TCP|UDP"
Expected: Connection count < 1000

# Database Connections
$ mysql -e "SELECT COUNT(*) FROM information_schema.processlist"
Expected: < 15 connections (down from 25)

# Service Health
$ curl https://api.company.com/health
Expected: Response time < 2s, all critical services responding
```

**Decision Point:**
- If systems responding: Continue to Phase 2
- If still critical: Execute immediate failover procedures (see Appendix)

---

## PHASE 2: CAPACITY RECOVERY (5-30 Minutes)

### Step 2.1: Increase Database Connection Pool
**Purpose:** Remove connection pool as bottleneck  
**Estimated Time:** 10-15 minutes  
**Responsible:** Database Administrator

**Current State:**
```
Connection Pool Size: 25 (100% utilized)
Pending Requests: 12
Response: Timeout after 5000ms
```

**Actions:**

**Option A: Dynamic Configuration Update (Preferred if supported)**
```
# Update configuration
$ curl -X POST https://internal-api/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "database": {
      "pool_size": 75,
      "max_idle_time": 300000,
      "connection_timeout": 30000
    }
  }'

# Restart application to apply
$ systemctl restart app-server
Wait: 60 seconds for service to stabilize

# Verify new pool size
$ mysql -e "SHOW PROCESSLIST" | wc -l
Expected: Should now support up to 75 connections
```

**Option B: Database Configuration File Update**
```
# Edit /etc/mysql/my.cnf or connection config
[database]
pool_size=75
max_connections=100

# Restart database service
$ systemctl restart mysql

# Verify
$ mysql -e "SHOW VARIABLES LIKE 'max_connections'"
Expected: 100 or higher
```

**Option C: Application Restart with New Settings**
```bash
# Update application config file
$ vi /opt/app/config/database.yml
# Change: pool_size: 75

# Restart app
$ systemctl restart app-server

# Monitor startup
$ tail -f /var/log/app-server.log
Wait for: "Connection pool initialized with 75 connections"
```

**Verification:**
```sql
-- Monitor new connection pool
SELECT 
  COUNT(*) as active_connections,
  MAX(TIMESTAMPDIFF(SECOND, last_query, NOW())) as idle_seconds
FROM information_schema.processlist;

-- Expected: active_connections < 30, idle connections available
-- Should see pending_requests dropping

-- Check pending queue
SELECT 
  SUM(CASE WHEN command != 'Sleep' THEN 1 ELSE 0 END) as active,
  SUM(CASE WHEN command = 'Sleep' THEN 1 ELSE 0 END) as idle
FROM information_schema.processlist;
```

**Rollback Plan:**
```
If increased pool causes resource contention:
$ curl -X POST https://internal-api/config/update \
  -d '{"database": {"pool_size": 40}}'
$ systemctl restart app-server
```

---

### Step 2.2: Check Payment Processing Failover
**Purpose:** Restore payment processing capability  
**Estimated Time:** 5-10 minutes  
**Responsible:** Payment Systems Team

**Current Issue:**
```
Payment Gateway: Timeout (30+ seconds)
Success Rate: 12% (should be 95%+)
Failed Orders: 8 in 5-minute window
```

**Actions:**

**If Backup Payment Gateway Available:**
```bash
# Failover to backup gateway
$ curl -X POST https://internal-api/payment/failover \
  -d '{"target": "backup_gateway", "primary": "primary_gateway"}'

# Monitor traffic
$ tail -f /var/log/payment-gateway.log

# Verify: Check success rate
$ curl https://internal-api/metrics/payment/success_rate
Expected: Should increase from 12% to 85%+ within 2 minutes
```

**If No Backup Gateway:**
```bash
# Increase timeout threshold temporarily
$ curl -X POST https://internal-api/payment/config \
  -d '{
    "timeout_ms": 60000,
    "retry_enabled": true,
    "retry_count": 3,
    "circuit_breaker_threshold": 0.5
  }'

# Resume payment processing
$ curl -X POST https://internal-api/payment/resume

# Monitor
$ curl https://internal-api/metrics/payment/transactions
Expected: New transactions being processed
```

**Queue Failed Transactions:**
```bash
# Retry failed transactions from queue
$ curl -X POST https://internal-api/payment/retry-queue \
  -d '{"order_ids": ["ord_12345", ...], "max_parallel": 5}'

# Monitor retry progress
$ tail -f /var/log/payment-retry.log
Expected: Messages like "Retrying order ord_12345..."
```

**Verification:**
```bash
# Check payment metrics
$ curl https://api.company.com/metrics/payment
Expected output example:
{
  "success_rate": 0.92,
  "average_response_time_ms": 2400,
  "failed_orders_in_5min": 0,
  "queue_depth": 3
}

# Should see:
# - success_rate > 85%
# - response_time < 5000ms
# - failed_orders = 0
```

---

### Step 2.3: Restart Load Balancer
**Purpose:** Recover from all-nodes-down state  
**Estimated Time:** 5-10 minutes  
**Responsible:** DevOps/Infrastructure Team

**Current Issue:**
```
Load Balancer: 0/5 nodes healthy (all failed)
Status: NO TRAFFIC REROUTE POSSIBLE
Incident: inc_001
```

**Actions:**

**Step 1: Check Node Health Individually**
```bash
# Check each node's health endpoint
for i in {1..5}; do
  node="server_0${i}"
  echo "Checking $node..."
  curl -s -m 5 "http://10.0.2.${i}:8080/health" && echo "$node OK" || echo "$node DOWN"
done

# Expected: Some nodes should respond (if they're actually down vs connection timeout)
```

**Step 2: Restart Individual Nodes (if running but unhealthy)**
```bash
# For each unhealthy node (e.g., server_05)
$ ssh app-server-05
$ systemctl status app-service
$ systemctl restart app-service
$ sleep 30
$ systemctl status app-service
# Wait for: "active (running)"

# Verify node is responding
$ curl http://10.0.2.5:8080/health
Expected: HTTP 200 OK
```

**Step 3: Update Load Balancer Configuration**
```bash
# Reduce health check timeout (currently 15s, too aggressive)
$ vi /etc/nginx/conf.d/upstream.conf
# Change: proxy_connect_timeout 5s;  (from 15s)

# Reload nginx
$ nginx -s reload

# Verify
$ nginx -t
Expected: "configuration file is OK"
```

**Step 4: Re-enable Load Balancer**
```bash
# Manually trigger health check update
$ curl -X POST https://internal-api/lb/healthcheck/force-update

# Monitor node status in real-time
$ watch -n 1 'curl -s https://internal-api/lb/status | jq ".nodes"'

# Expected: Nodes should transition to "healthy" within 30 seconds
```

**Verification:**
```bash
# Check load balancer status
$ curl https://internal-api/lb/status
Expected:
{
  "healthy_nodes": 5,
  "total_nodes": 5,
  "status": "operational",
  "traffic_reroute": true,
  "incident_id": null
}

# Traffic should resume flowing through all nodes
$ curl https://api.company.com/health
Expected: Response time < 2s
```

---

### Step 2.4: Database Integrity Check (Run in Background)
**Purpose:** Identify and repair corruption (234 inconsistencies detected)  
**Estimated Time:** 15-30 minutes  
**Responsible:** Database Administrator  
**Note:** Can run parallel with other steps; does not block service recovery

**Current Issue:**
```
Inconsistencies Found: 234
Orphaned References: Detected in users table
Table Checked: users (1,000,000 rows)
```

**Actions:**

**Non-Blocking Background Check:**
```bash
# Run in screen/tmux session or background
$ screen -S db-repair -d -m bash -c '
  # Start integrity check (low priority)
  mysql --batch << EOF
  
  -- Check for orphaned foreign keys
  SELECT 
    t1.*, t2.id IS NULL as is_orphaned
  FROM orders t1
  LEFT JOIN customers t2 ON t1.customer_id = t2.id
  WHERE t2.id IS NULL
  LIMIT 100;
  
  -- Repair corrupted tables
  REPAIR TABLE users, orders, customers;
  
  -- Rebuild indices
  OPTIMIZE TABLE users;
  
  EOF
'

# Monitor progress
$ tail -f /var/log/mysql-repair.log
```

**Blocking Repair (if inconsistencies critical):**
```bash
# Put database in maintenance mode
$ curl -X POST https://internal-api/maintenance/enable \
  -d '{"message": "Database integrity repair in progress"}'

# Run comprehensive check
$ mysqlcheck -u root -p --all-databases --repair --check-upgrade

# Exit maintenance mode
$ curl -X POST https://internal-api/maintenance/disable
```

**Verification:**
```sql
-- Verify repairs
SELECT 
  TABLE_NAME,
  CHECK_TIME,
  MSG_TEXT
FROM information_schema.TABLES t
LEFT JOIN information_schema.CHECK_CONSTRAINTS c 
  ON t.TABLE_SCHEMA = c.CONSTRAINT_SCHEMA
WHERE t.TABLE_SCHEMA = 'production';

-- Check specific table
CHECK TABLE users;
Expected: Table is ok

-- Count inconsistencies after repair
SELECT COUNT(*) 
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE c.id IS NULL;
Expected: 0 (was 234)
```

---

## PHASE 3: PERFORMANCE OPTIMIZATION (30-60 Minutes)

### Step 3.1: Expand and Optimize Cache
**Purpose:** Reduce cache miss rate from 45% to <25%  
**Estimated Time:** 20-30 minutes  
**Responsible:** Infrastructure/Cache Team

**Current State:**
```
Hit Rate: 55%
Miss Rate: 45% (high)
Latency: 1250ms per cache operation
```

**Actions:**

**Option A: Increase Cache Memory (if Redis/Memcached)**
```bash
# Check current cache size
$ redis-cli INFO memory
# Look for: used_memory_human

# Increase memory allocation
$ redis-cli CONFIG SET maxmemory 4gb
$ redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Persist changes
$ redis-cli CONFIG REWRITE

# Verify
$ redis-cli INFO memory | grep maxmemory
Expected: maxmemory = 4gb
```

**Option B: Adjust Cache TTL Strategy**
```bash
# Review current TTL settings
$ grep -r "TTL" /opt/app/config/cache.yml

# Update aggressive caching config
cache:
  ttl:
    user_profiles: 3600      # 1 hour
    product_data: 7200       # 2 hours
    payment_status: 300      # 5 minutes (short for accuracy)
    session_cache: 600       # 10 minutes
  
  eviction_policy: LRU
  max_size: 4gb

# Restart cache service
$ systemctl restart redis
```

**Option C: Implement Cache Warming**
```bash
# Pre-populate cache with frequently accessed data
$ curl -X POST https://internal-api/cache/warm \
  -d '{
    "categories": ["user_profiles", "product_data", "api_responses"],
    "parallel_workers": 8
  }'

# Monitor warming progress
$ tail -f /var/log/cache-warming.log
Expected: Messages like "Warmed 10,000 user profiles..."
```

**Verification:**
```bash
# Check cache metrics after optimization
$ curl https://internal-api/metrics/cache
Expected:
{
  "hit_rate": 0.75,        # Up from 0.55
  "miss_rate": 0.25,       # Down from 0.45
  "avg_latency_ms": 45,    # Down from 1250ms
  "memory_usage": "3.2GB"
}

# Monitor in real-time
$ watch -n 2 'redis-cli INFO stats'
```

---

### Step 3.2: Scale Metrics Collection
**Purpose:** Reduce high cardinality metric issue (15K labels vs 10K threshold)  
**Estimated Time:** 10-15 minutes  
**Responsible:** Monitoring/SRE Team

**Current Issue:**
```
Metric: api_response_time
Label Cardinality: 15,000 (50% over threshold)
Threshold: 10,000 labels
```

**Actions:**

**Reduce Label Cardinality:**
```yaml
# Update Prometheus/metrics configuration
metrics:
  api_response_time:
    # OLD: Labels for every unique URL, method, status, timestamp
    labels: [endpoint, method, status, user_id, region]  # 15K combinations
    
    # NEW: Consolidated labels
    labels: [endpoint, method, status_code_range]  # ~500 combinations
    
  # Implement label aggregation
  aggregation:
    status_code_range:
      "2xx": [200, 201, 202, 204]
      "3xx": [300, 301, 304]
      "4xx": [400, 401, 403, 404]
      "5xx": [500, 502, 503]
    
    response_time_bucket: [<100ms, 100-500ms, 500-1000ms, >1000ms]

# Restart metrics collection
$ systemctl restart prometheus-scraper
```

**Archive Old Metrics:**
```bash
# Move high-cardinality metrics to archive
$ prometheus-backup \
  --source=/var/lib/prometheus/api_response_time.tsdb \
  --destination=/archive/metrics/api_response_time_$(date +%Y%m%d).tar.gz

# Purge old metric entries
$ promtool query instant 'api_response_time' \
  --retention=30d \
  --prune
```

**Verification:**
```bash
# Check new cardinality
$ curl https://internal-api/metrics/cardinality
Expected:
{
  "api_response_time": 450,    # Down from 15,000
  "total_series": "50,000",    # Down from 200,000
  "status": "within_threshold"
}
```

---

### Step 3.3: Monitor and Stabilize System
**Purpose:** Confirm system stability after recovery  
**Estimated Time:** 10 minutes ongoing  
**Responsible:** SRE/On-Call Team

**Actions:**

**Establish Baseline Metrics:**
```bash
# Create monitoring dashboard
metrics_to_track=(
  "cpu_temperature"
  "memory_heap_usage"
  "database_connection_pool"
  "payment_success_rate"
  "api_response_time_p95"
  "cache_hit_rate"
  "load_balancer_healthy_nodes"
  "disk_free_space"
)

# Alert thresholds (NEW - more aggressive monitoring)
alerts:
  cpu_temperature:
    warning: 75°C  # Down from 85°C
    critical: 82°C # Down from 89°C
  
  memory_heap:
    warning: 70%   # Down from 80%
    critical: 80%  # Down from 87%
  
  database_connections:
    warning: 60%   # Down from 100%
    critical: 75%
  
  disk_space:
    warning: 75%   # Down from 90%
    critical: 85%
```

**Real-Time Monitoring Script:**
```bash
#!/bin/bash
# Monitor critical metrics every 10 seconds
while true; do
  echo "=== System Status $(date) ==="
  
  # CPU & Memory
  top -bn1 | head -15
  
  # Database
  mysql -e "SELECT COUNT(*) FROM information_schema.processlist;"
  
  # Disk
  df -h / | tail -1
  
  # Services
  curl -s https://api.company.com/health | jq '.services'
  
  # Payment metrics
  curl -s https://internal-api/metrics/payment | jq '.success_rate'
  
  sleep 10
done
```

**Verification Checklist:**
```
☐ CPU Temperature: < 75°C
☐ Memory Heap: < 70%
☐ DB Connections: < 60% utilized
☐ Payment Success: > 95%
☐ API Response Time (p95): < 2s
☐ Cache Hit Rate: > 75%
☐ Load Balancer: 5/5 nodes healthy
☐ Disk Free: > 15GB
☐ No error messages in logs
☐ Customer complaints resolved
```

---

## PHASE 4: HARDENING & PREVENTION (1-7 Days)

### Step 4.1: Implement Circuit Breaker Pattern
**Purpose:** Prevent cascading failures  
**Timeline:** Complete within 2 days  
**Responsible:** Architecture Team

**For Payment Gateway:**
```java
@CircuitBreaker(
  failureThreshold = 5,        // Fail after 5 errors
  delay = 60000,               // Wait 60s before retry
  failureRateThreshold = 0.5   // Fail if 50% of requests fail
)
public PaymentResponse processPayment(Order order) {
  return paymentGateway.process(order);
}
```

**For Database Layer:**
```java
@CircuitBreaker(
  failureThreshold = 10,
  delay = 30000,
  failureRateThreshold = 0.3
)
public List<Customer> getCustomers() {
  return database.query("SELECT * FROM customers");
}
```

---

### Step 4.2: Implement Bulkhead Pattern
**Purpose:** Isolate resources by service  
**Timeline:** Complete within 2 days  
**Responsible:** Architecture Team

```yaml
resourceIsolation:
  payment:
    threads: 20
    queue_size: 100
  
  analytics:
    threads: 5
    queue_size: 50
  
  auth:
    threads: 10
    queue_size: 100
```

---

### Step 4.3: Security Hardening
**Purpose:** Address brute force attack and unauthorized access  
**Timeline:** Complete this week  
**Responsible:** Security Team

**Actions:**
1. Investigate brute force attack: `203.45.123.89` (15 attempts)
2. Implement CAPTCHA after 3 failed login attempts
3. Review unauthorized access attempt: `usr_001` accessing `/admin/settings`
4. Enable adaptive authentication
5. Implement WAF (Web Application Firewall) rules

---

### Step 4.4: Capacity Planning
**Purpose:** Prevent recurrence  
**Timeline:** Plan this week, execute next quarter  
**Responsible:** Infrastructure Team

**Upgrades Needed:**
- CPU: Upgrade or add cooling (currently throttling at 89°C)
- Memory: Increase total system RAM by 50%
- Storage: Add 500GB SSD for logs
- Database: Upgrade connection pool infrastructure
- Network: Evaluate bandwidth constraints

---

## Appendix: Failover Procedures

### Emergency Failover Checklist

If mitigation steps don't restore service within 15 minutes:

```
FAILOVER PROCEDURE:

1. DECLARE FAILOVER MODE
   $ curl -X POST https://internal-api/failover/declare \
     -d '{"mode": "complete", "target_region": "us-west-2"}'

2. SWITCH LOAD BALANCER
   $ aws route53 change-resource-record-sets \
     --hosted-zone-id Z123456 \
     --change-batch 'file://failover.json'

3. DATABASE FAILOVER
   $ mysql -e "STOP SLAVE; SET GLOBAL read_only=OFF;"
   # Promote replica to master

4. UPDATE CUSTOMER STATUS
   $ STATUS_PAGE_API=/update \
     -d '{"status": "Failover in progress", "eta": "15 minutes"}'

5. VERIFY FAILOVER COMPLETE
   $ curl https://api.company.com/health
   Expected: All systems operational in failover region

6. NOTIFY STAKEHOLDERS
   - Send notifications to all service owners
   - Post incident channel update
   - Begin incident review process
```

---

## Post-Incident Actions

### Immediate (Within 24 hours)
- [ ] Complete incident post-mortem
- [ ] Document all actions taken
- [ ] Identify lessons learned
- [ ] Plan follow-up tasks

### Short-term (Within 1 week)
- [ ] Implement circuit breakers
- [ ] Increase monitoring thresholds
- [ ] Upgrade infrastructure as needed
- [ ] Review and update runbooks

### Long-term (Within 30 days)
- [ ] Complete capacity upgrade
- [ ] Implement auto-scaling
- [ ] Deploy chaos engineering tests
- [ ] Review SLOs and update targets

---

## Contact & Escalation

**On-Call Chain:**
1. **SRE/DevOps Lead:** Page immediately
2. **Database Administrator:** If DB issues persist > 10 min
3. **Engineering Manager:** If recovery > 30 min
4. **VP Engineering:** If customer-facing outage > 5 min
5. **Executive Team:** If revenue impact > $100K or > 1 hour outage

**Communication Channels:**
- **Real-time:** Slack #incident-response
- **Status:** Status page updates every 5 minutes
- **Customers:** Email notification if > 15 min outage
- **Post-mortem:** Scheduled within 24 hours

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | SRE Team | Initial runbook creation |
| | | | - Phase 1-4 procedures |
| | | | - Failover procedures |
| | | | - Appendix and contacts |
