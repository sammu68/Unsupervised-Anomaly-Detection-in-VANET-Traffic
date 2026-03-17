# Attack Log Management Guide

## Overview
Admins have flexible options to manage attack logs in the database. This guide explains all available deletion methods.

---

## 🔐 Access Requirements
- **Role:** Admin only
- **Authentication:** JWT token required
- **Audit:** All deletions are logged in audit trail

---

## 📋 Deletion Options

### 1. Delete All Attack Logs
**Endpoint:** `DELETE /attack-history/all`

**Description:** Removes ALL attack logs from the database permanently.

**Use Cases:**
- Complete system reset
- Testing/development cleanup
- Major maintenance

**Example:**
```bash
curl -X DELETE "http://localhost:8000/attack-history/all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "status": "cleared",
  "cleared_count": {
    "memory": 150,
    "database": 5420,
    "total": 5570
  },
  "note": "All attack history has been permanently deleted",
  "cleared_by": "admin",
  "timestamp": "2026-02-24T10:30:00"
}
```

**⚠️ Warning:** This action cannot be undone!

---

### 2. Delete Attacks Older Than X Days
**Endpoint:** `DELETE /attack-history/older-than?days=X`

**Description:** Removes attack logs older than specified number of days, keeping recent data.

**Parameters:**
- `days` (optional): Number of days to keep (default: 7)

**Use Cases:**
- Regular maintenance
- Database cleanup
- Storage management
- Compliance (keep last 30/90 days)

**Examples:**

Keep last 7 days (default):
```bash
curl -X DELETE "http://localhost:8000/attack-history/older-than?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Keep last 30 days:
```bash
curl -X DELETE "http://localhost:8000/attack-history/older-than?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Keep only today's data:
```bash
curl -X DELETE "http://localhost:8000/attack-history/older-than?days=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "status": "cleared",
  "cleared_count": {
    "memory": 150,
    "database": 3200,
    "total": 3350
  },
  "note": "Last 7 days of data preserved",
  "cleared_by": "admin",
  "timestamp": "2026-02-24T10:30:00"
}
```

---

### 3. Delete Attacks by Date Range
**Endpoint:** `DELETE /attack-history/date-range?start_date=X&end_date=Y`

**Description:** Removes attack logs within a specific date range.

**Parameters:**
- `start_date` (optional): Start date in ISO format
  - Date only (YYYY-MM-DD): Starts at 00:00:00 of that day
  - Full datetime (YYYY-MM-DDTHH:MM:SS): Exact time
- `end_date` (optional): End date in ISO format
  - Date only (YYYY-MM-DD): Ends at 23:59:59 of that day (includes entire day)
  - Full datetime (YYYY-MM-DDTHH:MM:SS): Exact time

**Note:** At least one parameter (start_date or end_date) must be provided.

**Use Cases:**
- Remove specific time period data
- Clean up test data from specific dates
- Targeted maintenance
- Remove data from a specific incident period

**Examples:**

Delete all attacks on February 24, 2026 (entire day):
```bash
curl -X DELETE "http://localhost:8000/attack-history/date-range?start_date=2026-02-24&end_date=2026-02-24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Delete January 2026 data:
```bash
curl -X DELETE "http://localhost:8000/attack-history/date-range?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Delete everything from February 1st onwards:
```bash
curl -X DELETE "http://localhost:8000/attack-history/date-range?start_date=2026-02-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Delete everything up to January 31st:
```bash
curl -X DELETE "http://localhost:8000/attack-history/date-range?end_date=2026-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Delete specific time range with hours:
```bash
curl -X DELETE "http://localhost:8000/attack-history/date-range?start_date=2026-02-20T08:00:00&end_date=2026-02-20T17:00:00" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "status": "cleared",
  "cleared_count": {
    "memory": 150,
    "database": 1250,
    "total": 1400
  },
  "date_range": {
    "start": "2026-01-01",
    "end": "2026-01-31"
  },
  "cleared_by": "admin",
  "timestamp": "2026-02-24T10:30:00"
}
```

