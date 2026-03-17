# Quick Reference Guide - VANET System v4.0

## 🚀 Quick Start

```bash
# Start everything (Windows)
run_project.bat

# Or manually:
cd backend && python -m uvicorn main:app --reload --port 8000
cd client && npm run dev

# Test attack detection (optional)
python attack_injector.py --duration 60
```

**Access**: http://localhost:5173  
**Login**: admin / admin123

---

## 🔐 Authentication

### Login
```javascript
// Frontend
const { login } = useAuth();
await login('admin', 'admin123');

// API
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

### Use Token
```javascript
// Frontend - automatic via useTrafficData(token)

// API
GET /data
Authorization: Bearer <your-token>
```

---

## 🎯 Attack Types

| Type | Icon | Severity | Detection Threshold |
|------|------|----------|---------------------|
| GPS Spoofing | 📡 | HIGH | Position jump >15 units |
| Position Falsification | 📍 | MEDIUM | Position jump 8-15 units |
| Sybil Attack | 👥 | HIGH | Position clustering <5 |
| DoS Attack | 💥 | HIGH | Message rate >100 |
| Message Tampering | ✏️ | MEDIUM | Velocity inconsistency >2 |
| Replay Attack | 🔁 | LOW | Jerk magnitude <0.05 |

---

## 📡 API Endpoints

### Public
```
POST /auth/login          # Login (no auth required)
```

### Authenticated (All Users)
```
GET  /                    # API info
GET  /health              # Health check
GET  /data                # Vehicle data + classifications
GET  /model-info          # Model information
GET  /attack-history      # Attack logs
POST /set-scenario        # Toggle attack mode (used by injector)
```

### Admin Only
```
POST   /set-params                           # Change vehicle count
POST   /auth/reset-password/{username}       # Reset user password
DELETE /attack-history/all                   # Delete all logs
DELETE /attack-history/older-than?days=X     # Delete old logs
DELETE /attack-history/date-range?start=X&end=Y  # Delete by range
```

---

## 🎨 UI Components

### Sidebar Buttons
- **M** - Toggle map view
- **AlertTriangle** - Open attack panel
- **Settings** - Open settings panel
- **User** - User profile / User management (admin)
- **LogOut** - Logout

### Attack Panel
- Real-time threat list
- Attack statistics
- Severity indicators
- Confidence scores
- Primary indicators

### User Management (Admin)
- Add/remove users
- Reset passwords (🔑 icon)
- View user list
- Cannot reset own password

---

## 🔧 Configuration

### Backend (.env)
```env
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (useTrafficData.js)
```javascript
const API_URL = "http://localhost:8000";
const THRESHOLD = 0.1114;
```

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access: view, modify, delete |
| **Operator** | Read-only: view data, toggle attacks |

---

## 🐛 Debugging

### Check Backend
```bash
curl http://localhost:8000/
```

### Check Auth
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Check Data
```bash
curl http://localhost:8000/data \
  -H "Authorization: Bearer <token>"
```

### Browser Console
```javascript
// Check token
localStorage.getItem('vanet_token')

// Check user
localStorage.getItem('vanet_user')

// Clear auth
localStorage.clear()
```

---

## 📊 Data Structure

### Vehicle Data
```json
{
  "id": 0,
  "x": 45.2,
  "y": 67.8,
  "speed": 35.5,
  "reconstruction_error": 0.2341,
  "is_anomaly": true,
  "attack_classification": {
    "attack_type": "GPS Spoofing",
    "confidence": 0.87,
    "severity": "HIGH",
    "details": {
      "primary_indicators": [
        "Extreme position jump: 18.5 units"
      ],
      "all_scores": { ... }
    }
  }
}
```

### Attack History
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "vehicle_id": 3,
  "position": {"x": 45.2, "y": 67.8},
  "attack_type": "GPS Spoofing",
  "confidence": 0.87,
  "severity": "HIGH",
  "reconstruction_error": 0.2341
}
```

---

## 🎯 Common Tasks

### Test Attack Detection
```bash
# 30-second campaign (default)
python attack_injector.py

# Custom duration
python attack_injector.py --duration 120

# Continuous mode
python attack_injector.py --continuous --interval 5

# Custom credentials
python attack_injector.py --username admin --password admin123
```

### Add New User
- Login as admin
- Click User icon → User Management
- Fill form and submit
- User persists in database

### Reset User Password
- Login as admin
- User Management → Click 🔑 icon
- Cannot reset own password or admin account

### Delete Attack Logs
```bash
# Delete all
curl -X DELETE http://localhost:8000/attack-history/all \
  -H "Authorization: Bearer <token>"

# Delete older than 7 days
curl -X DELETE "http://localhost:8000/attack-history/older-than?days=7" \
  -H "Authorization: Bearer <token>"

# Delete by date range
curl -X DELETE "http://localhost:8000/attack-history/date-range?start_date=2026-02-01&end_date=2026-02-15" \
  -H "Authorization: Bearer <token>"
```

### Change Token Expiration
Edit `backend/.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Adjust Detection Threshold
Edit `backend/main.py`:
```python
DETECTION_THRESHOLD = 0.15  # Increase for fewer alerts
```

### Change Vehicle Count Range
Edit `backend/main.py`:
```python
if count and 10 <= count <= 2000:  # Current range
```

### Adjust Polling Rate
Edit `client/src/hooks/useTrafficData.js`:
```javascript
const POLLING_INTERVAL = 250;  // milliseconds (4 updates/sec)
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Login fails | Check backend running, verify credentials |
| Token expired | Login again, increase expiration time |
| No attacks showing | Run attack injector: `python attack_injector.py` |
| CORS error | Check backend CORS middleware |
| Port in use | Change port in uvicorn/vite command |
| Users not persisting | Check database.py, users table |
| Can't reset password | Must be admin, can't reset own/admin password |

---

## 📚 File Structure

```
backend/
├── main.py              # FastAPI app
├── auth.py              # Authentication
├── attack_classifier.py # Attack classification
├── .env                 # Configuration
└── requirements.txt     # Dependencies

client/
├── src/
│   ├── components/
│   │   ├── LoginPhase.jsx
│   │   ├── DashboardPhase.jsx
│   │   ├── AttackPanel.jsx
│   │   └── TrafficMap.jsx
│   ├── contexts/
│   │   └── AuthContext.jsx
│   └── hooks/
│       └── useTrafficData.js
└── package.json
```

---

## 🎓 Learning Resources

- **API Docs**: http://localhost:8000/docs
- **SYSTEM_UPDATES_V4.md**: v4.0 features
- **ATTACK_INJECTOR_GUIDE.md**: Attack testing
- **USER_MANAGEMENT_GUIDE.md**: User admin
- **INSTALLATION.md**: Setup instructions

---

## 💡 Tips

1. **Use Admin account** for full testing
2. **Run attack injector** to test detection
3. **Open attack panel** for detailed threat info
4. **Hover over vehicles** on map for tooltips
5. **Check browser console** for errors
6. **Monitor backend logs** for API issues
7. **Users persist** in database across restarts
8. **Admin can reset** any user's password
9. **Vehicle limit** increased to 2000
10. **Performance optimized** for high vehicle counts

---

## 🔗 URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

---

## 📞 Support

1. Check this quick reference
2. Review IMPROVEMENTS.md
3. Check API documentation
4. Review browser/backend logs
5. Clear cache and retry

---

**Version**: 4.0.0 Enterprise Edition  
**Last Updated**: February 2026  
**Status**: Production Ready
