# Testing Guide - VANET System v3.0

## Overview

This guide covers all testing procedures for the VANET Anomaly Detection System.

---

## Pre-Testing Setup

### 1. System Health Check
```bash
python system_check.py
```

### 2. Start Services
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd client
npm run dev
```

### 3. Verify Services Running
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

## Authentication Testing

### Test 1: Admin Login
**Steps:**
1. Open http://localhost:5173
2. Enter username: `admin`
3. Enter password: `admin123`
4. Click "Initialize System"

**Expected:**
- ✅ Login successful
- ✅ Redirected to dashboard
- ✅ User profile shows "admin" role
- ✅ All features accessible

### Test 2: Operator Login
**Steps:**
1. Logout (if logged in)
2. Login with: `operator` / `operator123`

**Expected:**
- ✅ Login successful
- ✅ Dashboard accessible
- ✅ Settings button disabled (read-only)
- ✅ Cannot change vehicle count

### Test 3: Invalid Credentials
**Steps:**
1. Try login with: `admin` / `wrongpassword`

**Expected:**
- ✅ Error message displayed
- ✅ "Incorrect username or password"
- ✅ Remains on login screen

### Test 4: Token Expiration
**Steps:**
1. Login successfully
2. Wait 30+ minutes (or change expiration to 1 min for testing)
3. Try to interact with system

**Expected:**
- ✅ Token expires
- ✅ API calls fail with 401
- ✅ User redirected to login

### Test 5: Multiple Users
**Steps:**
1. Login as `admin` in one browser
2. Login as `operator` in another browser/incognito

**Expected:**
- ✅ Both sessions work independently
- ✅ Different permissions enforced
- ✅ No session conflicts

---

## Attack Detection Testing

### Test 6: Normal Traffic
**Steps:**
1. Login to system
2. Ensure attack mode is OFF (Shield icon not red)
3. Observe traffic map

**Expected:**
- ✅ All vehicles show as cyan (normal)
- ✅ Reconstruction errors < 0.1114
- ✅ No anomalies detected
- ✅ Attack panel shows 0 threats

### Test 7: Attack Simulation
**Steps:**
1. Click Shield icon to enable attack mode
2. Wait 2-3 seconds
3. Observe changes

**Expected:**
- ✅ Shield icon turns red and pulses
- ✅ Some vehicles change color
- ✅ Anomalies detected (MSE > 0.1114)
- ✅ Attack panel shows threats
- ✅ Attack counter badge appears

### Test 8: Attack Classification
**Steps:**
1. Enable attack mode
2. Open attack panel (AlertTriangle icon)
3. Review detected attacks

**Expected:**
- ✅ Multiple attack types detected
- ✅ GPS Spoofing (red)
- ✅ Position Falsification (orange)
- ✅ Sybil Attack (fuchsia)
- ✅ DoS Attack (violet)
- ✅ Message Tampering (amber)
- ✅ Replay Attack (yellow)
- ✅ Confidence scores shown (0-100%)
- ✅ Severity levels assigned

### Test 9: Attack Panel Details
**Steps:**
1. Open attack panel with active threats
2. Review each threat card

**Expected:**
- ✅ Vehicle ID displayed
- ✅ Attack type with icon
- ✅ Severity badge (LOW/MEDIUM/HIGH)
- ✅ Confidence percentage
- ✅ Position coordinates
- ✅ Reconstruction error (MSE)
- ✅ Primary indicators listed

### Test 10: Traffic Map Tooltips
**Steps:**
1. Hover over vehicles on map
2. Check tooltip information

**Expected:**
- ✅ Vehicle ID shown
- ✅ Position coordinates
- ✅ Speed displayed
- ✅ MSE value shown
- ✅ Attack classification (if anomaly)
- ✅ Severity and confidence

---

## UI/UX Testing

### Test 11: Dashboard Layout
**Steps:**
1. Login and view dashboard
2. Check all components

**Expected:**
- ✅ Header with user info
- ✅ Sidebar with icons
- ✅ Traffic map visible
- ✅ Metrics cards showing data
- ✅ Live graph updating
- ✅ Responsive layout

### Test 12: Settings Panel (Admin)
**Steps:**
1. Login as admin
2. Click Settings icon
3. Adjust vehicle density slider

**Expected:**
- ✅ Settings panel opens
- ✅ Slider works smoothly
- ✅ Vehicle count updates
- ✅ Map regenerates
- ✅ Debounced API calls (not every slider move)

### Test 13: Map Toggle
**Steps:**
1. Click "M" button in sidebar
2. Toggle map on/off

**Expected:**
- ✅ Map visibility toggles
- ✅ Button state changes
- ✅ Smooth transition
- ✅ Other components unaffected

### Test 14: Logout
**Steps:**
1. Click logout button in sidebar
2. Confirm logout

**Expected:**
- ✅ Token cleared from localStorage
- ✅ Redirected to login screen
- ✅ Cannot access dashboard without login
- ✅ API calls fail without token

---

## API Testing

### Test 15: Health Endpoint
```bash
curl http://localhost:8000/health \
  -H "Authorization: Bearer <your-token>"
```

**Expected:**
```json
{
  "status": "healthy",
  "tensorflow_available": true,
  "model_loaded": true,
  "current_scenario": "NORMAL",
  "vehicle_count": 15,
  "authenticated_user": "admin",
  "user_role": "admin"
}
```

### Test 16: Data Endpoint
```bash
curl http://localhost:8000/data \
  -H "Authorization: Bearer <your-token>"
