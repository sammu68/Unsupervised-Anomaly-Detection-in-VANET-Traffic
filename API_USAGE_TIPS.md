# API Documentation Usage Tips

## 🎯 Quick Start

### Access API Documentation
Navigate to: **http://localhost:8000/docs**

---

## 🔐 Authorization (One-Time Setup)

### Step 1: Get Your Token

**Method A: From React App (Easiest)**
1. Login to http://localhost:5173
2. Press F12 (open DevTools)
3. Go to Console tab
4. Type: `localStorage.getItem('token')`
5. Copy the token (without quotes)

**Method B: From Swagger UI**
1. In Swagger, expand `POST /auth/login`
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. Click "Execute"
5. Copy `access_token` from response

### Step 2: Authorize in Swagger
1. Click the **"Authorize"** button (🔒 icon, top right)
2. In the popup, enter: `Bearer YOUR_TOKEN`
   - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Click **"Authorize"**
4. Click **"Close"**

### ✅ Done! Token Persists Automatically

Your token is now saved in browser storage and will:
- ✅ Remain active after page refresh
- ✅ Work for all API calls
- ✅ Stay until you logout or it expires (30 minutes)

---

## 🚀 Using API Endpoints

### Example: Delete Attack Logs

1. **Expand the endpoint** you want to use
   - Example: `DELETE /attack-history/date-range`

2. **Click "Try it out"** button

3. **Enter parameters**
   - `start_date`: 2026-02-24
   - `end_date`: 2026-02-24

4. **Click "Execute"**

5. **View response** below
   ```json
   {
     "status": "cleared",
     "cleared_count": {
       "memory": 150,
       "database": 1250,
       "total": 1400
     }
   }
   ```

---

## 🔄 Token Expiration

### When Token Expires (30 minutes)
You'll see error: `401 Unauthorized` or `Token expired`

### Solution:
1. Get a new token (see Step 1 above)
2. Click "Authorize" button again
3. Enter new token
4. Continue working

---

## 💡 Pro Tips

### 1. Keep Token Handy
Save your token in a text file during development:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. Use Browser DevTools
- Network tab: See actual API requests/responses
- Console tab: Debug issues
- Application tab: View localStorage (where token is stored)

### 3. Test Endpoints Quickly
Swagger UI is faster than writing curl commands:
- No need to format JSON manually
- Auto-completion for parameters
- Instant response visualization
- Built-in validation

### 4. Copy as cURL
After executing a request:
1. Scroll down to response section
2. Click "Copy" button next to curl command
3. Use in terminal or scripts

### 5. Multiple Tabs
Open multiple Swagger tabs:
- Tab 1: Keep login endpoint open
- Tab 2: Test your actual endpoints
- Token persists across all tabs!

---

## 🛠️ Common Issues

### Issue: "Unauthorized" Error
**Cause:** Token not set or expired

**Solution:**
1. Check if you clicked "Authorize" button
2. Verify token format: `Bearer YOUR_TOKEN`
3. Get a new token if expired

---

### Issue: "Forbidden" Error
**Cause:** Insufficient permissions (not admin)

**Solution:**
- Login as admin user
- Operators cannot access admin-only endpoints

---

### Issue: Token Disappears After Refresh
**Cause:** Old version without persistence

**Solution:**
- Restart backend (token persistence is now enabled)
- Re-authorize once
- Token will now persist!

---

### Issue: "Failed to Fetch"
**Cause:** Backend not running

**Solution:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

---

## 📚 Endpoint Categories

### 🔐 Authentication
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - View current user
- `POST /auth/change-password` - Change password
- `POST /auth/register` - Register new user (admin)
- `GET /auth/users` - List all users (admin)

### 📊 Monitoring
- `GET /data` - Real-time vehicle data
- `GET /health` - System health check
- `GET /attack-history` - Attack logs

### ⚙️ Control
- `POST /set-scenario` - Toggle attack simulation
- `POST /set-params` - Adjust vehicle count (admin)

### 📈 Analytics
- `GET /analytics/attack-stats` - Attack statistics
- `GET /analytics/metrics` - System metrics
- `GET /analytics/audit-logs` - Audit trail
- `DELETE /attack-history/*` - Delete attack logs (admin)

---

## 🎓 Learning Path

### Beginner
1. Login and get token
2. Try `GET /health` (no auth needed)
3. Authorize with token
4. Try `GET /auth/me` (see your user info)

### Intermediate
1. View attack history: `GET /attack-history`
2. Get statistics: `GET /analytics/attack-stats`
3. Toggle attack mode: `POST /set-scenario`

### Advanced
1. Delete specific date range attacks
2. Export data to CSV
3. Manage users (admin only)
4. Review audit logs

---

## 🔗 Related Documentation

- [Attack Log Management](ATTACK_LOG_MANAGEMENT.md) - Detailed deletion guide
- [User Management Guide](USER_MANAGEMENT_GUIDE.md) - User CRUD operations
- [API Reference](http://localhost:8000/docs) - Live API documentation
- [Quick Reference](QUICK_REFERENCE.md) - Command cheat sheet

---

## 🆘 Need Help?

1. **Check Response:** Error messages are descriptive
2. **View Logs:** Backend terminal shows detailed logs
3. **Test Backend:** Run `python test_backend.py`
4. **Read Docs:** Each endpoint has detailed description

---

**Pro Tip:** Bookmark http://localhost:8000/docs for quick access during development!

---

**Last Updated:** February 24, 2026  
**Version:** 4.0.0 Enterprise Edition
