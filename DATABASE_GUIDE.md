# Database System Guide

## Overview

The VANET system now includes a **professional SQLite database** for persistent data storage, enabling historical analysis, compliance auditing, and data export capabilities.

---

## 🎯 What's Stored

### 1. Attack Logs
Every detected attack is permanently stored with:
- Timestamp
- Vehicle ID
- Position (x, y coordinates)
- Attack type
- Confidence score
- Severity level
- Reconstruction error
- Speed
- Additional metadata

### 2. System Metrics
Performance data logged every ~2 seconds:
- Total vehicles
- Total anomalies
- Detection rate
- Current scenario (NORMAL/ATTACK)

### 3. Audit Logs
User activity tracking for security:
- Login attempts (success/failure)
- Configuration changes
- Data exports
- History clearing
- IP addresses

---

## 📊 Database Schema

### attack_logs Table
```sql
CREATE TABLE attack_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    vehicle_id INTEGER NOT NULL,
    position_x REAL NOT NULL,
    position_y REAL NOT NULL,
    attack_type TEXT NOT NULL,
    confidence REAL NOT NULL,
    severity TEXT NOT NULL,
    reconstruction_error REAL NOT NULL,
    speed REAL,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### system_metrics Table
```sql
CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    total_vehicles INTEGER NOT NULL,
    total_anomalies INTEGER NOT NULL,
    detection_rate REAL,
    scenario TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### audit_logs Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 New API Endpoints

### 1. Get Attack History (Enhanced)
```http
GET /attack-history?limit=100&attack_type=GPS%20Spoofing&severity=HIGH&start_date=2024-01-01T00:00:00
```

**Parameters:**
- `limit`: Max records (default: 50, max: 1000)
- `offset`: Pagination offset
- `attack_type`: Filter by type
- `severity`: Filter by severity (LOW/MEDIUM/HIGH)
- `start_date`: From date (ISO format)
- `end_date`: To date (ISO format)

**Response:**
```json
{
  "attacks": [...],
  "statistics": {
    "total_attacks": 1523,
    "by_type": {
      "GPS Spoofing": 456,
      "DoS Attack": 389,
      ...
    },
    "by_severity": {
      "HIGH": 678,
      "MEDIUM": 543,
      "LOW": 302
    },
    "average_confidence": 0.87,
    "most_targeted_vehicle": 42,
    "most_common_attack": "GPS Spoofing"
  },
  "pagination": {
    "limit": 100,
    "offset": 0,
    "returned": 100
  }
}
```

### 2. Get System Metrics History
```http
GET /analytics/metrics?limit=100&start_date=2024-01-01T00:00:00
```

**Returns:**
```json
{
  "metrics": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "total_vehicles": 50,
      "total_anomalies": 12,
      "detection_rate": 24.0,
      "scenario": "ATTACK"
    },
    ...
  ],
  "count": 100
}
```

### 3. Get Audit Logs (Admin Only)
```http
GET /analytics/audit-logs?username=admin&action=LOGIN_SUCCESS
```

**Returns:**
```json
{
  "audit_logs": [
    {
      "timestamp": "2024-01-15T10:25:00",
      "username": "admin",
      "action": "LOGIN_SUCCESS",
      "details": "Role: admin",
      "ip_address": "192.168.1.100"
    },
    ...
  ],
  "count": 50
}
```

### 4. Export Data to CSV (Admin Only)
```http
POST /analytics/export
{
  "table": "attack_logs",
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T23:59:59"
}
```

**Returns:**
```json
{
  "status": "success",
  "file": "exports/attack_logs_20240115_103000.csv",
  "records_exported": 1523,
  "exported_by": "admin"
}
```

---

## 💾 Data Persistence

### What Survives Restart?
✅ **All attack logs** - Complete history
✅ **System metrics** - Performance data
✅ **Audit logs** - User activity
✅ **Statistics** - Aggregated data

### What Doesn't Survive?
❌ **Current vehicle positions** - Regenerated on start
❌ **Active sessions** - Users must login again
❌ **In-memory cache** - Last 100 attacks (rebuilt from DB)

---

## 📈 Use Cases

