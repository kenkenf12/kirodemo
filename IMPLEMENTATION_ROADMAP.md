# Logging Standards Implementation Roadmap

## Overview
This document provides concrete implementation guidance to improve the logging quality from 7.5/10 to 9/10.

---

## Phase 1: Critical Fixes (Week 1)

### 1.1 Add Trace Context Propagation

**What to do:**
Every log entry must include trace context that connects it to the original request.

**Implementation Pattern:**

```javascript
// Install OpenTelemetry
npm install @opentelemetry/api @opentelemetry/sdk-node

// Initialize trace context
import { trace, context } from '@opentelemetry/api';

const tracer = trace.getTracer('payment-service');

// Middleware to inject trace context
app.use((req, res, next) => {
  const span = tracer.startSpan(`http.${req.method}`);
  
  // Store in context
  context.with(trace.setSpan(context.active(), span), () => {
    // All logs in this request now have access to span
    next();
  });
});

// When logging
const activeSpan = trace.getActiveSpan();
logger.error('Payment failed', {
  trace_id: activeSpan.spanContext().traceId,
  span_id: activeSpan.spanContext().spanId,
  parent_span_id: activeSpan.parentSpanId,
  order_id: 'ord_12345',
  error: 'GATEWAY_TIMEOUT'
});
```

**Result:**
All logs in a single request flow automatically share the same trace_id, enabling correlation.

---

### 1.2 Mask PII Immediately

**Current Problem:**
```
email=john.doe@company.com    ← GDPR Violation
access_key_id=AKIA...         ← Partial credential exposure
```

**Implementation - Option A (Remove PII):**
```javascript
// Instead of logging email, log hashed user ID
logger.info('User login', {
  // ✗ DON'T: email: user.email,
  // ✓ DO: Use opaque identifier
  user_id: user.id,              // user_001
  user_hash: hash(user.email),   // Only if needed for debugging
  ip_address: request.ip
});

// Instead of logging full credentials
logger.error('Auth failed', {
  // ✗ DON'T: credentials: '${accessKey}:${secretKey}',
  // ✓ DO: Log credential type, not value
  credential_type: 'api_key',
  credential_id: 'key_12345...',  // Last 8 chars only
});
```

**Implementation - Option B (Hash-then-Log):**
```javascript
function sanitizeForLogging(data) {
  const sensitive_fields = ['email', 'password', 'credit_card', 'ssn', 'api_key'];
  
  for (let field of sensitive_fields) {
    if (data[field]) {
      data[field] = hash(data[field]);  // SHA256 one-way hash
    }
  }
  return data;
}

logger.info('User action', sanitizeForLogging({
  email: 'john@example.com',      // → 'a1b2c3d4e5f6...'
  phone: '+1-555-1234',           // → '8f7e6d5c4b3a...'
  user_id: 'usr_001',             // → 'usr_001' (not sensitive)
}));
```

**Immediate Actions:**
1. Search logs for: `email`, `password`, `api_key`, `access_key`, `credit_card`, `token`
2. Remove or hash these fields
3. Update logging middleware to sanitize

**Timeline:** 1-2 hours

---

### 1.3 Convert to JSON Format

**Current Format (Text-based):**
```
2024-01-15T09:24:02.156Z [ERROR] [PaymentGateway] Payment failed - order_id=ord_12345 amount=USD_1500.00 error_code=GATEWAY_TIMEOUT reason="Connection timeout"
```

**Issues:**
- Inconsistent delimiter usage (hyphens, equals signs, quotes)
- Parsing breaks if value contains delimiter
- Not machine-readable schema

**New Format (JSON Lines):**
```json
{"timestamp":"2024-01-15T09:24:02.156Z","level":"ERROR","component":"PaymentGateway","event":"payment_failed","order_id":"ord_12345","amount":"USD_1500.00","error_code":"GATEWAY_TIMEOUT","reason":"Connection timeout"}
```

**Implementation:**

```javascript
// 1. Use JSON-capable logger library
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DDTHH:mm:ss.SSSZ' }),
    winston.format.json()  // ← Automatic JSON formatting
  ),
  transports: [
    new winston.transports.File({ filename: 'app.log' })
  ]
});

// 2. Structured logging calls
logger.error('Payment processing failed', {
  trace_id: 'abc123',
  span_id: 'def456',
  component: 'PaymentGateway',
  event: 'payment_failed',
  order_id: 'ord_12345',
  amount: 'USD_1500.00',
  error_code: 'GATEWAY_TIMEOUT',
  reason: 'Connection timeout after 30s'
});

// Output (one per line):
// {"timestamp":"2024-01-15T09:24:02.156Z","level":"error","component":"PaymentGateway","event":"payment_failed",...}
```

