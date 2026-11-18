# Testing Guide - Multi-Agent Security Monitoring System

## System Overview
Complete multi-agent security analysis platform with:
- 3 specialized analysis agents (Security, Data Quality, Performance)
- Web dashboard with synthesis reports
- Interactive charts and metrics
- System refresh capability

## Pre-Test Checklist

✓ Python 3.x installed
✓ SQLite database functional
✓ Port 8000 available
✓ Browser with JavaScript enabled

## Starting the System

```bash
cd c:\Users\kenke\agent_code_review
python web_app.py
```

Expected output:
```
Security Monitor - Multi-Agent Analysis Platform
Server running on http://localhost:8000
```

## Test 1: Authentication

**Steps**:
1. Open `http://localhost:8000`
2. See login page
3. Enter wrong credentials
4. Verify rejection
5. Enter: `admin` / `admin123`
6. Verify redirect to dashboard

**Expected Result**: ✓ Login successful, redirected to `/dashboard`

## Test 2: Dashboard Navigation

**Steps**:
1. After login, see dashboard
2. Verify 2 tabs: "📋 Reports" and "📊 Synthesis Report"
3. Click "📋 Reports" tab
4. Verify content shows upload area and empty reports table
5. Click "📊 Synthesis Report" tab
6. Verify metrics grid appears

**Expected Result**: ✓ Both tabs switch correctly with appropriate content

## Test 3: File Upload

**Steps**:
1. Click "📋 Reports" tab
2. Upload `C:\tmp\logs\test_security.log`
3. Wait 2-3 seconds for analysis
4. Verify upload success message
5. Check reports table shows entry
6. See risk level badge (CRITICAL)

**Expected Result**: ✓ File analyzed, report created with findings

## Test 4: Multi-Agent Analysis

**Steps**:
1. After upload, wait for analysis
2. Check database: 3 reports created (one per agent)
3. Reports include: SECURITY, DATA_QUALITY, PERFORMANCE
4. Verify findings table populated
5. Check finding types:
   - BruteForceAttack (SECURITY)
   - MissingTraceIds (DATA_QUALITY)
   - HighErrorRate (PERFORMANCE)

**Expected Result**: ✓ All agents run, create appropriate findings

## Test 5: Synthesis Report Display

**Steps**:
1. Click "📊 Synthesis Report" tab
2. See 4 metrics cards:
   - Total Findings (blue border)
   - CRITICAL (red border)
   - HIGH (orange border)
   - MEDIUM (yellow border)
3. Verify numbers match findings in database
4. Scroll down to see chart

**Expected Result**: ✓ Metrics display correctly with data

## Test 6: Interactive Chart

**Steps**:
1. In Synthesis Report tab
2. See bar chart with severity levels
3. CRITICAL bar is red and tall
4. HIGH bar is orange and medium
5. MEDIUM and LOW bars are empty
6. Bars have labels and values
7. Hover over bars - verify tooltip

**Expected Result**: ✓ Chart renders with correct colors and heights

## Test 7: Executive Summary

**Steps**:
1. In Synthesis Report tab
2. Scroll to summary section
3. Verify text includes:
   - Overall risk level (CRITICAL)
   - Total findings count
   - Agent breakdown
   - Recommendations
4. Text is formatted properly

**Expected Result**: ✓ Summary displays analysis results

## Test 8: Download Report

**Steps**:
1. In Synthesis Report tab
2. Click "⬇️ Download HTML" button
3. Verify file downloads as `security_synthesis_report.html`
4. Open downloaded file in browser
5. Verify it contains all data:
   - Charts (ASCII or visual)
   - Metrics
   - Summary
   - Timestamp

**Expected Result**: ✓ HTML report downloads and opens correctly

## Test 9: Auto-Refresh Reports

**Steps**:
1. Check reports list
2. Wait 5 seconds
3. Verify "Recent Reports" updates automatically
4. Upload another log file
5. Wait for analysis
6. Verify new report appears without manual refresh

**Expected Result**: ✓ Reports list auto-refreshes every 5 seconds

## Test 10: System Refresh

**Steps**:
1. Verify reports and findings exist in database
2. Click "🔄 Refresh" button in header
3. See confirmation dialog
4. Click "Cancel"
5. Verify nothing is deleted
6. Click "🔄 Refresh" again
7. Click "OK" to confirm
8. Verify page reloads
9. Check dashboard - all reports gone
10. Verify database is empty

**Expected Result**: ✓ System clears all data on confirm

## Test 11: Fresh Analysis After Refresh

