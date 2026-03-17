from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "vanet-secret-key-2024-change-in-prod")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security
security = HTTPBearer()

# Models
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class User(BaseModel):
    username: str
    role: str
    full_name: str

class UserInDB(User):
    hashed_password: str

# Import database functions
from database import load_users_from_db, save_user_to_db

# Load users from database (persistent storage)
fake_users_db = load_users_from_db()

# Default users - only added if database is empty
DEFAULT_USERS = {
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "role": "admin",
        "disabled": False,
        # Password: admin123
        "hashed_password": "$2b$12$cQm7ja5474yuLYliWxC7pOwMfVaDjUl1DQ90aJ9U7uvRveeJi1hlu"
    },
    "operator": {
        "username": "operator",
        "full_name": "Network Operator",
        "role": "operator",
        "disabled": False,
        # Password: operator123
        "hashed_password": "$2b$12$UBN3Qubc2i7u93FAPJ7fkOcrm2h2k4sqhlQW6ep.7BI9/C/4Gq0ay"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# ============================================================================
# INITIAL USER SETUP: These users are ONLY added on first database initialization
# After first run, manage users through the admin panel
# Deleting users from admin panel will keep them deleted (won't re-add on restart)
# ============================================================================
INITIAL_USERS = [
    # Format: (username, password, full_name, role)
    # Role can be "admin" or "operator"
    
    # Example operators (only added if database is empty):
    ("operator2", "pass123", "Network Operator 2", "operator"),
    ("operator3", "pass456", "Network Operator 3", "operator"),
    ("john", "john123", "John Doe", "operator"),
    ("alice", "alice123", "Alice Smith", "operator"),
    ("bob", "bob123", "Bob Johnson", "operator"),
    
    # Example additional admin:
    # ("admin2", "admin456", "Second Administrator", "admin"),
]

# Initialize database with default users ONLY if database is completely empty
if not fake_users_db:
    print("✓ First time setup - Initializing database with default users...")
    
    # Add default admin and operator
    for username, user_data in DEFAULT_USERS.items():
        fake_users_db[username] = user_data
        save_user_to_db(
            username=user_data['username'],
            hashed_password=user_data['hashed_password'],
            full_name=user_data['full_name'],
            role=user_data['role'],
            disabled=user_data.get('disabled', False)
        )
    
    # Add initial users (only on first setup)
    for username, password, full_name, role in INITIAL_USERS:
        hashed_password = get_password_hash(password)
        fake_users_db[username] = {
            "username": username,
            "full_name": full_name,
            "role": role,
            "disabled": False,
            "hashed_password": hashed_password
        }
        save_user_to_db(
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            disabled=False
        )
    
    print(f"✓ Created {len(fake_users_db)} initial users")
else:
    print(f"✓ Loaded {len(fake_users_db)} users from database")

# ============================================================================

def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # Check if account is disabled
    if hasattr(user, 'disabled') and user.disabled:
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return User(username=user.username, role=user.role, full_name=user.full_name)

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
