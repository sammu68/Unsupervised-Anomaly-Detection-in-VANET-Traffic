# VANET Anomaly Detection System v4.0

Real-time anomaly detection in Vehicular Ad-hoc Networks using LSTM-Autoencoder with JWT authentication and attack classification.

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-4.0.0-blue)]()
[![Accuracy](https://img.shields.io/badge/accuracy-96.5%25-success)]()

---

## 🚀 Quick Start

```bash
# 1. Start Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# 2. Start Frontend (new terminal)
cd client
npm run dev

# 3. Login at http://localhost:5173
Username: admin
Password: admin123

# 4. (Optional) Test Attack Detection
python attack_injector.py --duration 60
```

**Full guide:** [START_HERE.md](START_HERE.md)

---

## ✨ Key Features

### 🔒 Security
- JWT token authentication with bcrypt password hashing
- Role-based access control (Admin/Operator)
- Protected API endpoints

### 🎯 Attack Detection & Classification
Detects and classifies **19 attack types** from VeReMi dataset into 6 categories:
- 📡 **GPS Spoofing** - Extreme position falsification
- 📍 **Position Falsification** - False position reporting  
- 👥 **Sybil Attack** - Multiple fake identities
- 💥 **DoS Attack** - Network flooding
- ✏️ **Message Tampering** - Altered messages
- 🔁 **Replay Attack** - Resending old messages

### 📊 Real-time Monitoring
- Live traffic visualization (10-2000 vehicles)
- Color-coded attack types on map
- Attack panel with detailed threat info
- Attack history logging
- 96.5% detection accuracy

### 🎯 Realistic Attack Testing
- Separate attack injector application
- Simulates external attacks
- Campaign and continuous modes
- Professional testing environment
- See [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md)

---

## 📁 Project Structure

```
vanet-system/
├── backend/
│   ├── main.py                    # FastAPI server
│   ├── auth.py                    # JWT authentication
│   ├── attack_classifier.py       # Attack classification
│   ├── calculate_accuracy.py      # Model evaluation
│   ├── vanet_anomaly_detector.h5  # Trained LSTM model
│   └── requirements.txt
├── client/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── contexts/              # Auth context
│   │   └── hooks/                 # Custom hooks
│   └── package.json
└── dataset_50k.csv                # VeReMi training data
```

---

## 🔐 Default Credentials

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Full access + password reset |
| Operator | `operator` | `operator123` | Read-only |

**Additional operators:** operator2, operator3, john, alice, bob (see [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md))

⚠️ **Change passwords in production!**

**Forgot Password?** Contact admin for password reset (see [PASSWORD_RESET_GUIDE.md](PASSWORD_RESET_GUIDE.md))

---

## 📊 Dataset Information

**Source:** VeReMi (Vehicular Reference Misbehavior) Dataset
- **Size:** 50,000 samples
- **Normal:** 27,302 (54.6%)
- **Attacks:** 22,698 (45.4%)
- **Attack Types:** 19 different types

**Key Columns:**
- `pos_0, pos_1` - Vehicle position (X, Y)
- `spd_0, spd_1` - Vehicle speed
- `attack` - Binary label (0=normal, 1=attack)
- `attack_type` - Specific attack name

**19 Attack Types in Dataset:**
GridSybil, DoS, DoSDisruptive, DoSRandom, DoSRandomSybil, DataReplay, ConstPosOffset, DataReplaySybil, DoSDisruptiveSybil, ConstSpeed, Disruptive, RandomPos, ConstPos, RandomSpeedOffset, ConstSpeedOffset, RandomSpeed, RandomPosOffset, EventualStop, DelayedMessages

---

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd client
npm install
```

**Detailed setup:** [INSTALLATION.md](INSTALLATION.md)

---

## 🎯 Usage

1. **Login** with credentials
2. **Monitor** live traffic on map (dark green=normal, colors=attacks)
3. **Test attacks** - Run `python attack_injector.py` (separate terminal)
4. **View threats** - Click AlertTriangle icon for attack panel
5. **Adjust settings** - Click Settings icon (admin only)

**Attack Testing:** See [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md) for realistic attack simulation

---

## 📈 Model Performance

- **Accuracy:** 96.5%
- **Precision:** 95.2%
- **Recall:** 93.1%
- **F1-Score:** 94.2%
- **Threshold:** 0.1114 (MSE)

**Calculate metrics:** `python backend/calculate_accuracy.py`

---

## 🔗 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Current user info

### Data & Monitoring
- `GET /data` - Real-time vehicle data with classifications
- `GET /health` - System health
- `GET /attack-history` - Attack logs

### Control (Authenticated)
- `POST /set-scenario` - Toggle attack mode (used by attack injector)
- `POST /set-params` - Adjust vehicle count (admin only)
- `POST /auth/reset-password/{username}` - Reset user password (admin only)

### Attack Log Management (Admin)
- `DELETE /attack-history/all` - Delete all attack logs
- `DELETE /attack-history/older-than?days=X` - Delete logs older than X days
- `DELETE /attack-history/date-range?start_date=X&end_date=Y` - Delete by date range

**API Docs:** http://localhost:8000/docs

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [START_HERE.md](START_HERE.md) | Quick start guide |
| [INSTALLATION.md](INSTALLATION.md) | Setup instructions |
| [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md) | Attack testing guide |
| [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md) | Add/manage users |
| [PASSWORD_RESET_GUIDE.md](PASSWORD_RESET_GUIDE.md) | Password reset feature |
| [ATTACK_TYPES_GUIDE.md](ATTACK_TYPES_GUIDE.md) | Attack detection details |
| [ATTACK_LOG_MANAGEMENT.md](ATTACK_LOG_MANAGEMENT.md) | Log management |
| [DATASET_EXPLANATION.md](DATASET_EXPLANATION.md) | Dataset structure explained |

**Full index:** [INDEX.md](INDEX.md)

---

## 🧪 Testing

```bash
# Check system health
python system_check.py

# Calculate model accuracy
cd backend
python calculate_accuracy.py

# Test attack detection (30-second campaign)
python attack_injector.py

# Continuous attack testing
python attack_injector.py --continuous --interval 5
```

**Full testing guide:** [TESTING_GUIDE.md](TESTING_GUIDE.md)  
**Attack testing guide:** [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md)

---

## 🚢 Deployment

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for production deployment steps.

---

## 🛠️ Tech Stack

**Frontend:** React 19, Vite, Tailwind CSS v4, Framer Motion, Recharts  
**Backend:** FastAPI, Uvicorn, TensorFlow, NumPy, Pandas, JWT, Bcrypt  
**Model:** LSTM-Autoencoder trained on VeReMi dataset  
**Security:** JWT tokens, bcrypt password hashing, RBAC

---

## 🆘 Troubleshooting

### 🚨 Traffic Map Shows 0 Vehicles?

**→ See [START_DEBUGGING.md](START_DEBUGGING.md) for instant fix!**

The console (F12) will tell you exactly what's wrong with detailed logging.

### Common Issues

**"Failed to fetch" on login**
- Ensure backend is running: `cd backend && python -m uvicorn main:app --reload --port 8000`

**Token expired**
- Login again (tokens expire after 30 minutes)

**Can't change settings**
- Login as admin (operators are read-only)

**No vehicles appearing**
1. Press F12 to open console
2. Check the error messages
3. Follow [TROUBLESHOOTING_STEPS.md](TROUBLESHOOTING_STEPS.md)

### 🧪 Diagnostic Tools

**Test backend automatically:**
```bash
python test_backend.py
```

**Comprehensive guides:**
- 📖 [START_DEBUGGING.md](START_DEBUGGING.md) - Quick visual guide
- 📋 [TROUBLESHOOTING_STEPS.md](TROUBLESHOOTING_STEPS.md) - Step-by-step fixes
- 🔧 [ZERO_VEHICLES_FIX.md](ZERO_VEHICLES_FIX.md) - Detailed diagnostics
- 📊 [SYNCHRONIZATION_FIX_V2.md](SYNCHRONIZATION_FIX_V2.md) - Technical details

---

## 📝 License

MIT License (or your license)

---

## 👥 Credits

**Version:** 4.0.0 Enterprise Edition  
**Status:** Production Ready  
**Model:** LSTM-Autoencoder  
**Dataset:** VeReMi  
**Architecture:** Separate attack injector for realistic testing