**Alternative (Python):**
```python
import json
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)
handler = logging.FileHandler('app.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Usage
logger.error('Payment failed', extra={
    'trace_id': 'abc123',
    'order_id': 'ord_12345',
    'error_code': 'GATEWAY_TIMEOUT'
})
```

**Benefits:**
- ✅ Universal tool support (Splunk, ELK, Datadog all parse JSON natively)
- ✅ No ambiguity in values
- ✅ Scalable to complex structures
- ✅ Enables schema validation

**Timeline:** 2-3 days (depends on codebase size)

---

## Phase 2: Important Enhancements (Week 2)

### 2.1 Request & Session Context Propagation

**Problem:**
```
Current: Two logs from same user session have no connection
Log 1: 09:23:15 [INFO] Login - user_id=usr_001
Log 2: 09:24:21 [INFO] Export - user_id=usr_001
Gap: No way to know if same session or different login
```

**Solution:**

```javascript
// Middleware to create context
const sessionMiddleware = (req, res, next) => {
  const sessionId = req.cookies.sessionId || generateUUID();
  const requestId = generateUUID();
  
  // Store in context
  req.context = {
    trace_id: getTraceId(),        // From OpenTelemetry
    span_id: getSpanId(),          // From OpenTelemetry
    request_id: requestId,         // Unique per HTTP request
    session_id: sessionId,         // Unique per user session
    user_id: req.user?.id,
    tenant_id: req.user?.tenantId,
    environment: process.env.NODE_ENV
  };
  
  // Make available to all logs
  res.locals.context = req.context;
  next();
};

// Helper to automatically inject context
function createContextualLogger(context) {
  return {
    info: (message, extra) => {
      logger.info(message, { ...context, ...extra });
    },
    error: (message, extra) => {
      logger.error(message, { ...context, ...extra });
    }
  };
}

// Usage
app.post('/api/orders', sessionMiddleware, (req, res) => {
  const log = createContextualLogger(req.context);
  
  // Automatically includes: trace_id, span_id, request_id, session_id, user_id
  log.info('Order created', { order_id: 'ord_12345' });
  log.error('Payment failed', { error_code: 'TIMEOUT' });
});

// Output:
// {
//   "trace_id": "4a8c7e1b...",      ← Shared across retries
//   "span_id": "a1b2c3d4...",        ← Per-operation
//   "request_id": "req_99999...",    ← Per-HTTP-call
//   "session_id": "sess_88888...",   ← Per-user-session
//   "user_id": "usr_001",
//   "order_id": "ord_12345",
//   ...
// }
```

**Key IDs Explained:**

| ID | Scope | Propagation | Use Case |
|---|---|---|---|
| `trace_id` | Single business transaction | Across all services | Link payment → retry → webhook |
| `span_id` | Single operation | Per-service per-operation | Debug which function failed |
| `parent_span_id` | Call hierarchy | Parent → child spans | Visualize call chain |
| `request_id` | Single HTTP request | End-to-end in one service | Link request start/end |
| `session_id` | User session lifetime | All logs for a user | Track user activity |

**Timeline:** 1-2 days

---

### 2.2 Add Source Location Metadata

**Current Problem:**
```
[ERROR] ValidationService] Data validation failed
        ↑ Where in the code? What line?
```

**Solution:**

```javascript
// Option 1: Automatic via Error Stack
function getSourceLocation() {
  const stack = new Error().stack.split('\n')[3];
  const match = stack.match(/\((.+):(\d+):(\d+)\)/);
  return {
    file: match[1],
    line: match[2],
    column: match[3]
  };
}

logger.error('Validation failed', {
  ...logContext,
  ...getSourceLocation(),  // Adds: file, line, column
  field: 'email',
  issue: 'Invalid format'
});

// Output:
// {
//   "file": "/app/services/validation.js",
//   "line": 142,
//   "column": 15,
//   ...
// }
```

**Option 2: Decorator Pattern (Recommended)**

```javascript
function withSourceLocation(logger) {
  return {
    error(msg, data) {
      const { file, line, column } = getSourceLocation();
      logger.error(msg, { ...data, source: { file, line, column } });
    }
  };
}

const log = withSourceLocation(logger);
log.error('Payment failed', { order_id: 'ord_12345' });
// → Automatically includes source location
```

**Timeline:** 4-8 hours

---

### 2.3 Add Host/Container Metadata

**For Kubernetes/Container Environments:**