```

**Expected:**
```json
{
  "vehicles": [...],
  "scenario": "NORMAL",
  "total_anomalies": 0,
  "detected_attacks": [],
  "user": "admin"
}
```

### Test 17: Attack History
```bash
curl http://localhost:8000/attack-history?limit=10 \
  -H "Authorization: Bearer <your-token>"
```

**Expected:**
```json
{
  "attacks": [...],
  "statistics": {
    "total_attacks": 5,
    "attack_types": {...},
    "severity_distribution": {...}
  }
}
```

### Test 18: Unauthorized Access
```bash
curl http://localhost:8000/data
```

**Expected:**
- ✅ 401 Unauthorized
- ✅ Error message about missing token

### Test 19: Admin-Only Endpoint
```bash
# As operator
curl -X POST http://localhost:8000/set-params \
  -H "Authorization: Bearer <operator-token>" \
  -H "Content-Type: application/json" \
  -d '{"vehicleCount": 50}'
```

**Expected:**
- ✅ 403 Forbidden
- ✅ "Admin privileges required"

---

## Performance Testing

### Test 20: High Vehicle Count
**Steps:**
1. Login as admin
2. Set vehicle count to 500
3. Monitor performance

**Expected:**
- ✅ System handles 500 vehicles
- ✅ Smooth animations
- ✅ No lag in UI
- ✅ API responses < 500ms

### Test 21: Long Running Session
**Steps:**
1. Login and leave system running
2. Monitor for 1+ hour
3. Check for memory leaks

**Expected:**
- ✅ No memory leaks
- ✅ Consistent performance
- ✅ No crashes
- ✅ Smooth operation

### Test 22: Rapid Toggling
**Steps:**
1. Rapidly toggle attack mode on/off
2. Quickly change vehicle count
3. Open/close panels repeatedly

**Expected:**
- ✅ No crashes
- ✅ State remains consistent
- ✅ No race conditions
- ✅ Smooth transitions

---

## Security Testing

### Test 23: SQL Injection (N/A - No SQL)
**Status:** Not applicable (using in-memory dict)

### Test 24: XSS Prevention
**Steps:**
1. Try entering `<script>alert('xss')</script>` in username
2. Check if script executes

**Expected:**
- ✅ Script does not execute
- ✅ Input sanitized
- ✅ No XSS vulnerability

### Test 25: CORS Configuration
**Steps:**
1. Try accessing API from different origin
2. Check CORS headers

**Expected:**
- ✅ CORS properly configured
- ✅ Only allowed origins accepted
- ✅ Credentials handled correctly

### Test 26: Token Tampering
**Steps:**
1. Get valid token
2. Modify token payload
3. Try using modified token

**Expected:**
- ✅ Modified token rejected
- ✅ 401 Unauthorized
- ✅ JWT signature validation works

---

## Model Testing

### Test 27: Model Accuracy
```bash
cd backend
python calculate_accuracy.py
```

**Expected:**
- ✅ Accuracy: ~96.5%
- ✅ F1-Score: ~94.2%
- ✅ Metrics displayed correctly

### Test 28: Real-Time Detection
**Steps:**
1. Enable attack mode
2. Monitor detection rate
3. Check false positives

**Expected:**
- ✅ Attacks detected within 1-2 seconds
- ✅ False positive rate < 5%
- ✅ False negative rate < 10%
- ✅ Consistent detection

---

## Browser Compatibility

### Test 29: Chrome
- ✅ Login works
- ✅ Dashboard renders correctly
- ✅ Animations smooth
- ✅ No console errors

### Test 30: Firefox
- ✅ All features work
- ✅ Layout correct
- ✅ Performance good

### Test 31: Edge
- ✅ Compatible
- ✅ No issues

### Test 32: Safari (if available)
- ✅ Works on macOS/iOS
- ✅ No compatibility issues

---

## Mobile Responsiveness

### Test 33: Mobile View
**Steps:**
1. Open on mobile device or use browser dev tools
2. Test all features

**Expected:**
- ✅ Responsive layout
- ✅ Touch interactions work
- ✅ Readable text
- ✅ Accessible buttons

---

## Error Handling

### Test 34: Backend Down
**Steps:**
1. Stop backend server
2. Try using frontend

**Expected:**
- ✅ Graceful error messages
- ✅ No crashes
- ✅ User informed of issue

### Test 35: Network Errors
**Steps:**
1. Simulate network issues
2. Check error handling

**Expected:**
- ✅ Retry logic works
- ✅ User notified
- ✅ System recovers when network restored

---

## Test Results Template

```
Test Date: ___________
Tester: ___________
Version: 3.0.0

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Admin Login | ✅ | |
| 2 | Operator Login | ✅ | |
| ... | ... | ... | ... |

Overall Status: ___________
Issues Found: ___________
```

---

## Automated Testing (Future)

### Unit Tests
```bash
# Backend
cd backend
pytest tests/

# Frontend
cd client
npm test
```

### Integration Tests
```bash
# End-to-end tests
npm run test:e2e
```

### Load Tests
```bash
# Using locust or similar
locust -f load_test.py
```

---

## Bug Reporting Template

```
**Bug Title**: 
**Severity**: Critical / High / Medium / Low
**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:

**Actual Behavior**:

**Screenshots**:

**Environment**:
- Browser:
- OS:
- Version:

**Additional Notes**:
```

---

**Testing Complete!** ✅

All tests passing = System ready for deployment
