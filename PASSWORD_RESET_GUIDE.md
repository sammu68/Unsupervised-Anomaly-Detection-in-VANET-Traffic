# Password Reset Guide (Admin)

## Overview
Admins can reset passwords for users who have forgotten their credentials. This is a manual process that requires admin intervention for security.

---

## 🔐 How It Works

### User Perspective
1. User forgets password
2. User contacts admin (phone, email, in-person)
3. Admin verifies user identity
4. Admin resets password
5. Admin provides temporary password to user
6. User logs in with temporary password
7. User changes password immediately

### Admin Perspective
1. Receive password reset request from user
2. Verify user identity (important!)
3. Open user management panel
4. Click key icon (🔑) next to user
5. Enter new temporary password
6. Provide password to user securely
7. Instruct user to change password after login

---

## 📱 Using the UI (React App)

### Step 1: Access User Management
1. Login as admin
2. Click user icon (👤) in sidebar
3. Go to "Manage" tab
4. Find the user who needs password reset

### Step 2: Reset Password
1. Click the **purple key icon** (🔑) next to the user
2. Enter a temporary password (min 6 characters)
3. Click "Reset Password"
4. Success notification appears

### Step 3: Provide Password to User
- Give the temporary password to the user securely
- Recommend they change it immediately after login

---

## 🔧 Using the API

### Endpoint
```
POST /auth/reset-password/{username}
```

### Request
```bash
curl -X POST "http://localhost:8000/auth/reset-password/operator" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "temp123456"}'
```

### Response
```json
{
  "status": "success",
  "message": "Password reset successfully for user 'operator'",
  "username": "operator",
  "reset_by": "admin",
  "note": "User should change this password after first login",
  "timestamp": "2026-02-24T10:30:00"
}
```

---

## 🛡️ Security Features

### Access Control
- **Admin only:** Only users with admin role can reset passwords
- **Cannot reset own password:** Admins must use change-password for themselves
- **Cannot reset admin account:** Admin account is protected

### Audit Trail
Every password reset is logged with:
- Admin who performed the reset
- Username whose password was reset
- Timestamp
- IP address

### View Audit Logs
```bash
GET /analytics/audit-logs
```

Look for action: `PASSWORD_RESET`

---

## 📋 Best Practices

### For Admins

1. **Verify Identity First**
   - Confirm user identity before resetting
   - Use multiple verification methods
   - Don't reset based on email alone

2. **Use Strong Temporary Passwords**
   - Minimum 6 characters (system requirement)
   - Recommend 8+ characters
   - Mix letters and numbers
   - Example: `Temp2024!`

3. **Secure Communication**
   - Don't send passwords via email
   - Use phone call or in-person
   - Use encrypted messaging if remote
   - Never post in public channels

4. **Document the Reset**
   - Note why password was reset
   - Keep record of verification method
   - System automatically logs in audit trail

5. **Follow Up**
   - Confirm user successfully logged in
   - Verify user changed password
   - Check for any suspicious activity

### For Users

1. **Change Password Immediately**
   - Don't use temporary password long-term
   - Change it right after first login
   - Use a strong, unique password

2. **Use Password Manager**
   - Store passwords securely
   - Avoid writing them down
   - Use different passwords for different systems

3. **Enable 2FA** (if available in future)
   - Additional security layer
   - Protects even if password is compromised

---

## 🚨 Common Scenarios

### Scenario 1: User Forgot Password
**Solution:** Admin resets password, provides temporary password

### Scenario 2: Account Locked/Compromised
**Solution:** Admin resets password + reviews audit logs for suspicious activity

### Scenario 3: New Employee Onboarding
**Solution:** Admin creates account with temporary password, user changes on first login

### Scenario 4: Employee Leaving
**Solution:** Admin disables account (don't delete for audit trail)

---

## ⚠️ Restrictions

### Cannot Reset
- ❌ Your own password (use change-password instead)
- ❌ Admin account (protected)
- ❌ Non-existent users (404 error)

### Requirements
- ✅ Must be logged in as admin
- ✅ Password must be at least 6 characters
- ✅ User must exist in system

---

## 🔍 Troubleshooting

### Error: "Unauthorized"
**Cause:** Not logged in as admin

**Solution:** Login with admin credentials

---

### Error: "Cannot reset your own password"
**Cause:** Trying to reset your own password

**Solution:** Use `/auth/change-password` endpoint instead

---

### Error: "User not found"
**Cause:** Username doesn't exist

**Solution:** Check username spelling, verify user exists in system

---

### Error: "Password must be at least 6 characters"
**Cause:** Password too short

**Solution:** Use longer password (recommend 8+ characters)

---

## 📊 Monitoring

### Check Recent Password Resets
```bash
GET /analytics/audit-logs
```

Filter for:
- Action: `PASSWORD_RESET`
- Recent timestamps
- Specific usernames

### Red Flags
- Multiple resets for same user
- Resets at unusual times
- Resets for admin accounts
- Pattern of resets before suspicious activity

---

## 🔄 Alternative: User Self-Service

If you want users to reset passwords themselves, consider implementing:

1. **Email-based reset** (requires SMTP server)
2. **Security questions** (less secure)
3. **SMS verification** (requires SMS service)

Current implementation is admin-only for maximum security and control.

---

## 📞 Support Workflow

### For Help Desk / IT Support

**When user calls:**
1. ✅ Verify caller identity (employee ID, personal info)
2. ✅ Check if account exists
3. ✅ Check if account is disabled
4. ✅ Reset password via admin panel
5. ✅ Provide temporary password securely
6. ✅ Instruct user to change password
7. ✅ Document the interaction
8. ✅ Follow up to confirm success

**Script:**
> "I've reset your password to [temporary password]. Please log in and change it immediately by clicking your profile icon and going to the Password tab. For security, don't share this password with anyone."

---

## 🎓 Training

### For New Admins

1. Practice resetting test account passwords
2. Review audit logs to see what's recorded
3. Understand security implications
4. Learn verification procedures
5. Know when to escalate (suspicious requests)

---

## 📚 Related Documentation

- [User Management Guide](USER_MANAGEMENT_GUIDE.md) - Complete user management
- [Enterprise User Management](ENTERPRISE_USER_MANAGEMENT.md) - Advanced features
- [API Usage Tips](API_USAGE_TIPS.md) - API documentation guide

---

## 🔐 Security Checklist

Before resetting a password:
- [ ] User identity verified
- [ ] Request is legitimate
- [ ] No suspicious activity on account
- [ ] Admin has proper authorization
- [ ] Secure channel for password delivery
- [ ] User instructed to change password
- [ ] Reset documented/logged

---

**Last Updated:** February 24, 2026  
**Version:** 4.0.0 Enterprise Edition  
**Feature:** Admin Password Reset (Option 1 - No Email)