---

## 🔍 Using API Documentation (Swagger)

1. Navigate to: http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Enter your JWT token: `Bearer YOUR_TOKEN`
4. Click "Authorize" then "Close"
5. Your token is now saved and will persist even after page refresh!

**Note:** The token is stored in your browser's localStorage and will remain until you:
- Click "Logout" in Swagger UI
- Clear browser data
- Token expires (30 minutes)

### Finding Your Token

**Option 1: From Frontend (easiest)**
1. Login to the React app (http://localhost:5173)
2. Open browser DevTools (F12)
3. Go to Console tab
4. Type: `localStorage.getItem('token')`
5. Copy the token value

**Option 2: From API Login**
1. In Swagger UI, expand `POST /auth/login`
2. Click "Try it out"
3. Enter credentials (admin/admin123)
4. Click "Execute"
5. Copy the `access_token` from response

### Using the Endpoints

Once authorized:
1. Expand the deletion endpoint you need:
   - `DELETE /attack-history/all`
   - `DELETE /attack-history/older-than`
   - `DELETE /attack-history/date-range`
2. Click "Try it out"
3. Enter parameters (if required)
4. Click "Execute"
5. Token is automatically included in the request!

---

## 📊 What Gets Deleted

### In-Memory Data
- Current session attack history (displayed in UI)
- Cleared immediately

### Database Data
- `attack_logs` table records
- Permanent deletion based on criteria
- Cannot be recovered after deletion

### What's NOT Deleted
- `system_metrics` table (performance data)
- `audit_logs` table (user activity logs)
- User accounts
- System configuration

---

## 🔒 Security & Audit

### Audit Logging
All deletion operations are logged with:
- Username who performed the action
- Action type (CLEAR_ALL_ATTACKS, CLEAR_OLD_ATTACKS, CLEAR_ATTACKS_BY_RANGE)
- Number of records deleted
- Date range or criteria used
- Timestamp

### View Audit Logs
```bash
curl -X GET "http://localhost:8000/analytics/audit-logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💡 Best Practices

### Delete Specific Day
```bash
# Delete all attacks on February 24, 2026
DELETE /attack-history/date-range?start_date=2026-02-24&end_date=2026-02-24
```

### Regular Maintenance
```bash
# Weekly cleanup - keep last 30 days
DELETE /attack-history/older-than?days=30
```

### Compliance Requirements
```bash
# Keep 90 days for regulatory compliance
DELETE /attack-history/older-than?days=90
```

### Testing Cleanup
```bash
# Remove test data from specific date
DELETE /attack-history/date-range?start_date=2026-02-20&end_date=2026-02-20
```

### Storage Management
```bash
# Check database size first
# Then delete old data to free space
DELETE /attack-history/older-than?days=7
```

---

## ⚠️ Important Notes

1. **Backup First:** Consider exporting data before deletion
2. **Cannot Undo:** Deleted data cannot be recovered
3. **Admin Only:** Only admin users can delete attack logs
4. **Audit Trail:** All deletions are logged for compliance
5. **In-Memory Clear:** All deletion methods clear in-memory data too
6. **Date Format:** Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)

---

## 📤 Export Before Delete

Export attack logs to CSV before deletion:

```bash
curl -X GET "http://localhost:8000/analytics/export/attack-logs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o attack_logs_backup.csv
```

---

## 🆘 Troubleshooting

### Error: "At least one of start_date or end_date must be provided"
- You called `/date-range` without any parameters
- Provide at least `start_date` or `end_date`

### Error: "Unauthorized"
- Your token expired (30 minutes)
- Login again to get a new token

### Error: "Forbidden"
- You're not logged in as admin
- Only admin users can delete attack logs

### Error: "Database error"
- Invalid date format
- Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS

---

## 📞 Support

For issues or questions:
1. Check API documentation: http://localhost:8000/docs
2. Review audit logs for deletion history
3. Check backend logs for error details

---

**Last Updated:** February 24, 2026  
**Version:** 4.0.0 Enterprise Edition
