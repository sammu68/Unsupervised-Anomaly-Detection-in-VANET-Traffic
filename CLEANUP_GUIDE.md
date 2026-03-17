# Folder Size Cleanup Guide

## Why Folder Size Grows

### 1. Database File (vanet_data.db)
**Location:** `backend/vanet_data.db`

**Why it grows:**
- Stores every attack detected
- Stores system metrics every update
- Stores audit logs for every user action
- Can grow to 100+ MB over time

**Current tables:**
- `attack_logs` - Every attack detected
- `system_metrics` - Performance data
- `audit_logs` - User activity
- `users` - User accounts (small)

### 2. Log Files
**Location:** `backend/vanet_system.log`

**Why it grows:**
- Logs every API request
- Logs every error
- Logs every user action
- Can grow to 50+ MB

### 3. Export Files
**Location:** `backend/exports/*.csv`

**Why it grows:**
- Each export creates a new CSV file
- Files accumulate over time
- Each can be 1-10 MB

### 4. Node Modules (Biggest!)
**Location:** `client/node_modules/`

**Size:** 200-500 MB

**Why it's large:**
- Contains all npm dependencies
- React, Recharts, Tailwind, etc.
- Normal for Node.js projects

### 5. Documentation Files
**Location:** Root directory `*.md`

**Size:** ~1-2 MB total (small)

**Files created:**
- Various guides and documentation
- Not a significant contributor

---

## How to Clean Up

### Option 1: Clean Database (Recommended)

**Delete old attack logs (keep last 7 days):**
```bash
# Using API (requires admin login)
DELETE http://localhost:8000/attack-history/older-than?days=7
```

**Or delete all attacks:**
```bash
DELETE http://localhost:8000/attack-history/all
```

**Or manually:**
```bash
# Stop backend first
cd backend
sqlite3 vanet_data.db "DELETE FROM attack_logs WHERE timestamp < datetime('now', '-7 days');"
sqlite3 vanet_data.db "DELETE FROM system_metrics WHERE timestamp < datetime('now', '-7 days');"
sqlite3 vanet_data.db "VACUUM;"  # Reclaim space
```

### Option 2: Clean Log Files

**Clear backend logs:**
```bash
# Windows
cd backend
type nul > vanet_system.log

# Linux/Mac
cd backend
> vanet_system.log
```

**Or delete and recreate:**
```bash
cd backend
rm vanet_system.log
# Will be recreated on next backend start
```

### Option 3: Clean Export Files

**Delete old exports:**
```bash
cd backend/exports
# Windows
del *.csv

# Linux/Mac
rm *.csv
```

**Or keep only recent ones:**
```bash
# Keep only today's exports, delete older
```

### Option 4: Clean Node Modules (Biggest Impact!)

**If you don't need to modify frontend:**
```bash
cd client
# Windows
rmdir /s /q node_modules

# Linux/Mac
rm -rf node_modules
```

**To reinstall later:**
```bash
cd client
npm install
```

### Option 5: Clean Python Cache

**Delete Python cache files:**
```bash
cd backend
# Windows
rmdir /s /q __pycache__

# Linux/Mac
rm -rf __pycache__
```

---

## Recommended Cleanup Routine

### Daily (Automated)
- Nothing needed

### Weekly
- Delete attack logs older than 7 days
- Clear log file if >50 MB

### Monthly
- Delete old export files
- Vacuum database to reclaim space

### Before Deployment
- Delete node_modules (reinstall on server)
- Delete __pycache__
- Delete old exports
- Keep only essential documentation

---

## Size Breakdown (Typical)

### Small Project (Fresh)
```
client/node_modules/     200-500 MB  (largest!)
dataset_50k.csv          10-20 MB
vanet_anomaly_detector.h5  5-10 MB
backend/vanet_data.db    1-5 MB
backend/vanet_system.log 1-5 MB
backend/exports/         1-5 MB
Documentation files      1-2 MB
Code files              1-2 MB
-----------------------------------
TOTAL:                  220-550 MB
```

### After Heavy Use (1 week)
```
client/node_modules/     200-500 MB
dataset_50k.csv          10-20 MB
vanet_anomaly_detector.h5  5-10 MB
backend/vanet_data.db    50-100 MB  (grew!)
backend/vanet_system.log 20-50 MB   (grew!)
backend/exports/         10-20 MB   (grew!)
Documentation files      1-2 MB
Code files              1-2 MB
-----------------------------------
TOTAL:                  300-700 MB
```

