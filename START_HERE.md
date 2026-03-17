# 🚀 VANET System v4.0 - Quick Start Guide

## Welcome! 👋

This is your complete VANET Anomaly Detection System with JWT authentication, attack classification, and realistic attack testing.

---

## ⚡ Quick Start (3 Steps)

### Step 1: Start Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Step 2: Start Frontend (New Terminal)
```bash
cd client
npm run dev
```

### Step 3: Login
- Open: http://localhost:5173
- Username: `admin`
- Password: `admin123`

**That's it!** 🎉

### Step 4 (Optional): Test Attack Detection
```bash
# Run 60-second attack campaign
python attack_injector.py --duration 60

# Or continuous mode
python attack_injector.py --continuous
```

See [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md) for details.

---

## 📚 Documentation Index

### Getting Started
- **START_HERE.md** ← You are here
- **INSTALLATION.md** - Detailed setup instructions
- **README.md** - Project overview

### Features & Improvements
- **SYSTEM_UPDATES_V4.md** - v4.0 features and improvements
- **USER_PERSISTENCE_FIX.md** - Database persistence implementation
- **PASSWORD_RESET_GUIDE.md** - Admin password reset feature
- **ATTACK_INJECTOR_GUIDE.md** - Realistic attack testing
- **REAL_ATTACK_DETECTION.md** - Attack architecture explained
- **ATTACK_LOG_MANAGEMENT.md** - Log management features
- **PERFORMANCE_OPTIMIZATION.md** - Performance improvements

### User Guides
- **USER_MANAGEMENT_GUIDE.md** - How to add multiple users
- **ATTACK_TYPES_GUIDE.md** - Attack detection explained
- **QUICK_REFERENCE.md** - Developer quick reference

### Technical Documentation
- **DATASET_INFO.md** - Dataset structure and usage
- **MODEL_EVALUATION_GUIDE.md** - Model performance metrics
- **API Documentation** - http://localhost:8000/docs (when running)

---

## 🔐 Default Credentials

### Admin Account (Full Access)
- Username: `admin`
- Password: `admin123`

### Operator Accounts (Read-Only)
- `operator` / `operator123`
- `operator2` / `pass123`
- `operator3` / `pass456`
- `john` / `john123`
- `alice` / `alice123`
- `bob` / `bob123`

⚠️ **Change these in production!**

---

## ✨ Key Features

### 🔒 Security
- JWT token authentication
- Role-based access control (Admin/Operator)
- Password hashing with bcrypt
- Protected API endpoints

### 🎯 Attack Detection
- **6 Attack Types**:
  - 📡 GPS Spoofing
  - 📍 Position Falsification
  - 👥 Sybil Attack
  - 💥 DoS Attack
  - ✏️ Message Tampering
  - 🔁 Replay Attack
- Real-time classification
- Confidence scoring
- Severity levels

### 📊 Monitoring
- Live traffic visualization
- Attack panel with threat details
- Color-coded attack types (dark green=normal)
- Attack history logging
- Real-time statistics
- Flexible log management (delete all, by date, by range)

---

## 🎮 How to Use

### 1. Login
- Enter your credentials
- System validates and issues JWT token

### 2. Monitor Traffic
- View live vehicle positions on map
- Dark green = Normal, Colors = Different attack types
- Hover over vehicles for details

### 3. Test Attack Detection (Optional)
- Open new terminal
- Run: `python attack_injector.py --duration 60`
- Watch dashboard detect attacks in real-time
- See [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md)

### 4. View Attack Panel
- Click AlertTriangle icon
- See all active threats
- Check attack statistics
- Review severity levels

### 5. Adjust Settings (Admin Only)
- Click Settings icon
- Change vehicle density (10-2000)
- System updates in real-time

### 6. Manage Users (Admin Only)
- Click User icon → User Management
- Add/remove operators
- Reset passwords
- View audit logs

---

## 🛠️ Troubleshooting

### "Failed to fetch" on Login
**Problem**: Backend not running
**Solution**: 
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Port Already in Use
**Backend (8000)**:
```bash
# Change port
python -m uvicorn main:app --reload --port 8001
# Update API_URL in client/src/hooks/useTrafficData.js
```

