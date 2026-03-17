# VANET Anomaly Detection System - Documentation Index

## 🚀 Getting Started

### Essential Documents
1. **[START_HERE.md](START_HERE.md)** - Quick start guide and first steps
2. **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Complete system guide (READ THIS!)
3. **[INSTALLATION.md](INSTALLATION.md)** - Detailed setup instructions
4. **[README.md](README.md)** - Project overview

---

## 📚 Core Documentation

### System Understanding
- **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Everything you need to know
  - Quick start
  - Attack types
  - User management
  - Analytics
  - API reference
  - Troubleshooting
  - Best practices

### Technical Details
- **[DATABASE_GUIDE.md](DATABASE_GUIDE.md)** - Database schema and operations
- **[ATTACK_TYPES_GUIDE.md](ATTACK_TYPES_GUIDE.md)** - Attack classification details
- **[METRICS_EXPLAINED.md](METRICS_EXPLAINED.md)** - Understanding system metrics
- **[MODEL_EVALUATION_GUIDE.md](MODEL_EVALUATION_GUIDE.md)** - LSTM model details

### User Guides
- **[USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md)** - Admin user management
- **[ENTERPRISE_USER_MANAGEMENT.md](ENTERPRISE_USER_MANAGEMENT.md)** - Advanced features
- **[PASSWORD_RESET_GUIDE.md](PASSWORD_RESET_GUIDE.md)** - Password reset feature
- **[ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md)** - Attack testing guide
- **[REAL_ATTACK_DETECTION.md](REAL_ATTACK_DETECTION.md)** - Attack architecture
- **[ATTACK_LOG_MANAGEMENT.md](ATTACK_LOG_MANAGEMENT.md)** - Log management
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference

### Deployment
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Production deployment
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing procedures
- **[PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)** - Performance tuning
- **[CLEANUP_GUIDE.md](CLEANUP_GUIDE.md)** - Folder size management

### Dataset
- **[DATASET_EXPLANATION.md](DATASET_EXPLANATION.md)** - VeReMi dataset details

---

## 🎯 Quick Access by Task

### I want to...

**Start the system**
→ [START_HERE.md](START_HERE.md)

**Understand how it works**
→ [HOW_IT_WORKS.md](HOW_IT_WORKS.md)

**Manage users**
→ [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md)

