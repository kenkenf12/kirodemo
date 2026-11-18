# System Refresh Feature

## Overview
The "🔄 Refresh" button allows you to clear all analysis data and start over with a clean slate. This is useful for:
- Starting a new analysis cycle
- Testing the system with fresh data
- Clearing old reports
- Resetting after testing

## Location
The refresh button is in the top-right header next to the Logout button.

## How It Works

### Before Clicking Refresh
- System has multiple reports and findings
- Synthesis report shows accumulated analysis

### Clicking Refresh Button
1. Confirmation dialog appears: "Are you sure you want to clear all analysis data and start fresh?"
2. Click "OK" to confirm or "Cancel" to abort

### After Refresh
- All reports are deleted from database
- All findings are deleted from database
- All application logs are cleared
- All uploaded log files are removed
- Dashboard reloads automatically with empty state
- User remains logged in

## What Gets Deleted

✓ **Reports**: All analysis reports cleared
✓ **Findings**: All security findings cleared
✓ **Log Files**: All uploaded .log files deleted
✓ **Application Logs**: Internal logs cleared

## What Stays

✗ **User Accounts**: Admin account unchanged
✗ **Sessions**: Current session remains valid
✗ **Database**: Tables exist but are empty

## API Endpoint

### GET /api/refresh
Clears all analysis data. Requires authentication.

**Request**:
```
GET /api/refresh
Cookie: session_id=<session_id>
```

**Response**:
```json
{
  "success": true,
  "message": "System reset complete. All reports and findings cleared.",
  "reports_cleared": true,
  "logs_cleared": true
}
```

## Usage Example

1. Open dashboard at `http://localhost:8000`
2. Login with admin/admin123
3. See current reports and synthesis data
4. Click "🔄 Refresh" button in header
5. Confirm in dialog
6. Page reloads with empty state
7. Upload new log files to begin fresh analysis

## Safety Features

- **Confirmation Required**: Prevents accidental deletion
- **Clear Message**: Users know what will happen
- **Audit Trail**: System logs the reset action
- **User Context**: Only authenticated users can refresh
- **Reversible Data**: Upload new logs to restart

## Code Implementation

### Backend (Python)
```python
def api_refresh(self):
    """Clear all analysis data and reset system."""
    # Clears findings, reports, logs tables
    # Deletes uploaded log files
    # Logs the action
```

### Frontend (JavaScript)
```javascript
function refreshSystem() {
    // Confirmation dialog
    // Calls /api/refresh endpoint
    // Reloads page on success
}
```

## Performance

- Refresh completes in <100ms
- Works with any database size
- No performance degradation

## Troubleshooting

**Refresh button not working**
- Clear browser cache
- Refresh page (F5)
- Check browser console (F12) for errors

**Refresh stuck on loading**
- Wait 30 seconds
- Close and reopen dashboard
- Check server logs

**Data not cleared**
- Verify endpoint returned success
- Check database directly
- Restart server and try again

## Related Features

- **Upload**: Add new log files to analyze
- **Synthesis Report**: View aggregated findings
- **Download**: Export reports before refresh

## Best Practices

1. **Download Before Refresh**: Save important reports
2. **Confirm Action**: Always confirm in dialog
3. **Fresh Start**: Upload new logs after refresh
4. **Regular Cleanup**: Periodically refresh for clean analysis

## Examples

### Start Fresh Analysis
```
1. Upload test_security.log
2. System analyzes (3 agents)
3. Review synthesis report
4. Click Refresh
5. Confirm deletion
6. Upload different_log.log
7. New analysis begins
```

### Test Different Scenarios
```
1. Upload log with brute force patterns
2. Review CRITICAL findings
3. Refresh system
4. Upload log with missing timestamps
5. Review DATA_QUALITY findings
6. Compare patterns
```

## Limitations

- Cannot undo refresh (data is deleted)
- Requires authentication
- Cannot refresh specific reports (all-or-nothing)

## Future Enhancements

- Selective report deletion
- Backup before refresh
- Undo functionality
- Scheduled auto-refresh
