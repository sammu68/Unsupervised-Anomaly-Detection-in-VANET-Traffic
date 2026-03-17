# User Persistence Fix

## Problems Fixed

### Problem 1: User Changes Not Persisting
User changes (register, delete, update, password reset) were only stored in memory (`fake_users_db` dictionary). When the backend restarted, all changes were lost and the system reverted to default users.

### Problem 2: Deleted Users Reappearing  
Even after implementing database persistence, deleted users would reappear on restart because the `NEW_USERS` list was re-adding them every time the backend started.

## Solutions

### Solution 1: Database Persistence
Implemented full database persistence using SQLite for all user data.

### Solution 2: One-Time Initialization
Changed user initialization to only add users from `INITIAL_USERS` list when database is completely empty (first time setup only). After that, the system respects all admin changes including deletions.

---

## Changes Made

### 1. Database Schema (`backend/database.py`)
Added `users` table:
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    disabled INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### 2. Database Functions (`backend/database.py`)
Added user persistence functions:
- `load_users_from_db()` - Load all users from database into memory
- `save_user_to_db()` - Save/update user in database
- `delete_user_from_db()` - Delete user from database
- `update_user_password_in_db()` - Update password in database
- `update_user_in_db()` - Update user info in database
- `toggle_user_disabled_in_db()` - Toggle disabled status in database

### 3. Authentication Module (`backend/auth.py`)
- Load users from database on startup
- Initialize database with default users if empty
- Changed `NEW_USERS` to `INITIAL_USERS` - only added on first setup
- Prevents deleted users from reappearing on restart
- Shows count of loaded users in console

### 4. API Endpoints (`backend/main.py`)
Updated all user management endpoints to sync with database:
- `POST /auth/register` - Save new user to database
- `POST /auth/change-password` - Update password in database
- `POST /auth/reset-password/{username}` - Update password in database
- `PUT /auth/users/{username}` - Update user info in database
- `DELETE /auth/users/{username}` - Delete user from database
- `PATCH /auth/users/{username}/toggle` - Update disabled status in database

---

## How It Works

### On First Backend Startup (Empty Database)
1. Database initializes and creates `users` table
2. `auth.py` finds database is empty
3. Creates default users (admin, operator)
4. Creates initial users from `INITIAL_USERS` list
5. All users saved to database
6. Console shows: "✓ Created X initial users"

### On Subsequent Startups (Database Has Users)
1. Database already has `users` table
2. `auth.py` loads all users from database into `fake_users_db` dictionary
3. **Does NOT re-add users from `INITIAL_USERS` list**
4. Respects all admin changes (deletions, updates, etc.)
5. Console shows: "✓ Loaded X users from database"

### On User Operations
1. Operation performed on in-memory `fake_users_db` (fast)
2. Change immediately synced to database (persistent)
3. Both memory and database stay in sync

### On Backend Restart After User Changes
1. All users loaded from database (including new ones)
2. Deleted users stay deleted (not re-added)
3. Updated users keep their updates
4. No data loss

---

## Benefits

### Before (Memory Only)
- ❌ User changes lost on restart
- ❌ Had to manually re-add users
- ❌ No persistence
- ❌ Testing was difficult
- ❌ Deleted users reappeared

### After (Database Persistence + One-Time Init)
- ✅ User changes survive restarts
- ✅ Automatic persistence
- ✅ Production-ready
- ✅ Easy testing and development
- ✅ Deleted users stay deleted
- ✅ New users persist correctly

---

## Database Location

User data stored in: `backend/vanet_data.db`

This SQLite database file contains:
- `users` table - All user accounts
- `attack_logs` table - Attack history
- `system_metrics` table - Performance metrics
- `audit_logs` table - User activity logs

---

## Migration

### First Time Running Updated Code
1. Existing `vanet_data.db` will be updated with `users` table
2. Default users (admin, operator) will be created
3. Additional users from `NEW_USERS` list will be added

### No Data Loss
- Existing attack logs and metrics are preserved
- Only adds new `users` table
- Safe to run on existing database

---

## Testing

### Test User Persistence
1. Start backend
2. Login as admin
3. Register a new operator (e.g., "testuser")
4. Stop backend (Ctrl+C)
5. Start backend again
6. Login as admin
7. Check Manage tab - "testuser" should still be there!

### Test User Deletion Persistence
1. Start backend
2. Login as admin
3. Delete a user (e.g., "bob")
4. Stop backend (Ctrl+C)
5. Start backend again
6. Login as admin
7. Check Manage tab - "bob" should NOT be there! ✅
8. User stays deleted permanently

### Test Password Changes
1. Change a user's password
2. Restart backend
3. Login with new password - should work!

---

## Backup & Recovery

### Backup Users
```bash
# Copy database file
cp backend/vanet_data.db backend/vanet_data_backup.db
```

### Restore Users
```bash
# Restore from backup
cp backend/vanet_data_backup.db backend/vanet_data.db
```

### Export Users (Future Enhancement)
Could add CSV export for users similar to attack logs.

---

## Performance

### Memory + Database Hybrid
- **Read operations:** Fast (from memory)
- **Write operations:** Slightly slower (sync to database)
- **Startup:** Minimal delay (load from database)

### Scalability
- Suitable for 100s of users
- For 1000s of users, consider PostgreSQL/MySQL
- Current SQLite implementation is production-ready for typical use

---

## Security Notes

### Password Storage
- Passwords hashed with bcrypt
- Hashes stored in database
- Plain passwords never stored

### Database Security
- SQLite file should have restricted permissions
- In production, set file permissions: `chmod 600 vanet_data.db`
- Consider encrypting database file for sensitive deployments

---

## Troubleshooting

### Issue: Users not persisting
**Check:**
1. Database file exists: `backend/vanet_data.db`
2. File has write permissions
3. No database errors in backend logs

### Issue: "Database is locked"
**Cause:** Multiple processes accessing database

**Solution:** Ensure only one backend instance running

### Issue: Users reset to defaults
**Cause:** Database file deleted or corrupted

**Solution:** Restore from backup or re-register users

---

## Future Enhancements

### Possible Improvements
1. User roles beyond admin/operator
2. User groups and permissions
3. Password expiry policies
4. Login attempt tracking
5. Session management
6. Two-factor authentication
7. User profile pictures
8. Email notifications

---

**Fixed:** February 24, 2026  
**Version:** 4.0.0 Enterprise Edition  
**Status:** Production Ready