```javascript
// Inject at startup
const hostMetadata = {
  hostname: require('os').hostname(),
  pod_name: process.env.POD_NAME,
  pod_namespace: process.env.POD_NAMESPACE,
  container_id: process.env.CONTAINER_ID,
  node_name: process.env.NODE_NAME,
  service_version: process.env.APP_VERSION,
  region: process.env.AWS_REGION || 'unknown'
};

// Add to every log
logger.info('Service started', {
  ...hostMetadata,
  message: 'Payment service initialized'
});
```

**For Docker Compose:**

```javascript
const hostMetadata = {
  hostname: require('os').hostname(),
  container_name: process.env.HOSTNAME,
  service_name: process.env.SERVICE_NAME,
  docker_image: process.env.IMAGE_TAG,
  environment: process.env.COMPOSE_ENV || 'development'
};
```

**Kubernetes Deployment Example:**

```yaml
env:
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
  - name: POD_NAMESPACE
    valueFrom:
      fieldRef:
        fieldPath: metadata.namespace
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
```

**Timeline:** 2-4 hours

---

## Phase 3: Polish & Optimization (Week 3)

### 3.1 Error Categorization

**Current Problem:**
```
[ERROR] Database connection failed
[ERROR] Payment gateway timeout
[ERROR] Insufficient permissions
        ↑ All look the same; hard to aggregate
```

**Solution:**

```javascript
const ERROR_CATEGORIES = {
  TIMEOUT: 'external_service_timeout',
  VALIDATION: 'input_validation_failed',
  PERMISSION: 'access_denied',
  RESOURCE_EXHAUSTED: 'resource_limit_exceeded',
  INTEGRATION: 'external_service_error',
  DATABASE: 'database_error',
  CONFIGURATION: 'configuration_error',
  UNKNOWN: 'unknown_error'
};

function categorizeError(error) {
  if (error.code === 'GATEWAY_TIMEOUT') return ERROR_CATEGORIES.TIMEOUT;
  if (error.code === 'ENOENT') return ERROR_CATEGORIES.VALIDATION;
  if (error.code === 'FORBIDDEN') return ERROR_CATEGORIES.PERMISSION;
  // ... more mappings
  return ERROR_CATEGORIES.UNKNOWN;
}

logger.error('Operation failed', {
  error_code: 'GATEWAY_TIMEOUT',
  error_category: categorizeError(error),  // ← NEW
  retriable: true,
  reason: error.message
});

// Now you can query:
// error_category:timeout | stats count by service
// error_category:permission | alert on threshold
```

**Timeline:** 4-8 hours

---

### 3.2 Log Sampling Strategy

**Problem:**
```
Current: Every health check logged = 86,400 logs/day per service
Cost: High storage, high processing, noise in aggregation
```

**Solution:**

```javascript
function shouldLog(level, eventType) {
  // Always log errors and above
  if (level >= LOG_LEVEL.ERROR) return true;
  
  // Sample high-volume events
  const samplingRates = {
    'health_check': 0.01,        // Log 1 in 100
    'config_reload': 0.05,       // Log 1 in 20
    'metrics_collection': 0.02,  // Log 1 in 50
    'api_request': 1.0           // Log all
  };
  
  const rate = samplingRates[eventType] || 1.0;
  return Math.random() < rate;
}

logger.info('Health check passed', {
  sample_rate: 0.01,
  should_sample: shouldLog(LOG_LEVEL.INFO, 'health_check'),
  service: 'payment-service'
});

// Result: 1 log per 100 health checks
// If aggregation tool sees sample_rate field, it scales: count * 100
```

**Timeline:** 2-4 hours

---

### 3.3 Structured Error Responses

**Current Problem:**
```
[ERROR] ETL job failed - error="Out of memory"
        ↑ No helpful context for debugging
```

**Solution:**

```javascript
class ErrorWithContext extends Error {
  constructor(message, context = {}) {
    super(message);
    this.context = context;
    this.timestamp = new Date();
    this.stack = Error.captureStackTrace(this, this.constructor);
  }
}

// Usage
throw new ErrorWithContext('ETL processing failed', {
  pipeline_id: 'etl_daily_001',
  error_type: 'OUT_OF_MEMORY',
  available_memory: '256MB',
  required_memory: '2048MB',
  input_records: 1000000,
  processed_records: 450000,
  checkpoint_available: true,
  recovery_strategy: 'RESUME_FROM_CHECKPOINT'
});

// Logging
try {
  // ... ETL code
} catch (error) {
  logger.error('ETL failed', {
    message: error.message,
    error_type: error.context?.error_type,
    available_memory: error.context?.available_memory,
    stack_trace: error.stack,
    recovery_hint: error.context?.recovery_strategy
  });
}
```

