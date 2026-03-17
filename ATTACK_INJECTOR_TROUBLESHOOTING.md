# Attack Injector Troubleshooting Guide

## Common Issues and Solutions

---

## Issue 1: Continuous Mode (Option 4) Not Working

### Symptoms
- Selected option 4 from batch file
- Script seems to hang or do nothing
- No attacks appearing on dashboard

### Possible Causes & Solutions

#### Cause 1: Backend Not Running
**Check:**
```bash
curl http://localhost:8000/health
```

**Solution:**
```bash
# Start backend first
cd backend
python -m uvicorn main:app --reload --port 8000
```

#### Cause 2: Login Failed
**Check:** Look for error message:
```
❌ Failed to login. Please check:
   1. Backend is running on http://localhost:8000
   2. Credentials are correct
   3. User has admin privileges
```

**Solution:**
- Verify backend is running
- Check credentials (default: admin/admin123)
- Ensure user has admin role

#### Cause 3: Script Running But No Visible Output
**What's happening:**
- Script is waiting for login response
- Network delay or backend slow to respond

**Solution:**
- Wait 5-10 seconds for login to complete
- Check backend terminal for login logs
- Look for "🔄 Continuous mode detected" message

#### Cause 4: Continuous Mode Started But Attacks Not Visible
**Check:**
1. Is dashboard open? (http://localhost:5173)
2. Are you logged in to dashboard?
3. Is dashboard showing "⚠ SYSTEM UNDER ATTACK" banner?

**Solution:**
- Refresh dashboard (F5)
- Check browser console (F12) for errors
- Verify attack mode enabled in backend

---

## Issue 2: "Failed to Login" Error

### Symptoms
```
❌ Failed to login. Please check:
   1. Backend is running on http://localhost:8000
   2. Credentials are correct
   3. User has admin privileges
```

### Solutions

#### Solution 1: Check Backend Status
```bash
# Test if backend is accessible
curl http://localhost:8000/

# Should return: {"message": "VANET Anomaly Detection API"}
```

#### Solution 2: Verify Credentials
```bash
# Test login manually
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should return token
```

#### Solution 3: Use Custom Credentials
```bash
# If default credentials changed
python attack_injector.py --continuous --username yourusername --password yourpassword
```

---

## Issue 3: Attacks Not Appearing on Dashboard

### Symptoms
- Injector running successfully
- No attacks visible on dashboard
- No "SYSTEM UNDER ATTACK" banner

### Solutions

#### Solution 1: Refresh Dashboard
- Press F5 to refresh
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito/private window

#### Solution 2: Check Attack Mode
The injector should automatically enable attack mode, but verify:

```bash
# Check current scenario
curl http://localhost:8000/data \
  -H "Authorization: Bearer <your-token>"

# Look for vehicles with is_anomaly: true
```

#### Solution 3: Check Browser Console
1. Press F12 to open developer tools
2. Go to Console tab
3. Look for errors
4. Check Network tab for failed requests

---

## Issue 4: Script Exits Immediately

### Symptoms
- Run attack injector
- Script exits right away
- No attacks injected

### Possible Causes

#### Cause 1: Python Not Installed
```bash
# Check Python version
python --version

# Should show Python 3.9 or higher
```

#### Cause 2: Missing Dependencies
```bash
# Install requests library
pip install requests

# Verify installation
python -c "import requests; print('OK')"
```

#### Cause 3: Syntax Error in Script
```bash
# Test script syntax
python -m py_compile attack_injector.py

# Should complete without errors
```

---

## Issue 5: Ctrl+C Not Stopping Continuous Mode

### Symptoms
- Press Ctrl+C
- Script doesn't stop
- Have to close terminal

### Solutions

#### Solution 1: Press Ctrl+C Multiple Times
- Press Ctrl+C 2-3 times rapidly
- Wait 2-3 seconds between presses

#### Solution 2: Force Close
**Windows:**
```bash
# Find Python process
tasklist | findstr python

# Kill process
taskkill /F /PID <process_id>
```

**Linux/Mac:**
```bash
# Find Python process
ps aux | grep attack_injector

# Kill process
kill -9 <process_id>
```

---

## Diagnostic Commands

### Test Connection
```bash
# Test backend health
curl http://localhost:8000/health

# Expected: {"status": "healthy"}
```

### Test Login
```bash
# Test authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Expected: {"access_token": "...", "token_type": "bearer"}
```

### Test Attack Mode
```bash
# Enable attack mode manually
curl -X POST http://localhost:8000/set-scenario \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"scenario":"ATTACK"}'

# Expected: {"message": "Scenario set to ATTACK"}
```

### Test Argument Parsing
```bash
# Run test script
python test_continuous_mode.py --continuous --interval 5

# Should show: "✓ Continuous mode flag is working!"
```

---

## Debug Mode

### Enable Verbose Output
Modify `attack_injector.py` temporarily:

```python
# Add at top of main()
print(f"DEBUG: Arguments: {sys.argv}")
print(f"DEBUG: Continuous: {continuous}")
print(f"DEBUG: Duration: {duration}")
print(f"DEBUG: Interval: {interval}")
```

---

## Quick Fixes

### Fix 1: Restart Everything
```bash
# 1. Stop all running processes (Ctrl+C)
# 2. Close all terminals
# 3. Start fresh:

# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd client
npm run dev

# Terminal 3: Attack Injector
python attack_injector.py --continuous --interval 5
```

### Fix 2: Use Direct Command Instead of Batch File
```bash
# Skip batch file, run directly
python attack_injector.py --continuous --interval 5

# This bypasses any batch file issues
```

### Fix 3: Test with Campaign Mode First
```bash
# Test with short campaign
python attack_injector.py --duration 10

# If this works, continuous mode should too
```

---

## Expected Behavior

### Continuous Mode Should Show:
```
🔄 Continuous mode detected
🔐 Logging in as admin...
✓ Login successful!
✓ Token: eyJhbGciOiJIUzI1NiIsInR5cCI6...
⚔️  Enabling attack mode...
✓ Attack mode enabled!

============================================================
🎯 VANET ATTACK INJECTOR - CONTINUOUS MODE
============================================================
Interval: 5 seconds between attacks
Target: http://localhost:8000
Press Ctrl+C to stop
============================================================

⏳ Starting continuous attack mode...
   Attacks will begin shortly...

[10:30:15] 🚨 Attack #1: GPS Spoofing
⏳ Next attack in 5 seconds...
[10:30:20] 🚨 Attack #2: DoS Attack
⏳ Next attack in 5 seconds...
[10:30:25] 🚨 Attack #3: Sybil Attack
⏳ Next attack in 5 seconds...
```

### Dashboard Should Show:
- ⚠ SYSTEM UNDER ATTACK banner (red)
- Colored vehicles on map (attack types)
- Attack panel with threat details
- Real-time attack count increasing

---

## Still Not Working?

### Checklist
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Logged in to dashboard as admin
- [ ] Python 3.9+ installed
- [ ] requests library installed
- [ ] No firewall blocking localhost
- [ ] No other process using port 8000

### Get Help
1. Check backend logs: `backend/vanet_system.log`
2. Check browser console (F12)
3. Run diagnostic: `python test_backend.py`
4. Try campaign mode first: `python attack_injector.py --duration 30`

---

## Performance Tips

### Reduce Interval for Faster Attacks
```bash
# Attack every 2 seconds
python attack_injector.py --continuous --interval 2
```

### Increase Interval for Slower Attacks
```bash
# Attack every 10 seconds
python attack_injector.py --continuous --interval 10
```

### Monitor System Resources
- Watch CPU usage
- Check memory consumption
- Monitor network traffic
- Reduce interval if system struggles

---

**Last Updated:** February 24, 2026  
**Version:** 4.0.0 Enterprise Edition

