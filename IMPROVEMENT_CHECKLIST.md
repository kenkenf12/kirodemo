# Logging Standards Improvement Checklist

Track progress on raising log quality from 7.5/10 to 9/10.

---

## 🔴 Phase 1: Critical (Must Do First)

### Trace Context Implementation

- [ ] **Install OpenTelemetry libraries**
  - [ ] npm install @opentelemetry/api @opentelemetry/sdk-node
  - [ ] npm install @opentelemetry/auto (for Node.js)
  - [ ] Create otel-config.js with initialization

- [ ] **Create trace middleware**
  - [ ] Middleware that injects trace_id, span_id into every request
  - [ ] Pass context to logger throughout request lifetime
  - [ ] Test: Generate request, verify all logs have trace_id

- [ ] **Update all logger calls**
  - [ ] Find all logger.info/error/warn/debug calls
  - [ ] Add trace_id, span_id, context to each call
  - [ ] Use automated context propagation where possible

- [ ] **Enable distributed tracing**
  - [ ] Configure tracer to export spans
  - [ ] Test with APM tool (Jaeger, Datadog, or New Relic)

### PII Masking

- [ ] **Identify sensitive fields**
  - [ ] [ ] email
  - [ ] [ ] phone
  - [ ] [ ] credit_card
  - [ ] [ ] ssn
  - [ ] [ ] api_key
  - [ ] [ ] access_key
  - [ ] [ ] secret_key
  - [ ] [ ] password
  - [ ] [ ] bearer_token

- [ ] **Grep for PII patterns**
  - [ ] `grep -r "email" app.log`
  - [ ] `grep -r "AKIA\|access_key" app.log`
  - [ ] `grep -r "credit_card\|card_number" app.log`

- [ ] **Create sanitization function**
  - [ ] Regex patterns for each PII type
  - [ ] Test sanitization function
  - [ ] Add to logging middleware

- [ ] **Update logging calls**
  - [ ] Replace `email: user.email` with `user_id: user.id`
  - [ ] Replace credential logging with `credential_type` + `credential_id`
  - [ ] Remove unnecessary sensitive data entirely

- [ ] **Verify PII removal**
  - [ ] Run grep patterns again; should find 0 results
  - [ ] Deploy to staging
  - [ ] Monitor logs for 24 hours

### JSON Format Migration

- [ ] **Update logger configuration**
  - [ ] Switch to JSON output format
  - [ ] Enable JSON formatting in pino/winston/structlog
  - [ ] Test single log entry; verify it's valid JSON

- [ ] **Update all logger calls**
  - [ ] Structured objects instead of string concatenation
  - [ ] Ensure all values are properly escaped
  - [ ] Test complex values (quotes, newlines, special chars)

- [ ] **Update log parsing in tools**
  - [ ] Splunk: Update props.conf for JSON parsing
  - [ ] ELK: Disable custom grok patterns
  - [ ] Datadog: Verify automatic JSON parsing

- [ ] **Verify JSON output**
  - [ ] `jq . app.log` should parse without errors
  - [ ] Sample 100 entries; all valid JSON

---

## 🟠 Phase 2: Important (Week 2)

### Request & Session Context

- [ ] **Create context structure**
  ```json
  {
    "trace_id": "uuid",
    "request_id": "uuid", 
    "session_id": "uuid",
    "user_id": "user_123",
    "tenant_id": "tenant_456",
    "environment": "prod"
  }
  ```

- [ ] **Add to middleware**
  - [ ] Extract session_id from cookies/JWT
  - [ ] Generate request_id for each HTTP request
  - [ ] Pass to logger

- [ ] **Update logging calls**
  - [ ] Include session_id in user-initiated operations
  - [ ] Include request_id for API calls
  - [ ] Include tenant_id for multi-tenant systems

- [ ] **Test context propagation**
  - [ ] Make API call; trace single request_id through all logs
  - [ ] Verify session_id groups all user operations

### Source Location Metadata

- [ ] **Add getSourceLocation() function**
  - [ ] Extract file, line, column from Error.stack
  - [ ] Test with sample calls

- [ ] **Integrate into logger**
  - [ ] Auto-inject on every log call
  - [ ] Or configure logger library to do this natively