**Frontend (5173)**:
```bash
# Vite will auto-select next available port
npm run dev
```

### Token Expired
**Solution**: Just login again (tokens expire after 30 minutes)

### Can't Change Settings
**Problem**: Logged in as Operator (read-only)
**Solution**: Login as Admin

---

## 📁 Project Structure

```
vanet-system/
├── backend/
│   ├── main.py                    # FastAPI server
│   ├── auth.py                    # Authentication
│   ├── attack_classifier.py       # Attack classification
│   ├── calculate_accuracy.py      # Model metrics
│   ├── vanet_anomaly_detector.h5  # Trained model
│   └── requirements.txt           # Dependencies
│
├── client/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── contexts/              # Auth context
│   │   └── hooks/                 # Custom hooks
│   └── package.json               # Dependencies
│
├── Documentation/
│   ├── START_HERE.md              # This file
│   ├── IMPROVEMENTS.md            # Feature docs
│   ├── USER_MANAGEMENT_GUIDE.md   # User guide
│   └── ... (more docs)
│
└── dataset_50k.csv                # Training data
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
```

### Add New User
Admin panel → User Management → Add User

### Reset User Password
Admin panel → User Management → Click key icon (🔑)

### Delete Attack Logs
```bash
# Via API (see ATTACK_LOG_MANAGEMENT.md)
DELETE /attack-history/all
DELETE /attack-history/older-than?days=7
DELETE /attack-history/date-range?start_date=2026-02-01&end_date=2026-02-15
```

### Change Token Expiration
Edit `backend/.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### View API Documentation
Open: http://localhost:8000/docs

### Check Model Performance
```bash
cd backend
python calculate_accuracy.py
```

---

## 🔗 Important URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

---

## 📊 System Performance

- **Accuracy**: 96.5%
- **F1-Score**: 94.2%
- **Detection Rate**: 93%
- **False Alarm Rate**: 3.5%
- **Vehicle Capacity**: 10-2000 units
- **Polling Rate**: 250ms (4 updates/second)

---

## 🆘 Need Help?

1. Check the relevant documentation file
2. Review error messages in terminal/console
3. Check browser console (F12) for frontend issues
4. Verify both backend and frontend are running
5. Ensure correct credentials

---

## 🎓 Learning Path

**Beginner**:
1. Read START_HERE.md (this file)
2. Follow Quick Start
3. Explore the UI
4. Try attack injector

**Intermediate**:
1. Read SYSTEM_UPDATES_V4.md
2. Review ATTACK_INJECTOR_GUIDE.md
3. Check API documentation
4. Manage users via admin panel

**Advanced**:
1. Study MODEL_EVALUATION_GUIDE.md
2. Review ATTACK_LOG_MANAGEMENT.md
3. Explore PERFORMANCE_OPTIMIZATION.md
4. Extend API endpoints

---

## 🚀 Next Steps

After getting started:

1. ✅ Login and explore the dashboard
2. ✅ Run attack injector to test detection
3. ✅ Open attack panel to see threat details
4. ✅ Try different user accounts
5. ✅ Adjust vehicle density (up to 2000)
6. ✅ Review attack history
7. ✅ Test user management features
8. ✅ Check API documentation

---

## 💡 Pro Tips

- Use **Admin** account for full testing
- **Operator** accounts are read-only
- Attack panel shows real-time threats
- Hover over vehicles for detailed info
- Check browser console for debugging
- Backend logs show authentication events
- Use attack injector for realistic testing
- Users persist in database across restarts
- Admin can reset any user's password

---

## 🎉 You're Ready!

Everything is set up and ready to go. Start the backend and frontend, then login to begin!

**Questions?** Check the documentation files listed above.

**Issues?** Review the Troubleshooting section.

**Enjoy using VANET Guardian System v4.0!** 🛡️

---

**Version**: 4.0.0 Enterprise Edition  
**Status**: Production Ready  
**Last Updated**: February 2026
