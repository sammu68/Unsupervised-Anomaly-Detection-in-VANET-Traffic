# User Management Guide

## How to Add Multiple Users/Operators

There are two ways to add new users to the system:

---

## Method 1: Manual Addition (Recommended for Production)

### Step 1: Generate Password Hash

Run the helper script in the backend folder:

```bash
cd backend
python add_users.py
```

This will output password hashes for predefined users.

### Step 2: Add to auth.py

Open `backend/auth.py` and add the new user entries to the `fake_users_db` dictionary:

```python
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "role": "admin",
        "hashed_password": "$2b$12$..."
    },
    "operator": {
        "username": "operator",
        "full_name": "Network Operator",
        "role": "operator",
        "hashed_password": "$2b$12$..."
    },
    # Add your new users here
    "operator2": {
        "username": "operator2",
        "full_name": "Network Operator 2",
        "role": "operator",
        # Password: pass123
        "hashed_password": "$2b$12$..."  # Copy from add_users.py output
    },
    "john": {
        "username": "john",
        "full_name": "John Doe",
        "role": "operator",
        # Password: john123
        "hashed_password": "$2b$12$..."  # Copy from add_users.py output
    }
}
```

### Step 3: Restart Backend

The backend will automatically reload if you're using `--reload` flag:

```bash
python -m uvicorn main:app --reload --port 8000
```

---

## Method 2: Generate Custom Hash (For Single User)

### Option A: Using Python Directly

```bash
cd backend
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"
```

### Option B: Using the Helper Script

```bash
cd backend
python generate_password.py
```

Then follow the prompts to generate a hash for your custom password.

---

## Quick Example: Adding 5 Operators

Here's a ready-to-use example with 5 operators:

```python
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "role": "admin",
        "hashed_password": "$2b$12$cQm7ja5474yuLYliWxC7pOwMfVaDjUl1DQ90aJ9U7uvRveeJi1hlu"
    },
    "operator1": {
        "username": "operator1",
        "full_name": "Operator One",
        "role": "operator",
        # Password: op1pass
        "hashed_password": "$2b$12$..."  # Generate using add_users.py
    },
    "operator2": {
        "username": "operator2",
        "full_name": "Operator Two",
        "role": "operator",
        # Password: op2pass
        "hashed_password": "$2b$12$..."
    },
    "operator3": {
        "username": "operator3",
        "full_name": "Operator Three",
        "role": "operator",
        # Password: op3pass
        "hashed_password": "$2b$12$..."
    },
    "operator4": {
        "username": "operator4",
        "full_name": "Operator Four",
        "role": "operator",
        # Password: op4pass
        "hashed_password": "$2b$12$..."
    },
    "operator5": {
        "username": "operator5",
        "full_name": "Operator Five",
        "role": "operator",
        # Password: op5pass
        "hashed_password": "$2b$12$..."
    }
}
```

---

## User Roles Explained

### Admin Role
- **Full access** to all features
- Can modify system settings
- Can change vehicle count
- Can clear attack history
- Can view all data

### Operator Role
- **Read-only** access
- Can view traffic data
- Can toggle attack mode
- Can view attack history
- **Cannot** modify settings
- **Cannot** clear logs
- **Cannot** change vehicle count

---

## Customizing User Roles

### To Add a New Admin:

```python
"newadmin": {
    "username": "newadmin",
    "full_name": "New Administrator",
    "role": "admin",  # Set role to admin
    "hashed_password": "$2b$12$..."
}
```

### To Add a New Operator:

```python
"newoperator": {
    "username": "newoperator",
    "full_name": "New Operator",
    "role": "operator",  # Set role to operator
    "hashed_password": "$2b$12$..."
}
```

---

## Security Best Practices

### 1. Strong Passwords
Use passwords with:
- At least 8 characters
- Mix of uppercase and lowercase
- Numbers and special characters
- Example: `Op3r@t0r!2024`