**Timeline:** 4-8 hours

---

## Reference: Logging Levels

Use these guidelines:

| Level | Use Case | Frequency |
|---|---|---|
| **DEBUG** | Code execution flow, variable values | High (usually disabled in production) |
| **INFO** | Business events: user login, order created, job started | Medium (important milestones) |
| **WARN** | Degraded state: cache miss, high latency, retries | Low (investigate if trending) |
| **ERROR** | Request failed: payment failed, validation failed | Very low (each is an incident) |
| **CRITICAL** | System failure: service down, data corruption | Rare (page on-call) |

**Current Log Analysis:**
- ✅ Appropriate mix of levels
- ⚠️ Too many INFO logs (health checks, config reloads)
- 💡 Consider: Sample INFO → INFO_SAMPLED

---

## Testing the Improvements

### Test 1: Trace Context Propagation

```javascript
// Request comes in with trace context
// Follow trace_id through all services:
// 1. API Gateway receives request → generates trace_id=abc123
// 2. Auth Service logs: trace_id=abc123 event=auth_success
// 3. Payment Service logs: trace_id=abc123 event=payment_started
// 4. Retry Service logs: trace_id=abc123 event=retry_attempt
// 5. Webhook Service logs: trace_id=abc123 event=webhook_received

// Query: Find all operations for this transaction
// splunk query: trace_id=abc123 | sort timestamp

// Expected: All 5 events returned in chronological order
```

### Test 2: PII Masking

```
grep -r "email.*@" app.log           → Should find 0 results
grep -r "access_key_id.*AKIA" app.log → Should find 0 results
```

### Test 3: JSON Parsing

```bash
# Each line should be valid JSON
jq . app.log | head -100

# Should be able to extract any field
jq '.trace_id' app.log | sort | uniq -c
```

---

## Implementation Timeline Summary

| Phase | Duration | Tasks |
|---|---|---|
| **P0 - Critical** | **Week 1** | Trace IDs (2-3d) + PII masking (1d) + JSON (2-3d) |
| **P1 - Important** | **Week 2** | Session context (1-2d) + Source location (4-8h) + Host metadata (2-4h) |
| **P2 - Polish** | **Week 3** | Error categories (4-8h) + Log sampling (2-4h) + Error context (4-8h) |

**Total Effort:** ~3-4 weeks depending on team size and codebase complexity

**Expected Quality Improvement:** 7.5/10 → 9/10

---

## Rollout Strategy

### Option A: Gradual Rollout
1. Week 1: Deploy to staging; verify with APM tools
2. Week 2: Deploy to production canary (5% traffic)
3. Week 3: Full production rollout

### Option B: Fast Track (High Confidence)
1. Deploy to production immediately
2. Monitor logs for issues (2-3 days)
3. Fine-tune sampling rates based on volume

### Monitoring Metrics During Rollout
- Log volume (should increase initially, then plateau with sampling)
- Parse errors (should be ~0)
- Trace correlation ratio (should be 95%+)
- Tool ingestion latency (should be <100ms p95)

---

## Tools & Libraries Recommendations

| Language | Logger | Trace Library | Notes |
|---|---|---|---|
| **Node.js** | winston / pino | @opentelemetry/api | Pino is faster for high volume |
| **Python** | structlog / python-json-logger | opentelemetry-api | Structlog has better context management |
| **Java** | SLF4J + Logback | opentelemetry-java | Can output OTLP directly |
| **Go** | logrus / zap | go.opentelemetry.io/otel | Zap is high-performance |
| **.NET** | Serilog | OpenTelemetry.Api | Serilog integrates well with OT |

**Universal:**
- **Collector:** OpenTelemetry Collector (processes logs before sending to backend)
- **Backend:** Datadog, New Relic, Grafana Loki, or self-hosted ELK
- **Visualization:** Grafana, Kibana

---

## Success Criteria

| Criterion | Before | After | Target |
|---|---|---|---|
| **Trace Coverage** | 0% | 100% | All requests traced |
| **Correlation Ability** | Manual | Automatic | Click to see full transaction |
| **MTTR (Mean Time to Resolve)** | 2-4 hours | 15-30 minutes | 10x improvement |
| **Log Quality Score** | 7.5/10 | 9/10 | Production-ready |
| **Tool Compatibility** | ELK only | All major platforms | Full flexibility |
| **PII Incidents** | High risk | Zero risk | Compliance achieved |