---

## Automated Cleanup Script

### Windows (cleanup.bat)
```batch
@echo off
echo Cleaning up VANET system...

REM Clean database (keep last 7 days)
echo Cleaning database...
cd backend
sqlite3 vanet_data.db "DELETE FROM attack_logs WHERE timestamp < datetime('now', '-7 days');"
sqlite3 vanet_data.db "DELETE FROM system_metrics WHERE timestamp < datetime('now', '-7 days');"
sqlite3 vanet_data.db "VACUUM;"

REM Clear log file
echo Clearing log file...
type nul > vanet_system.log

REM Delete old exports
echo Deleting old exports...
cd exports
del *.csv
cd ..

echo Cleanup complete!
pause
```

### Linux/Mac (cleanup.sh)
```bash
#!/bin/bash
echo "Cleaning up VANET system..."

# Clean database (keep last 7 days)
echo "Cleaning database..."
cd backend
sqlite3 vanet_data.db "DELETE FROM attack_logs WHERE timestamp < datetime('now', '-7 days');"
sqlite3 vanet_data.db "DELETE FROM system_metrics WHERE timestamp < datetime('now', '-7 days');"
sqlite3 vanet_data.db "VACUUM;"

# Clear log file
echo "Clearing log file..."
> vanet_system.log

# Delete old exports
echo "Deleting old exports..."
rm -f exports/*.csv

echo "Cleanup complete!"
```

---

## What NOT to Delete

### Keep These Files:
- ✅ `vanet_anomaly_detector.h5` - ML model (needed!)
- ✅ `dataset_50k.csv` - Training data (needed for retraining)
- ✅ `backend/vanet_data.db` - Database (but clean old data)
- ✅ `backend/.env` - Configuration
- ✅ All `.py` files - Source code
- ✅ All `.jsx` files - Frontend code
- ✅ `package.json` - Dependencies list
- ✅ `requirements.txt` - Python dependencies

### Safe to Delete:
- ❌ `client/node_modules/` - Can reinstall with `npm install`
- ❌ `backend/__pycache__/` - Python cache, auto-recreated
- ❌ `backend/exports/*.csv` - Old exports
- ❌ `backend/vanet_system.log` - Log file (auto-recreated)
- ❌ Old attack logs in database (keep recent ones)

---

## Preventing Growth

### 1. Automatic Database Cleanup
Add to backend startup or cron job:
```python
# In main.py startup
from database import clear_old_data
clear_old_data(days=7)  # Keep only last 7 days
```

### 2. Log Rotation
Configure log rotation:
```python
# In main.py
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'vanet_system.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=3
)
```

### 3. Limit Export Files
Delete exports after download or keep only last 5.

### 4. Database Maintenance
Run VACUUM monthly:
```bash
sqlite3 backend/vanet_data.db "VACUUM;"
```

---

## Quick Size Check

### Windows
```cmd
dir /s
```

### Linux/Mac
```bash
du -sh *
du -sh client/node_modules
du -sh backend/vanet_data.db
```

---

## Deployment Optimization

### For Production Deployment:

1. **Delete node_modules** (reinstall on server)
2. **Clean database** (keep only essential data)
3. **Delete exports** (not needed on server)
4. **Delete __pycache__** (recreated on server)
5. **Keep only essential docs** (README, INSTALLATION)

**Result:** Reduce from 500 MB to ~50 MB!

---

## Summary

**Main culprits:**
1. `client/node_modules/` - 200-500 MB (biggest!)
2. `backend/vanet_data.db` - Grows over time
3. `backend/vanet_system.log` - Grows over time
4. `backend/exports/` - Accumulates files

**Quick cleanup:**
```bash
# Delete node_modules (can reinstall)
rm -rf client/node_modules

# Clean database (keep last 7 days)
# Use API endpoint or SQL commands

# Clear log file
> backend/vanet_system.log

# Delete old exports
rm backend/exports/*.csv
```

**Result:** Reduce size by 50-80%!

---

**Last Updated:** February 24, 2026  
**Version:** 4.0.0 Enterprise Edition