### 2. Unique Usernames
- Use descriptive usernames
- Avoid generic names like "user1", "test"
- Consider: department, shift, or role-based names
  - `morning_operator`
  - `night_shift_admin`
  - `security_team_1`

### 3. Regular Password Changes
- Change default passwords immediately
- Rotate passwords every 90 days
- Never share passwords

### 4. Remove Unused Accounts
Delete user entries from `fake_users_db` when no longer needed.

---

## Testing New Users

### 1. Add User to auth.py
```python
"testuser": {
    "username": "testuser",
    "full_name": "Test User",
    "role": "operator",
    "hashed_password": "$2b$12$..."
}
```

### 2. Restart Backend
The server will reload automatically if using `--reload` flag.

### 3. Test Login
- Open http://localhost:5173
- Enter username: `testuser`
- Enter password: (the one you used to generate the hash)
- Verify login works

### 4. Test Permissions
- **Operator**: Try to change vehicle count (should fail)
- **Admin**: Try to change vehicle count (should work)

---

## Troubleshooting

### "Incorrect username or password"
- Verify the username exists in `fake_users_db`
- Check that the password hash was generated correctly
- Ensure the password matches what you used to generate the hash

### "Admin privileges required"
- Check that the user's role is set to "admin" in auth.py
- Restart the backend after making changes

### Backend not reloading
- Stop the backend (Ctrl+C)
- Start it again: `python -m uvicorn main:app --reload --port 8000`

---

## Production Deployment

For production, replace the in-memory `fake_users_db` with a real database:

### 1. Install Database Driver
```bash
pip install sqlalchemy psycopg2-binary
```

### 2. Create User Model
```python
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String)
    hashed_password = Column(String)
```

### 3. Create User Management API
Add endpoints for:
- `POST /users` - Create new user (admin only)
- `GET /users` - List all users (admin only)
- `PUT /users/{username}` - Update user (admin only)
- `DELETE /users/{username}` - Delete user (admin only)

---

## Quick Reference

### Generate Hash for New User
```bash
cd backend
python -c "import bcrypt; print(bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode())"
```

### Add User to auth.py
```python
"username": {
    "username": "username",
    "full_name": "Full Name",
    "role": "operator",  # or "admin"
    "hashed_password": "$2b$12$..."
}
```

### Restart Backend
```bash
# If running with --reload, it restarts automatically
# Otherwise:
Ctrl+C
python -m uvicorn main:app --reload --port 8000
```

---

## Example: Adding 10 Operators

```python
fake_users_db = {
    "admin": {...},  # Keep existing admin
    
    # Morning Shift
    "morning_op1": {"username": "morning_op1", "full_name": "Morning Operator 1", "role": "operator", "hashed_password": "$2b$12$..."},
    "morning_op2": {"username": "morning_op2", "full_name": "Morning Operator 2", "role": "operator", "hashed_password": "$2b$12$..."},
    "morning_op3": {"username": "morning_op3", "full_name": "Morning Operator 3", "role": "operator", "hashed_password": "$2b$12$..."},
    
    # Afternoon Shift
    "afternoon_op1": {"username": "afternoon_op1", "full_name": "Afternoon Operator 1", "role": "operator", "hashed_password": "$2b$12$..."},
    "afternoon_op2": {"username": "afternoon_op2", "full_name": "Afternoon Operator 2", "role": "operator", "hashed_password": "$2b$12$..."},
    
    # Night Shift
    "night_op1": {"username": "night_op1", "full_name": "Night Operator 1", "role": "operator", "hashed_password": "$2b$12$..."},
    "night_op2": {"username": "night_op2", "full_name": "Night Operator 2", "role": "operator", "hashed_password": "$2b$12$..."},
    
    # Supervisors
    "supervisor1": {"username": "supervisor1", "full_name": "Supervisor One", "role": "admin", "hashed_password": "$2b$12$..."},
    "supervisor2": {"username": "supervisor2", "full_name": "Supervisor Two", "role": "admin", "hashed_password": "$2b$12$..."},
}
```

---

**Need Help?** Check the backend logs for authentication errors or contact your system administrator.