**View analytics**
→ [HOW_IT_WORKS.md](HOW_IT_WORKS.md#-analytics-dashboard)

**Understand attacks**
→ [ATTACK_TYPES_GUIDE.md](ATTACK_TYPES_GUIDE.md)

**Check metrics**
→ [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md)

**Test attack detection**
→ [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md)

**Reset user password**
→ [PASSWORD_RESET_GUIDE.md](PASSWORD_RESET_GUIDE.md)

**Delete attack logs**
→ [ATTACK_LOG_MANAGEMENT.md](ATTACK_LOG_MANAGEMENT.md)

**Test the system**
→ [TESTING_GUIDE.md](TESTING_GUIDE.md)

**Troubleshoot issues**
→ [HOW_IT_WORKS.md](HOW_IT_WORKS.md#-troubleshooting)

---

## 📖 Documentation Structure

```
Documentation/
├── START_HERE.md                    # Start here!
├── HOW_IT_WORKS.md                  # Complete guide (MAIN DOC)
├── README.md                        # Project overview
├── INSTALLATION.md                  # Setup instructions
│
├── Core Guides/
│   ├── DATABASE_GUIDE.md           # Database details
│   ├── ATTACK_TYPES_GUIDE.md       # Attack classification
│   ├── METRICS_EXPLAINED.md        # System metrics
│   └── MODEL_EVALUATION_GUIDE.md   # ML model details
│
├── User Management/
│   ├── USER_MANAGEMENT_GUIDE.md    # Basic user admin
│   ├── ENTERPRISE_USER_MANAGEMENT.md # Advanced features
│   ├── PASSWORD_RESET_GUIDE.md     # Password reset
│   └── USER_PERSISTENCE_FIX.md     # Database persistence
│
├── Attack Testing/
│   ├── ATTACK_INJECTOR_GUIDE.md    # Attack testing tool
│   ├── REAL_ATTACK_DETECTION.md    # Architecture explained
│   └── ATTACK_LOG_MANAGEMENT.md    # Log management
│
├── Operations/
│   ├── DEPLOYMENT_CHECKLIST.md     # Production deployment
│   ├── TESTING_GUIDE.md            # Testing procedures
│   ├── PERFORMANCE_OPTIMIZATION.md # Performance tuning
│   ├── CLEANUP_GUIDE.md            # Folder management
│   └── QUICK_REFERENCE.md          # Quick commands
│
└── Dataset/
    └── DATASET_EXPLANATION.md      # VeReMi dataset info
```

---

## 🎓 Learning Path

### Beginner
1. Read [START_HERE.md](START_HERE.md)
2. Follow installation steps
3. Login and explore dashboard
4. Read [HOW_IT_WORKS.md](HOW_IT_WORKS.md) sections 1-5

### Intermediate
1. Understand [ATTACK_TYPES_GUIDE.md](ATTACK_TYPES_GUIDE.md)
2. Learn [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md)
3. Explore analytics dashboard
4. Read [DATABASE_GUIDE.md](DATABASE_GUIDE.md)

### Advanced
1. Study [MODEL_EVALUATION_GUIDE.md](MODEL_EVALUATION_GUIDE.md)
2. Master [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md)
3. Review [ENTERPRISE_USER_MANAGEMENT.md](ENTERPRISE_USER_MANAGEMENT.md)
4. Prepare for production with [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 🔧 Utilities

### Helper Scripts
- **test_backend.py** - Backend diagnostic tool
- **system_check.py** - System requirements check
- **extract_50k.py** - Dataset extraction utility
- **run_project.bat** - Windows quick start script

### API Documentation
- **Interactive Docs:** http://localhost:8000/docs
- Complete endpoint reference
- Try-it-out functionality

---

## 📊 System Information

**Version:** 4.0.0 Enterprise Edition  
**Model:** LSTM-Autoencoder  
**Accuracy:** 96.5%  
**F1-Score:** 94.2%  
**Dataset:** VeReMi (50,000 samples)  
**Detection Threshold:** 0.1114  
**Vehicle Capacity:** 10-2000 units  
**Polling Rate:** 250ms (4 updates/second)  
**Architecture:** Separate attack injector for realistic testing

---

## 🆘 Need Help?

1. **Check [HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Most comprehensive guide
2. **Run diagnostic:** `python test_backend.py`
3. **Check logs:** `backend/vanet_system.log`
4. **API docs:** http://localhost:8000/docs
5. **Browser console:** Press F12 for frontend logs

---

## 📝 Document Descriptions

| Document | Purpose | Audience |
|----------|---------|----------|
| START_HERE.md | Quick start guide | Everyone |
| HOW_IT_WORKS.md | Complete system guide | Everyone |
| README.md | Project overview | Everyone |
| INSTALLATION.md | Setup instructions | Developers |
| DATABASE_GUIDE.md | Database details | Developers |
| ATTACK_TYPES_GUIDE.md | Attack classification | Operators/Admins |
| METRICS_EXPLAINED.md | System metrics | Operators/Admins |
| MODEL_EVALUATION_GUIDE.md | ML model details | Data Scientists |
| USER_MANAGEMENT_GUIDE.md | User administration | Admins |
| ENTERPRISE_USER_MANAGEMENT.md | Advanced features | Admins |
| DEPLOYMENT_CHECKLIST.md | Production deployment | DevOps |
| TESTING_GUIDE.md | Testing procedures | QA/Developers |
| QUICK_REFERENCE.md | Quick commands | Everyone |
| DATASET_EXPLANATION.md | Dataset information | Researchers |

---

## 🎯 Most Important Documents

### Must Read (Top 3)
1. **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** ⭐⭐⭐
2. **[START_HERE.md](START_HERE.md)** ⭐⭐
3. **[USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md)** ⭐⭐

### For Admins
- [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md)
- [ENTERPRISE_USER_MANAGEMENT.md](ENTERPRISE_USER_MANAGEMENT.md)
- [PASSWORD_RESET_GUIDE.md](PASSWORD_RESET_GUIDE.md)
- [ATTACK_LOG_MANAGEMENT.md](ATTACK_LOG_MANAGEMENT.md)
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

### For Operators
- [HOW_IT_WORKS.md](HOW_IT_WORKS.md)
- [ATTACK_TYPES_GUIDE.md](ATTACK_TYPES_GUIDE.md)
- [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md)
- [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md)

### For Developers
- [DATABASE_GUIDE.md](DATABASE_GUIDE.md)
- [MODEL_EVALUATION_GUIDE.md](MODEL_EVALUATION_GUIDE.md)
- [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

**Last Updated:** February 2026  
**System Status:** Production Ready ✅