### 1. Historical Analysis
```python
# Get all GPS Spoofing attacks from last month
GET /attack-history?attack_type=GPS%20Spoofing&start_date=2024-01-01&end_date=2024-01-31
```

### 2. Trend Identification
```python
# Get system metrics to see detection rate over time
GET /analytics/metrics?limit=1000&start_date=2024-01-01
```

### 3. Security Auditing
```python
# Check who logged in and when
GET /analytics/audit-logs?action=LOGIN_SUCCESS
```

### 4. Compliance Reporting
```python
# Export all data for compliance review
POST /analytics/export
{
  "table": "attack_logs",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### 5. Forensic Investigation
```python
# Find all attacks on specific vehicle
GET /attack-history?limit=1000
# Then filter by vehicle_id in results
```

---

## 🔧 Database Management

### Location
```
backend/vanet_data.db
```

### Size Management
The database automatically:
- Indexes for fast queries
- Stores efficiently (SQLite is compact)
- Can be backed up easily

### Cleanup Old Data
```python
# Clear data older than 30 days (admin only)
DELETE /attack-history
# This keeps last 7 days for compliance
```

### Backup
```bash
# Simple file copy
cp backend/vanet_data.db backend/vanet_data_backup.db

# Or use SQLite backup
sqlite3 backend/vanet_data.db ".backup 'backup.db'"
```

### View Data Directly
```bash
# Open database
sqlite3 backend/vanet_data.db

# Query attacks
SELECT * FROM attack_logs ORDER BY timestamp DESC LIMIT 10;

# Get statistics
SELECT attack_type, COUNT(*) as count 
FROM attack_logs 
GROUP BY attack_type 
ORDER BY count DESC;

# Exit
.quit
```

---

## 📊 Performance

### Optimizations
- **Indexed columns** for fast queries
- **Batch inserts** for efficiency
- **Periodic logging** (not every request)
- **Connection pooling** via context managers

### Expected Performance
- **Insert**: <1ms per attack
- **Query**: <10ms for 1000 records
- **Export**: ~1 second per 10,000 records
- **Database size**: ~1MB per 10,000 attacks

---

## 🔐 Security

### Access Control
- All endpoints require authentication
- Admin-only endpoints for sensitive operations
- Audit trail of all data access

### Data Protection
- Database file excluded from git (.gitignore)
- Exports folder excluded from git
- IP addresses logged for security

### Compliance
- Complete audit trail
- Data retention policies
- Export capabilities for compliance
- Automatic cleanup options

---

## 🎓 Examples

### Example 1: Daily Report
```python
# Get yesterday's attacks
import datetime
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
today = datetime.datetime.now().isoformat()

GET /attack-history?start_date={yesterday}&end_date={today}&limit=1000
```

### Example 2: High Severity Alerts
```python
# Get all HIGH severity attacks
GET /attack-history?severity=HIGH&limit=1000
```

### Example 3: User Activity Report
```python
# Get all admin actions
GET /analytics/audit-logs?username=admin&limit=1000
```

### Example 4: Performance Analysis
```python
# Get metrics for last week
week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()

GET /analytics/metrics?start_date={week_ago}&limit=10000
```

---

## 🔄 Migration to PostgreSQL (Future)

The system is designed to easily migrate to PostgreSQL:

1. Install PostgreSQL
2. Update connection string
3. Run migration script
4. No code changes needed!

SQLite is perfect for:
- ✅ Single server deployments
- ✅ Up to 100,000 attacks/day
- ✅ Simple setup
- ✅ No separate database server

PostgreSQL is better for:
- 🚀 Multiple servers
- 🚀 Millions of attacks/day
- 🚀 Advanced analytics
- 🚀 High concurrency

---

## 📝 Summary

### Before (v3.0.1)
- ❌ Data lost on restart
- ❌ No historical analysis
- ❌ Limited to last 100 attacks
- ❌ No audit trail

### After (v3.1.0)
- ✅ Persistent storage
- ✅ Complete history
- ✅ Advanced queries
- ✅ Data export
- ✅ Audit trail
- ✅ Compliance ready

---

**Your VANET system now has enterprise-grade data persistence!** 🎉

**Database File:** `backend/vanet_data.db`  
**Exports Folder:** `backend/exports/`  
**Documentation:** This file