- [ ] **Verify in logs**
  - [ ] Sample ERROR logs should include "file", "line", "column"

### Host/Container Metadata

- [ ] **For Kubernetes**
  - [ ] [ ] Set POD_NAME env var
  - [ ] [ ] Set POD_NAMESPACE env var
  - [ ] [ ] Set NODE_NAME env var

- [ ] **For Docker Compose**
  - [ ] [ ] Set SERVICE_NAME env var
  - [ ] [ ] Set CONTAINER_ID env var

- [ ] **For Traditional Servers**
  - [ ] [ ] Log os.hostname()
  - [ ] [ ] Log environment (prod/staging/dev)

- [ ] **Add to startup logs**
  - [ ] Log all host metadata on service start
  - [ ] Include version, build, deployment info

---

## 🟡 Phase 3: Polish (Week 3)

### Error Categorization

- [ ] **Define ERROR_CATEGORIES constant**
  - [ ] TIMEOUT
  - [ ] VALIDATION
  - [ ] PERMISSION
  - [ ] RESOURCE_EXHAUSTED
  - [ ] INTEGRATION
  - [ ] DATABASE
  - [ ] CONFIGURATION
  - [ ] UNKNOWN

- [ ] **Create categorizeError() function**
  - [ ] Map error codes → categories
  - [ ] Add to error logging

- [ ] **Test queries**
  - [ ] `error_category:timeout | stats count by service`
  - [ ] `error_category:permission | alert`

### Stack Trace Inclusion

- [ ] **Update error logging**
  - [ ] Include error.stack for all exceptions
  - [ ] Include error.cause.stack for nested errors
  - [ ] Format stack traces for readability

- [ ] **Test stack trace capture**
  - [ ] Trigger intentional error
  - [ ] Verify stack trace appears in logs
  - [ ] Verify it's readable in log viewer

### Log Sampling

- [ ] **Identify high-volume logs**
  - [ ] health_check: ~86,400/day/service
  - [ ] config_reload: ~100/day/service
  - [ ] metrics_collection: ~1,000/day

- [ ] **Implement sampling**
  - [ ] health_check: 1%
  - [ ] config_reload: 5%
  - [ ] metrics_collection: 2%

- [ ] **Verify sampling**
  - [ ] Run for 24 hours
  - [ ] Check log volume reduction
  - [ ] Verify can still see errors (0% sampling for ERROR+)

### Error Context Structure

- [ ] **Create structured error objects**
  - [ ] message
  - [ ] code
  - [ ] category
  - [ ] retriable
  - [ ] suggested_action
  - [ ] stack_trace
  - [ ] context

- [ ] **Update error logging**
  - [ ] Use structured error format
  - [ ] Test with complex errors

---

## ✅ Verification & Testing

### Phase 1 Verification

- [ ] **Trace ID Tests**
  - [ ] Single request generates unique trace_id
  - [ ] trace_id appears in all related logs
  - [ ] Retry request gets new trace_id but linked via request_id
  - [ ] Query: `trace_id=abc123 | stats count by component` → ≥3 results

- [ ] **PII Masking Tests**
  - [ ] `grep -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]' app.log` → No results
  - [ ] `grep -E 'AKIA[0-9A-Z]{16}' app.log` → No results
  - [ ] Manual review of 100 random entries → No PII visible

- [ ] **JSON Format Tests**
  - [ ] `jq . app.log` → All entries parse
  - [ ] `jq '.trace_id, .level, .message' app.log` → Can extract fields
  - [ ] Log ingestion latency in Splunk/ELK → <100ms

### Phase 2 Verification

- [ ] **Request Context Tests**
  - [ ] Single API call has unique request_id
  - [ ] All logs for that call have same request_id
  - [ ] Query: `request_id=req_123 | stats count` → ≥5 entries

- [ ] **Session Context Tests**
  - [ ] User session has unique session_id
  - [ ] All user operations have same session_id
  - [ ] Query: `session_id=sess_xyz | stats count by event`

- [ ] **Source Location Tests**
  - [ ] ERROR logs include file, line, column
  - [ ] Can open file at specified line; find exact log call

### Phase 3 Verification