**Steps**:
1. After refresh, upload new log file
2. Verify system creates fresh reports
3. Check synthesis report shows new data
4. Upload different log file
5. Verify multiple analyses run

**Expected Result**: ✓ System ready for new analysis cycle

## Test 12: API Direct Access

**Steps**:
1. Get session via POST to `/api/login`
2. Use session to call `/api/synthesis`
3. Verify JSON response with metrics
4. Verify `/api/reports` shows list
5. Call `/api/synthesis/html` and download
6. Call `/api/refresh` to clear

**Expected Result**: ✓ All API endpoints functional

## Test 13: Security (Authentication)

**Steps**:
1. Try accessing `/dashboard` without session
2. Verify redirect to login
3. Try calling `/api/synthesis` without session
4. Verify 401 Unauthorized response
5. Try with fake session ID
6. Verify rejected

**Expected Result**: ✓ Protected endpoints require auth

## Test 14: Error Handling

**Steps**:
1. Manually delete database file
2. Try accessing dashboard
3. Verify system recreates database
4. Try uploading invalid file
5. Verify error message
6. Try large file
7. Verify handling

**Expected Result**: ✓ System handles errors gracefully

## Test 15: Concurrent Operations

**Steps**:
1. Upload log file 1
2. Quickly upload log file 2
3. While analyzing, click Synthesis Report tab
4. Verify no errors
5. Wait for both analyses
6. Verify both reports in list

**Expected Result**: ✓ System handles concurrent requests

## Performance Benchmarks

**Expected Performance**:
- Page load: <2 seconds
- Report upload: <3 seconds
- Analysis per agent: <1 second
- Synthesis report: <500ms
- Chart render: <100ms
- Database query: <50ms
- Dashboard refresh: <5 seconds

## Debugging Tips

### If dashboard doesn't load:
1. Check server is running
2. Verify port 8000 is open
3. Check browser console (F12)
4. Try incognito mode
5. Clear browser cache

### If reports don't appear:
1. Check upload succeeded
2. Check database file exists
3. Verify reports table not empty
4. Check server logs
5. Try refresh dashboard

### If charts don't render:
1. Check JavaScript enabled
2. Verify browser is modern
3. Check console for errors
4. Try different browser
5. Clear cache and reload

### If synthesis report empty:
1. Verify reports exist
2. Check findings populated
3. Try refresh page
4. Check API endpoint directly
5. Restart server

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on dashboard | Server not running | Start web_app.py |
| Login fails | Wrong credentials | Use admin/admin123 |
| No reports show | No files uploaded | Upload log file |
| Charts blank | No findings | Upload log with issues |
| Refresh stuck | Server busy | Wait or restart |
| API error 401 | No session | Login first |

## Test Data

### Sample Test Log
Location: `C:\tmp\logs\test_security.log`

Contains:
- Brute force attack patterns
- Credential exposure (AWS keys)
- Privilege escalation attempts
- Service timeouts
- High error rates
- Cascading failures

**Findings Expected**:
- CRITICAL: 6 findings
- HIGH: 8 findings
- Total: 14 findings

## Test Report Template

```
Test Date: ___________
Tester: ___________
System Version: ___________

[ ] Test 1: Authentication - PASS/FAIL
[ ] Test 2: Dashboard Navigation - PASS/FAIL
[ ] Test 3: File Upload - PASS/FAIL
[ ] Test 4: Multi-Agent Analysis - PASS/FAIL
[ ] Test 5: Synthesis Report - PASS/FAIL
[ ] Test 6: Interactive Chart - PASS/FAIL
[ ] Test 7: Executive Summary - PASS/FAIL
[ ] Test 8: Download Report - PASS/FAIL
[ ] Test 9: Auto-Refresh - PASS/FAIL
[ ] Test 10: System Refresh - PASS/FAIL
[ ] Test 11: Fresh Analysis - PASS/FAIL
[ ] Test 12: API Access - PASS/FAIL
[ ] Test 13: Security - PASS/FAIL
[ ] Test 14: Error Handling - PASS/FAIL
[ ] Test 15: Concurrent Ops - PASS/FAIL

Overall Status: [ ] PASS [ ] FAIL
Issues Found: ___________
Recommendations: ___________
```

## Success Criteria

✓ All 15 tests pass
✓ No error messages in console
✓ Performance within benchmarks
✓ Charts display correctly
✓ Data persists across sessions
✓ System recovers from errors
✓ Security controls work

## Next Steps After Testing

1. Document any issues
2. Report performance metrics
3. Verify deployment readiness
4. Plan production rollout
5. Set up monitoring
6. Create backup procedures
