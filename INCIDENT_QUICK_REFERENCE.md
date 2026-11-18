# Incident Quick Reference Card

**Incident ID:** inc_001  
**Severity:** P0 - CRITICAL  
**Date:** 2024-01-15  
**Time:** 09:24:46 UTC  

---

## 🚨 Critical Status

| Component | Status | Action |
|-----------|--------|--------|
| **Payment Processing** | 🔴 DOWN | Failover to backup / Manual queue |
| **Load Balancer** | 🔴 DOWN | Restart nodes / Check health endpoints |
| **Database** | 🟠 CRITICAL | Increase pool 25→75, check integrity |
| **CPU** | 🔴 THERMAL | Cool down, reduce load, migrate workload |
| **Memory** | 🔴 87% | Restart app, force GC, increase heap |
| **Storage** | 🟠 90% | Purge logs, free 10GB immediately |

---

## ⚡ Immediate Actions (Next 5 min)

### Step 1: LOAD SHEDDING (60 sec)
```bash
# Cut API requests to 25% of normal
curl -X POST https://internal-api/emergency/shed-load

# Stop background jobs
kill $ETL_PID $BACKUP_PID
curl -X POST https://internal-api/services/email/pause

# Reduce logging
curl -X POST https://internal-api/monitoring/disable-collection
```

### Step 2: MEMORY RECOVERY (90 sec)
```bash
# Force garbage collection
jcmd $(pgrep -f java) GC.run

# Or restart app
systemctl restart app-server
# Wait: 60s for startup
```

### Step 3: DATABASE RECOVERY (5 min)
```bash
# Increase connection pool
curl -X POST https://internal-api/config/update \
  -d '{"database": {"pool_size": 75}}'

# Restart app
systemctl restart app-server
```

### Step 4: CHECK PAYMENT FAILOVER (5 min)
```bash
# Activate backup gateway
curl -X POST https://internal-api/payment/failover \
  -d '{"target": "backup"}'

# Queue failed transactions
curl -X POST https://internal-api/payment/retry-queue
```

---

## ✅ Verification Checklist

- [ ] Load shedding active (rate limit < 1000 req/min)
- [ ] Background jobs stopped
- [ ] Heap usage < 70%
- [ ] CPU temp < 80°C
- [ ] DB connections < 50 active
- [ ] Payment success rate > 85%
- [ ] LB reporting nodes healthy (4+ of 5)
- [ ] Storage free > 5GB
- [ ] API response time < 2s p95

---

## 📊 Key Metrics to Monitor

```
CPU Temp:     89°C  →  Target: < 75°C ✓
Memory Heap:  87%   →  Target: < 60%  ✓
DB Pool:      25/25 →  Target: < 50/75 ✓
Payment:      12%   →  Target: > 95% ✓
LB Nodes:     0/5   →  Target: 5/5 ✓
Cache Hit:    55%   →  Target: > 75% ✓
Storage:      90%   →  Target: < 80% ✓
```

---

## 📞 Escalation Chain

**0-5 min:** SRE/DevOps on-call  
**5-15 min:** Add Database DBA  
**15-30 min:** Add Engineering Manager  
**30+ min:** Add VP Engineering  
**Revenue impact $100K+:** Add Executive  

---

## 🔄 Phase Timeline

| Phase | Time | Actions |
|-------|------|---------|
| **Emergency** | 0-5 min | Load shed, restart, GC |
| **Recovery** | 5-30 min | Increase resources, failover |
| **Stabilization** | 30-60 min | Monitor, verify, optimize |
| **Analysis** | 60+ min | Post-mortem, root cause, prevention |

---

## 💥 Cascading Failure Chain

```
Cache Miss ↑ (45%)
    ↓
DB Load ↑  (more queries)
    ↓
Pool Exhaustion (25/25 connections)
    ↓
Timeouts (5sec wait → 30sec timeout)
    ↓
Payment Failures (8 lost orders)
    ↓
Load Spike (retry traffic)
    ↓
All LB Nodes Fail (0/5 healthy)
    ↓
COMPLETE OUTAGE
```

---

## 🛑 Root Causes Identified

1. **Undersized Cache** → 45% miss rate (should be < 25%)
2. **Connection Pool Too Small** → 25 connections insufficient
3. **No Circuit Breaker** → Failures cascade
4. **No Autoscaling** → Fixed 5 nodes
5. **Resource Monitoring Too Late** → 80% threshold vs 70%
6. **Data Integrity Issues** → 234 inconsistencies in DB

---

## 🚀 Quick Fixes

| Issue | Quick Fix | Time |
|-------|-----------|------|
| High CPU Temp | Reduce load + increase cooling | 5 min |
| High Memory | Restart app + force GC | 3 min |
| DB Pool Full | Increase pool size + restart | 10 min |
| Payment Down | Failover to backup gateway | 5 min |
| LB Nodes Down | Restart nodes + check health | 10 min |
| Storage Full | Purge old logs | 5 min |

---

## 📈 Post-Incident Actions

**Today (Within 24h):**
- [ ] Post-mortem meeting
- [ ] Document lessons learned
- [ ] Plan follow-up fixes

**This Week:**
- [ ] Increase connection pool to 50-75
- [ ] Expand cache infrastructure
- [ ] Upgrade CPU cooling
- [ ] Implement circuit breakers

**This Month:**
- [ ] Auto-scaling implementation
- [ ] SLO monitoring setup
- [ ] Chaos engineering tests
- [ ] Capacity upgrade

---

## 🔗 Related Documents

- **SYSTEM_ANALYSIS_REPORT.md** - Complete technical analysis
- **EXECUTIVE_SUMMARY.md** - Leadership overview
- **REMEDIATION_RUNBOOK.md** - Step-by-step recovery procedures
- **DETAILED_METRICS.md** - Metric deep-dives and correlation analysis

---

## 📝 Notes Section

```
Action Log:
[09:24:47] Incident declared - all nodes down
[09:24:XX] Load shedding activated
[09:25:XX] App server restarted
[09:25:XX] Payment failover initiated
[09:26:XX] System stabilizing...
```

---

## 🆘 Emergency Contact Info

**On-Call SRE:** [Page immediately]  
**Database DBA:** [Page after 5 min if not resolved]  
**Engineering Lead:** [Page after 15 min if not resolved]  
**VP Engineering:** [Notify after 30 min outage]  

**Status Page URL:** https://status.company.com  
**Incident Channel:** #incident-response on Slack  
**Escalation Hotline:** +1-555-INC-1DEX  

---

## Key Numbers to Remember

- **CPU Threshold:** 85°C (current: 89°C ⚠️)
- **Memory Threshold:** 80% (current: 87% ⚠️)
- **DB Pool Size:** 25 (need: 75 💥)
- **Payment Success:** 12% (expected: 95%+ ⚠️)
- **Cache Hit Rate:** 55% (target: 75%+ ⚠️)
- **LB Nodes:** 0/5 (need: 5/5 ⚠️)
- **Storage Free:** ~5GB (critical when < 2GB)
- **Failed Orders:** 8+ (revenue impact: $1500+)

---

**Last Updated:** 2024-01-15T09:24:47Z  
**Document Version:** 1.0  
**Classification:** INCIDENT - Highly Confidential