- [ ] **Error Categorization Tests**
  - [ ] Query: `error_category:timeout` → Gets all timeouts
  - [ ] Query: `error_category:permission` → Gets all auth errors
  - [ ] Categorization ≥95% accurate

- [ ] **Stack Trace Tests**
  - [ ] ERROR logs include error.stack field
  - [ ] Stack trace is readable (not truncated)
  - [ ] Can trace back to specific line of code

- [ ] **Sampling Tests**
  - [ ] Log volume reduced for sampled entries
  - [ ] Can still see ERROR+ logs (100% fidelity)
  - [ ] Aggregation accounts for sample rate

---

## 📊 Metrics to Track

### Before Improvements
- [ ] Log quality score: 7.5/10
- [ ] Average log volume: ___ entries/day
- [ ] MTTR (mean time to resolve): ___ hours
- [ ] Trace correlation: 0%
- [ ] PII incidents: ___ (track compliance)

### After Phase 1
- [ ] Log quality score: ___ / 10
- [ ] Log volume: ___ entries/day (may increase with trace IDs)
- [ ] MTTR: ___ hours (should improve)
- [ ] Trace correlation: ≥95%
- [ ] PII incidents: 0

### After Phase 2
- [ ] Log quality score: ___ / 10
- [ ] MTTR: ___ hours (should improve further)
- [ ] Session traceability: ≥99%
- [ ] Source location availability: ≥99% of ERROR logs

### After Phase 3
- [ ] Log quality score: 9/10
- [ ] Error categorization accuracy: ≥95%
- [ ] Mean time to identify error category: <5 minutes

---

## 🚀 Deployment Strategy

### Option A: Gradual Rollout (Lower Risk)

**Week 1:**
- [ ] Implement Phase 1 (trace, PII, JSON) in staging
- [ ] Run for 1 week; monitor for issues
- [ ] Deploy to production 5% canary traffic
- [ ] Monitor for 24 hours; scale to 25%

**Week 2:**
- [ ] Full rollout to production
- [ ] Implement Phase 2 in staging
- [ ] Deploy Phase 2 to canary

**Week 3:**
- [ ] Full Phase 2 rollout
- [ ] Implement Phase 3 features
- [ ] Deploy to production

### Option B: Fast Track (Higher Confidence)

- [ ] Implement all phases locally
- [ ] Comprehensive testing
- [ ] Deploy to production directly
- [ ] Monitor closely for 3 days
- [ ] Rollback plan: Keep old logging library available for 2 weeks

**Recommended:** Option A (Gradual) due to broad impact on all services

---

## 🔄 Rollback Plan

If issues occur, rollback to previous logging format:

- [ ] Keep old logger configuration in a branch
- [ ] Deploy if: Parse errors >1%, ingestion latency >500ms, data loss detected
- [ ] Timeline: Can rollback within 30 minutes
- [ ] Impact: Will lose new fields (trace_id, source location) but preserve function

---

## 📋 Sign-Off Checklist

- [ ] Technical lead reviewed and approved plan
- [ ] Security team approved PII masking approach
- [ ] Operations team ready for deployment
- [ ] Monitoring/alerting set up for new fields
- [ ] Rollback plan tested
- [ ] Documentation updated
- [ ] Team trained on new logging standards
- [ ] Compliance team confirmed GDPR/CCPA adherence

---

## 📞 Escalation Path

If issues occur during implementation:

1. **Parsing errors** → Engineering lead
2. **Performance degradation** → Infrastructure team
3. **Data loss** → Database team + Engineering lead
4. **Security concerns** → Security team
5. **Compliance issues** → Legal/Compliance team

---

## Post-Implementation Review (Month 1)

- [ ] Review actual log volume vs. estimated
- [ ] Analyze MTTR improvement
- [ ] Gather team feedback
- [ ] Identify any edge cases
- [ ] Document lessons learned
- [ ] Plan refinements for Month 2

---

## Success Criteria

✅ Implementation complete when:

1. ✅ All Phase 1 items checked
2. ✅ Trace correlation ≥95%
3. ✅ PII incidents = 0
4. ✅ JSON parsing rate = 100%
5. ✅ MTTR improved by ≥50%
6. ✅ Team feedback positive
7. ✅ No production incidents
8. ✅ Log quality = 9/10

