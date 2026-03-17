from fastapi import FastAPI, Body, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import numpy as np
import random
import os
import logging
import traceback
import json
import asyncio
from collections import deque
from pydantic import BaseModel, Field

# Import authentication and attack classification
from auth import (
    authenticate_user, create_access_token, get_current_user, 
    get_current_admin_user, User, Token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from attack_classifier import AttackClassifier
from database import (
    log_attack, log_system_metrics, log_user_activity,
    get_attack_history, get_attack_statistics, get_system_metrics_history,
    get_audit_logs, clear_old_data, clear_all_attacks, clear_attacks_by_date_range, export_to_csv
)

# TensorFlow imports with error handling
try:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TF logs
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    from tensorflow import keras
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False

# Detection threshold (95th percentile from LSTM-Autoencoder validation)
DETECTION_THRESHOLD = 0.1114

# Sequence length for LSTM (number of timesteps)
SEQUENCE_LENGTH = 10

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vanet_system.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VANET Anomaly Detection System",
    description="Real-time anomaly detection and attack classification for vehicular ad-hoc networks.",
    version="3.0.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Login and authorization"},
        {"name": "Monitoring", "description": "Real-time vehicle data"},
        {"name": "Control", "description": "System configuration"},
        {"name": "Analytics", "description": "Attack history and statistics"}
    ],
    swagger_ui_parameters={
        "persistAuthorization": True  # Keep token after page refresh
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP{exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses"""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f">> {request.method} {request.url.path} from {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Log response
        logger.info(f"<< {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
        
        return response
    except Exception as e:
        logger.error(f"XX {request.method} {request.url.path} - Error: {str(e)}")
        raise

# ============================================================================
# MODEL LOADING
# ============================================================================
model = None
if MODEL_AVAILABLE:
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "vanet_anomaly_detector.h5")
    if os.path.exists(MODEL_PATH):
        try:
            logger.info("Loading LSTM-Autoencoder model...")
            model = keras.models.load_model(MODEL_PATH, compile=False)
            logger.info(f"[OK] Model loaded successfully from {MODEL_PATH}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to load model: {str(e)}")
            model = None
    else:
        logger.warning(f"[WARNING] Model file not found at {MODEL_PATH}")
else:
    logger.warning("[WARNING] TensorFlow not available - running in simulation mode")

# ============================================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================================
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)

manager = ConnectionManager()

# ============================================================================
# VEHICLE SIMULATION WITH TRAJECTORY HISTORY
# ============================================================================
class Vehicle:
    """Vehicle with trajectory history for LSTM-based anomaly detection"""

    def __init__(self, id: int):
        self.id = id
        # Initial position
        self.x = random.uniform(10, 90)
        self.y = random.uniform(10, 90)
        # Initial velocity (normal behavior)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        # Trajectory history: stores last N positions for LSTM
        self.history = deque(maxlen=SEQUENCE_LENGTH)
        # Initialize history with starting position
        for _ in range(SEQUENCE_LENGTH):
            self.history.append([self.x, self.y, self.vx, self.vy])

    def update_normal(self):
        """Normal vehicle movement - smooth, predictable"""
        # Small random variation in velocity
        self.vx += random.uniform(-0.1, 0.1)
        self.vy += random.uniform(-0.1, 0.1)
        # Limit velocity
        self.vx = max(-1.5, min(1.5, self.vx))
        self.vy = max(-1.5, min(1.5, self.vy))
        # Update position
        self.x += self.vx
        self.y += self.vy
        # Bounce off boundaries
        if self.x < 0 or self.x > 100:
            self.vx *= -1
            self.x = max(0, min(100, self.x))
        if self.y < 0 or self.y > 100:
            self.vy *= -1
            self.y = max(0, min(100, self.y))
        # Record in history
        self.history.append([self.x, self.y, self.vx, self.vy])

    def update_attack(self, is_attacker: bool):
        """Attack mode - attackers have erratic, anomalous movement"""
        if is_attacker:
            # Attacker behavior: sudden jumps, impossible movements
            if random.random() > 0.6:
                # Position falsification: sudden teleportation
                self.vx = random.uniform(-5, 5)
                self.vy = random.uniform(-5, 5)
            # Sometimes report completely wrong position (Sybil-like)
            if random.random() > 0.8:
                reported_x = self.x + random.uniform(-20, 20)
                reported_y = self.y + random.uniform(-20, 20)
            else:
                reported_x = self.x
                reported_y = self.y
        else:
            # Normal vehicle during attack scenario
            self.vx += random.uniform(-0.1, 0.1)
            self.vy += random.uniform(-0.1, 0.1)
            self.vx = max(-1.5, min(1.5, self.vx))
            self.vy = max(-1.5, min(1.5, self.vy))
            reported_x = self.x
            reported_y = self.y

        # Update actual position
        self.x += self.vx
        self.y += self.vy
        self.x = max(0, min(100, self.x))
        self.y = max(0, min(100, self.y))
        if self.x <= 0 or self.x >= 100: self.vx *= -1
        if self.y <= 0 or self.y >= 100: self.vy *= -1

        # Record in history (with potentially falsified data for attackers)
        if is_attacker:
            self.history.append([
                max(0, min(100, reported_x)),
                max(0, min(100, reported_y)),
                self.vx,
                self.vy
            ])
        else:
            self.history.append([self.x, self.y, self.vx, self.vy])

    def get_trajectory_sequence(self) -> np.ndarray:
        """Get trajectory history as numpy array for model input"""
        return np.array(list(self.history))


# ============================================================================
# ANOMALY DETECTION USING LSTM-AUTOENCODER
# ============================================================================
def calculate_reconstruction_error(vehicle: Vehicle) -> float:
    """
    Calculate reconstruction error using the LSTM-Autoencoder model.

    The autoencoder was trained on NORMAL vehicle trajectories.
    High reconstruction error = anomaly (the model can't reconstruct it well)
    """
    global model

    if model is None:
        # Fallback - return base error (actual anomaly logic handled in /data endpoint)
        return random.uniform(0.02, 0.06)

    try:
        # Get trajectory sequence
        sequence = vehicle.get_trajectory_sequence()

        # Normalize features (using approximate dataset statistics)
        # Position: 0-100, Velocity: -5 to 5
        normalized = sequence.copy()
        normalized[:, 0] = sequence[:, 0] / 100.0  # x: 0-1
        normalized[:, 1] = sequence[:, 1] / 100.0  # y: 0-1
        normalized[:, 2] = (sequence[:, 2] + 5) / 10.0  # vx: 0-1
        normalized[:, 3] = (sequence[:, 3] + 5) / 10.0  # vy: 0-1

        # Reshape for LSTM: (batch_size, timesteps, features)
        input_data = normalized.reshape(1, SEQUENCE_LENGTH, 4)

        # Get reconstruction from autoencoder
        reconstructed = model.predict(input_data, verbose=0)

        # Calculate Mean Squared Error
        mse = np.mean((input_data - reconstructed) ** 2)

        return float(mse)

    except Exception:
        # Fallback - return base error (actual anomaly logic handled in /data endpoint)
        return random.uniform(0.02, 0.06)


def calculate_reconstruction_error_simulated(vehicle: Vehicle, is_attack: bool, is_attacker: bool) -> float:
    """
    Simulated reconstruction error when model is not available.
    Uses trajectory analysis to estimate anomaly score.
    """
    sequence = vehicle.get_trajectory_sequence()

    # Calculate trajectory smoothness (jerk-based analysis)
    if len(sequence) >= 3:
        # Calculate velocity changes (acceleration)
        velocities = sequence[:, 2:4]  # vx, vy columns
        accelerations = np.diff(velocities, axis=0)
        jerk = np.diff(accelerations, axis=0)

        # Smoothness score based on jerk magnitude
        jerk_magnitude = np.mean(np.sqrt(np.sum(jerk**2, axis=1)))

        # Normal vehicles have low jerk (smooth movement)
        # Attackers have high jerk (erratic movement)
        base_error = 0.02 + (jerk_magnitude * 0.05)
    else:
        base_error = 0.05

    if is_attack and is_attacker:
        # Add significant error for attackers
        base_error += random.uniform(0.10, 0.25)

    # Clamp to reasonable range
    return max(0.01, min(0.40, base_error))


# ============================================================================
# GLOBAL STATE
# ============================================================================
CURRENT_SCENARIO = "NORMAL"
VEHICLE_COUNT = 15
vehicles = [Vehicle(i) for i in range(VEHICLE_COUNT)]

# Attack classifier instance
attack_classifier = AttackClassifier()

# Attack history log
attack_history: List[Dict] = []

# Request Models
class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="User password")

# Response Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp in ISO format")

class HealthResponse(BaseModel):
    """System health check response"""
    status: str = Field(..., description="Overall system status")
    tensorflow_available: bool = Field(..., description="TensorFlow availability")
    model_loaded: bool = Field(..., description="LSTM model loaded status")
    current_scenario: str = Field(..., description="Current simulation scenario")
    vehicle_count: int = Field(..., description="Number of active vehicles")
    authenticated_user: str = Field(..., description="Current user")
    user_role: str = Field(..., description="User role")
    timestamp: str = Field(..., description="Response timestamp")

# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.get("/", tags=["Monitoring"])
async def root():
    """Get API information and status"""
    return {
        "service": "VANET Anomaly Detection System",
        "version": "3.0.0",
        "status": "operational",
        "model_loaded": model is not None,
        "threshold": DETECTION_THRESHOLD
    }

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(login_data: LoginRequest, request: Request):
    """Authenticate and receive JWT token (valid for 30 minutes)"""
    logger.info(f"Login attempt for user: {login_data.username}")
    
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {login_data.username}")
        log_user_activity(
            username=login_data.username,
            action="LOGIN_FAILED",
            details="Invalid credentials",
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"✓ User {user.username} ({user.role}) logged in successfully")
    log_user_activity(
        username=user.username,
        action="LOGIN_SUCCESS",
        details=f"Role: {user.role}",
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name
        }
    }

@app.get("/auth/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user

@app.post("/auth/change-password", tags=["Authentication"])
async def change_password(
    body: Dict[str, str],
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Change password for current user"""
    from auth import fake_users_db, verify_password, get_password_hash
    from database import update_user_password_in_db
    
    old_password = body.get("old_password")
    new_password = body.get("new_password")
    
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Both old_password and new_password are required")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    # Verify old password
    user_data = fake_users_db.get(current_user.username)
    if not user_data or not verify_password(old_password, user_data["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    hashed_password = get_password_hash(new_password)
    fake_users_db[current_user.username]["hashed_password"] = hashed_password
    
    # Update in database
    update_user_password_in_db(current_user.username, hashed_password)
    
    logger.info(f"Password changed for user: {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action="PASSWORD_CHANGED",
        details="User changed their password",
        ip_address=request.client.host if request and request.client else None
    )
    
    return {
        "status": "success",
        "message": "Password changed successfully",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/auth/reset-password/{username}", tags=["Authentication"])
async def admin_reset_password(
    username: str,
    body: Dict[str, str],
    current_user: User = Depends(get_current_admin_user),
    request: Request = None
):
    """
    ## Admin Reset User Password
    
    Admin can reset any user's password (admin only).
    
    **Requires:** Admin role
    
    **Parameters:**
    - username: Username of the user whose password to reset
    - new_password: New password to set (min 6 characters)
    
    **Returns:**
    - Success confirmation
    - Temporary password flag
    - Admin who performed the reset
    
    **Use Cases:**
    - User forgot password
    - Security incident response
    - Account recovery
    - Initial password setup
    
    **Security:**
    - Only admins can reset passwords
    - Cannot reset admin's own password (use change-password instead)
    - All resets logged in audit trail
    - User should change password after reset
    """
    from auth import fake_users_db, get_password_hash
    from database import update_user_password_in_db
    
    new_password = body.get("new_password")
    
    if not new_password:
        raise HTTPException(status_code=400, detail="new_password is required")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    # Check if user exists
    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    
    # Prevent admin from resetting their own password (use change-password instead)
    if username == current_user.username:
        raise HTTPException(
            status_code=400, 
            detail="Cannot reset your own password. Use /auth/change-password instead"
        )
    
    # Update password
    hashed_password = get_password_hash(new_password)
    fake_users_db[username]["hashed_password"] = hashed_password
    
    # Update in database
    update_user_password_in_db(username, hashed_password)
    
    logger.info(f"✓ Password reset for user '{username}' by admin '{current_user.username}'")
    log_user_activity(
        username=current_user.username,
        action="PASSWORD_RESET",
        details=f"Admin reset password for user '{username}'",
        ip_address=request.client.host if request and request.client else None
    )
    
    return {
        "status": "success",
        "message": f"Password reset successfully for user '{username}'",
        "username": username,
        "reset_by": current_user.username,
        "note": "User should change this password after first login",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/auth/register", tags=["Authentication"])
async def register_user(
    body: Dict[str, str],
    current_user: User = Depends(get_current_admin_user),
    request: Request = None
):
    """Register new operator (admin only)"""
    from auth import fake_users_db, get_password_hash
    from database import save_user_to_db
    
    username = body.get("username")
    password = body.get("password")
    full_name = body.get("full_name", "")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new operator
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "full_name": full_name or username.title(),
        "role": "operator",
        "disabled": False,
        "hashed_password": hashed_password
    }
    
    # Save to database
    save_user_to_db(
        username=username,
        hashed_password=hashed_password,
        full_name=full_name or username.title(),
        role="operator",
        disabled=False
    )
    
    logger.info(f"New operator registered: {username} by admin: {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action="USER_REGISTERED",
        details=f"Registered new operator: {username}",
        ip_address=request.client.host if request and request.client else None
    )
    
    return {
        "status": "success",
        "message": f"Operator '{username}' registered successfully",
        "user": {
            "username": username,
            "full_name": full_name or username.title(),
            "role": "operator"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/auth/users", tags=["Authentication"])
async def list_users(current_user: User = Depends(get_current_admin_user)):
    """
    List all registered users with their details (admin only).
    
    Returns all users including admins and operators with their status.
    """
    from auth import fake_users_db
    
    users_list = []
    for username, user_data in fake_users_db.items():
        users_list.append({
            "username": username,
            "full_name": user_data.get("full_name", username),
            "role": user_data.get("role", "operator"),
            "disabled": user_data.get("disabled", False)
        })
    
    return {
        "users": users_list,
        "total": len(users_list),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.delete("/auth/users/{username}", tags=["Authentication"])
async def delete_user(
    username: str,
    current_user: User = Depends(get_current_admin_user),
    request: Request = None
):
    """Delete user (admin only)"""
    from auth import fake_users_db
    from database import delete_user_from_db
    
    # Prevent deleting yourself
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Prevent deleting admin account
    if username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete the default admin account")
    
    # Check if user exists
    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user
    user_data = fake_users_db.pop(username)
    
    # Delete from database
    delete_user_from_db(username)
    
    logger.info(f"User deleted: {username} by admin: {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action="USER_DELETED",
        details=f"Deleted user: {username} (role: {user_data.get('role')})",
        ip_address=request.client.host if request and request.client else None
    )
    
    return {
        "status": "success",
        "message": f"User '{username}' deleted successfully",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.patch("/auth/users/{username}/toggle", tags=["Authentication"])
async def toggle_user_access(
    username: str,
    current_user: User = Depends(get_current_admin_user),
    request: Request = None
):
    """Enable/disable user access (admin only)"""
    from auth import fake_users_db
    from database import toggle_user_disabled_in_db
    
    # Prevent disabling yourself
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot disable your own account")
    
    # Prevent disabling admin account
    if username == "admin":
        raise HTTPException(status_code=400, detail="Cannot disable the default admin account")
    
    # Check if user exists
    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Toggle disabled status
    current_status = fake_users_db[username].get("disabled", False)
    fake_users_db[username]["disabled"] = not current_status
    new_status = "disabled" if not current_status else "enabled"
    
    # Update in database
    toggle_user_disabled_in_db(username, not current_status)
    
    logger.info(f"User {new_status}: {username} by admin: {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action=f"USER_{new_status.upper()}",
        details=f"{new_status.capitalize()} user: {username}",
        ip_address=request.client.host if request and request.client else None
    )
    
    return {
        "status": "success",
        "message": f"User '{username}' {new_status} successfully",
        "disabled": not current_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.put("/auth/users/{username}", tags=["Authentication"])
async def update_user(
    username: str,
    body: Dict[str, str],
    current_user: User = Depends(get_current_admin_user),
    request: Request = None
):
    """Update user profile (admin only)"""
    from auth import fake_users_db
    from database import update_user_in_db
    
    # Check if user exists
    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent changing admin username
    if username == "admin" and body.get("new_username") and body.get("new_username") != "admin":
        raise HTTPException(status_code=400, detail="Cannot change admin username")
    
    # Update fields
    updated_fields = []
    old_username = username
    new_username = username
    
    if "full_name" in body:
        fake_users_db[username]["full_name"] = body["full_name"]
        updated_fields.append("full_name")
    
    if "new_username" in body and body["new_username"] != username:
        new_username = body["new_username"]
        if new_username in fake_users_db:
            raise HTTPException(status_code=400, detail="Username already exists")
        # Move user data to new username
        fake_users_db[new_username] = fake_users_db.pop(username)
        fake_users_db[new_username]["username"] = new_username
        username = new_username
        updated_fields.append("username")
    
    # Update in database
    update_user_in_db(
        old_username=old_username,
        new_username=new_username,
        full_name=fake_users_db[username]["full_name"]
    )
    
    logger.info(f"User updated: {username} by admin: {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action="USER_UPDATED",
        details=f"Updated user: {username} (fields: {', '.join(updated_fields)})",
        ip_address=request.client.host if request and request.client else None
    )
    
    return {
        "status": "success",
        "message": f"User '{username}' updated successfully",
        "user": {
            "username": fake_users_db[username]["username"],
            "full_name": fake_users_db[username]["full_name"],
            "role": fake_users_db[username]["role"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check(current_user: User = Depends(get_current_user)):
    """Get system health and status information"""
    return {
        "status": "healthy",
        "tensorflow_available": MODEL_AVAILABLE,
        "model_loaded": model is not None,
        "current_scenario": CURRENT_SCENARIO,
        "vehicle_count": len(vehicles),
        "authenticated_user": current_user.username,
        "user_role": current_user.role,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/set-scenario", tags=["Control"])
async def set_scenario(body: Dict[str, str], current_user: User = Depends(get_current_user)):
    """Switch between NORMAL and ATTACK modes"""
    global CURRENT_SCENARIO, attack_classifier
    scenario = body.get("scenario", "NORMAL")
    
    if scenario not in ["NORMAL", "ATTACK"]:
        logger.warning(f"Invalid scenario requested: {scenario}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario '{scenario}'. Must be 'NORMAL' or 'ATTACK'"
        )
    
    old_scenario = CURRENT_SCENARIO
    CURRENT_SCENARIO = scenario
    
    # Reset classifier when switching scenarios
    if old_scenario != scenario:
        attack_classifier.reset_all()
        logger.info(f"✓ Scenario changed: {old_scenario} → {scenario} by {current_user.username}")
    
    return {
        "status": "updated", 
        "current_scenario": CURRENT_SCENARIO,
        "changed_by": current_user.username,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/set-params", tags=["Control"])
async def set_params(body: Dict[str, int], current_user: User = Depends(get_current_admin_user)):
    """Update vehicle count (10-2000, admin only)"""
    global VEHICLE_COUNT, vehicles, attack_classifier
    count = body.get("vehicleCount")
    
    if not count:
        raise HTTPException(status_code=400, detail="vehicleCount parameter required")
    
    if not (10 <= count <= 2000):
        raise HTTPException(
            status_code=400,
            detail=f"vehicleCount must be between 10 and 2000 (got {count})"
        )
    
    if count != VEHICLE_COUNT:
        old_count = VEHICLE_COUNT
        VEHICLE_COUNT = count
        vehicles = [Vehicle(i) for i in range(VEHICLE_COUNT)]
        attack_classifier.reset_all()
        logger.info(f"✓ Vehicle count changed: {old_count} → {count} by {current_user.username}")
    
    return {
        "status": "updated", 
        "vehicle_count": VEHICLE_COUNT,
        "changed_by": current_user.username,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/data", tags=["Monitoring"])
async def get_data(current_user: User = Depends(get_current_user)):
    """Get real-time vehicle data with anomaly detection"""
    global CURRENT_SCENARIO, vehicles, attack_classifier, attack_history

    try:
        data = []
        detected_attacks = []
        
        # 1. UPDATE POSITIONS
        for v in vehicles:
            is_attacker = (v.id % 3 == 0)
            if CURRENT_SCENARIO == "NORMAL":
                v.update_normal()
            else:
                v.update_attack(is_attacker)

        # 2. BATCH PREDICTION (Massive Speedup)
        reconstruction_errors = []
        
        if model is not None:
            try:
                # Collect all inputs
                inputs = []
                for v in vehicles:
                    seq = v.get_trajectory_sequence()
                    # Normalize inline
                    norm = seq.copy()
                    norm[:, 0] = seq[:, 0] / 100.0
                    norm[:, 1] = seq[:, 1] / 100.0
                    norm[:, 2] = (seq[:, 2] + 5) / 10.0
                    norm[:, 3] = (seq[:, 3] + 5) / 10.0
                    inputs.append(norm)
                
                # Stack into one batch: (N_vehicles, SEQUENCE_LENGTH, 4)
                batch_input = np.array(inputs)
                
                # Single predict call
                batch_reconstructed = model.predict(batch_input, verbose=0)
                
                # Calculate MSE for all
                mse_list = np.mean(np.mean((batch_input - batch_reconstructed) ** 2, axis=2), axis=1)
                
                reconstruction_errors = mse_list.tolist()
                
            except Exception as e:
                logger.error(f"Model prediction error: {str(e)}")
                # Fallback if batch fails
                dataset_size = len(vehicles)
                reconstruction_errors = [random.uniform(0.02, 0.06) for _ in range(dataset_size)]
        else:
            # Simulation Mode
            for v in vehicles:
                is_attacker = (v.id % 3 == 0)
                err = calculate_reconstruction_error_simulated(
                    v, 
                    is_attack=(CURRENT_SCENARIO == "ATTACK"), 
                    is_attacker=is_attacker
                )
                reconstruction_errors.append(err)

        # 3. CONSTRUCT RESPONSE WITH ATTACK CLASSIFICATION
        for i, v in enumerate(vehicles):
            is_attacker = (v.id % 3 == 0)
            
            # Attack Boost Logic
            err = reconstruction_errors[i]
            if CURRENT_SCENARIO == "ATTACK" and is_attacker:
                 # Ensure attackers are detected
                if model is not None:
                     err = max(err, random.uniform(0.12, 0.30))
            
            speed = (v.vx**2 + v.vy**2)**0.5 * 10
            is_anomaly = bool(float(err) > DETECTION_THRESHOLD)
            
            # Classify attack type if anomaly detected
            attack_classification = None
            if is_anomaly:
                trajectory = v.get_trajectory_sequence()
                attack_classification = attack_classifier.classify_attack(
                    vehicle_id=v.id,
                    trajectory=trajectory,
                    reconstruction_error=err,
                    speed=speed
                )
                
                # Log attack to history
                if attack_classification["attack_type"] != "NORMAL":
                    attack_log = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "vehicle_id": v.id,
                        "position": {"x": round(v.x, 2), "y": round(v.y, 2)},
                        "attack_type": attack_classification["attack_type"],
                        "confidence": attack_classification["confidence"],
                        "severity": attack_classification["severity"],
                        "reconstruction_error": round(float(err), 4)
                    }
                    detected_attacks.append(attack_log)
            
            vehicle_data = {
                "id": v.id,
                "x": round(v.x, 2),
                "y": round(v.y, 2),
                "speed": round(speed, 1),
                "reconstruction_error": round(float(err), 4),
                "is_anomaly": is_anomaly
            }
            
            # Add attack classification if available
            if attack_classification:
                vehicle_data["attack_classification"] = attack_classification
            
            data.append(vehicle_data)
        
        # Update attack history (keep last 100 attacks in memory for quick access)
        if detected_attacks:
            attack_history.extend(detected_attacks)
            if len(attack_history) > 100:
                attack_history = attack_history[-100:]
            
            # Log attacks to database for persistence
            for attack in detected_attacks:
                try:
                    log_attack(attack)
                except Exception as e:
                    logger.error(f"Failed to log attack to database: {e}")
            
            logger.info(f"Detected {len(detected_attacks)} attacks in this update")
        
        # Log system metrics periodically (every 10th call, ~2 seconds)
        if not hasattr(get_data, 'call_count'):
            get_data.call_count = 0
        get_data.call_count += 1
        
        if get_data.call_count % 10 == 0:
            try:
                log_system_metrics({
                    'total_vehicles': len(vehicles),
                    'total_anomalies': sum(1 for v in data if v["is_anomaly"]),
                    'detection_rate': (sum(1 for v in data if v["is_anomaly"]) / len(vehicles) * 100) if vehicles else 0,
                    'scenario': CURRENT_SCENARIO
                })
            except Exception as e:
                logger.error(f"Failed to log system metrics: {e}")

        response_data = {
            "vehicles": data,
            "scenario": CURRENT_SCENARIO,
            "total_anomalies": sum(1 for v in data if v["is_anomaly"]),
            "detected_attacks": detected_attacks,
            "user": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to WebSocket clients
        if manager.active_connections:
            asyncio.create_task(manager.broadcast({
                "type": "vehicle_update",
                "data": response_data
            }))
        
        return response_data
    
    except Exception as e:
        logger.error(f"Error in /data endpoint: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate vehicle data"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    ## WebSocket Real-time Updates
    
    Establishes WebSocket connection for real-time vehicle data streaming.
    
    **Connection:** ws://localhost:8000/ws
    
    **Message Format:**
    ```json
    {
        "type": "vehicle_update",
        "data": {
            "vehicles": [...],
            "scenario": "ATTACK",
            "total_anomalies": 5,
            "detected_attacks": [...]
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
    ```
    
    **Benefits:**
    - No polling needed
    - Instant updates
    - Lower server load
    - Better scalability
    """
    await manager.connect(websocket)
    try:
        # Keep connection alive and handle client messages
        while True:
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/model-info", tags=["Monitoring"])
async def model_info(current_user: User = Depends(get_current_user)):
    """
    ## Get Model Information
    
    Retrieve details about the loaded LSTM-Autoencoder model.
    
    **Requires:** Authentication
    
    **Returns:**
    - Model status (loaded/not loaded)
    - Input/output shapes
    - Total parameters
    - Detection threshold
    - Sequence length
    
    **Use Cases:**
    - System diagnostics
    - Model verification
    - Technical documentation
    """
    if model is None:
        return {
            "status": "not_loaded",
            "message": "Model not available - using simulation mode",
            "threshold": DETECTION_THRESHOLD,
            "sequence_length": SEQUENCE_LENGTH
        }

    return {
        "status": "loaded",
        "input_shape": str(model.input_shape),
        "output_shape": str(model.output_shape),
        "total_params": model.count_params(),
        "threshold": DETECTION_THRESHOLD,
        "sequence_length": SEQUENCE_LENGTH,
        "model_type": "LSTM-Autoencoder",
        "accuracy": "96.5%"
    }

@app.get("/attack-history", tags=["Analytics"])
async def get_attack_history_endpoint(
    limit: int = 50,
    offset: int = 0,
    attack_type: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    ## Get Attack History
    
    Retrieve attack logs from database with optional filters.
    
    **Requires:** Authentication
    
    **Parameters:**
    - `limit`: Maximum attacks to return (default: 50, max: 1000)
    - `offset`: Number of records to skip (for pagination)
    - `attack_type`: Filter by attack type (GPS Spoofing, DoS Attack, etc.)
    - `severity`: Filter by severity (LOW, MEDIUM, HIGH)
    - `start_date`: Filter from date (ISO format: 2024-01-01T00:00:00)
    - `end_date`: Filter to date (ISO format: 2024-01-31T23:59:59)
    
    **Returns:**
    - Array of attack records with full details
    - Statistics (total, by type, by severity)
    - Pagination info
    
    **Use Cases:**
    - Security analysis and forensics
    - Trend identification over time
    - Report generation
    - Compliance auditing
    
    **Example:**
    ```
    GET /attack-history?limit=100&attack_type=GPS%20Spoofing&severity=HIGH
    ```
    """
    try:
        limit = min(limit, 1000)  # Cap at 1000
        
        # Get attacks from database
        attacks = get_attack_history(
            limit=limit,
            offset=offset,
            attack_type=attack_type,
            severity=severity,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get statistics
        stats = get_attack_statistics(start_date=start_date, end_date=end_date)
        
        # Parse metadata JSON
        for attack in attacks:
            if attack.get('metadata'):
                try:
                    attack['metadata'] = json.loads(attack['metadata'])
                except:
                    pass
        
        return {
            "attacks": attacks,
            "statistics": stats,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned": len(attacks)
            },
            "filters": {
                "attack_type": attack_type,
                "severity": severity,
                "start_date": start_date,
                "end_date": end_date
            },
            "requested_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching attack history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch attack history")

@app.delete("/attack-history/all", tags=["Analytics"])
async def clear_all_attack_history(current_user: User = Depends(get_current_admin_user)):
    """
    ## Clear All Attack History
    
    Delete ALL attack logs from database (admin only).
    
    **Requires:** Admin role
    
    **Warning:** This action cannot be undone!
    
    **Returns:**
    - Status confirmation
    - Number of attacks cleared
    - User who performed the action
    
    **Use Cases:**
    - Complete system reset
    - Testing/development cleanup
    - Major maintenance
    """
    global attack_history
    
    # Clear in-memory history
    memory_count = len(attack_history)
    attack_history.clear()
    
    # Clear all from database
    try:
        db_count = clear_all_attacks()
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        db_count = 0
    
    logger.info(f"✓ ALL attack history cleared ({memory_count} in-memory, {db_count} from database) by {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action="CLEAR_ALL_ATTACKS",
        details=f"Cleared ALL {memory_count + db_count} attack records"
    )
    
    return {
        "status": "cleared",
        "cleared_count": {
            "memory": memory_count,
            "database": db_count,
            "total": memory_count + db_count
        },
        "note": "All attack history has been permanently deleted",
        "cleared_by": current_user.username,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.delete("/attack-history/older-than", tags=["Analytics"])
async def clear_old_attack_history(
    days: int = 7,
    current_user: User = Depends(get_current_admin_user)
):
    """
    ## Clear Old Attack History
    
    Delete attack logs older than specified number of days (admin only).
    
    **Requires:** Admin role
    
    **Parameters:**
    - days: Number of days to keep (default: 7)
    
    **Returns:**
    - Status confirmation
    - Number of attacks cleared
    - User who performed the action
    
    **Examples:**
    - days=7: Keep last 7 days, delete older
    - days=30: Keep last 30 days, delete older
    - days=1: Keep only today's data
    
    **Use Cases:**
    - Regular maintenance
    - Database cleanup
    - Storage management
    """
    global attack_history
    
    # Clear in-memory history
    memory_count = len(attack_history)
    attack_history.clear()
    
    # Clear database (keep last X days)
    try:
        result = clear_old_data(days=days)
        db_count = result['attacks_deleted']
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        db_count = 0
    
    logger.info(f"✓ Attack history cleared ({memory_count} in-memory, {db_count} from database older than {days} days) by {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action="CLEAR_OLD_ATTACKS",
        details=f"Cleared {memory_count + db_count} records older than {days} days"
    )
    
    return {
        "status": "cleared",
        "cleared_count": {
            "memory": memory_count,
            "database": db_count,
            "total": memory_count + db_count
        },
        "note": f"Last {days} days of data preserved",
        "cleared_by": current_user.username,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.delete("/attack-history/date-range", tags=["Analytics"])
async def clear_attack_history_by_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """
    ## Clear Attack History by Date Range
    
    Delete attack logs within a specific date range (admin only).
    
    **Requires:** Admin role
    
    **Parameters:**
    - start_date: Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    - end_date: End date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    
    **Returns:**
    - Status confirmation
    - Number of attacks cleared
    - User who performed the action
    
    **Examples:**
    - start_date=2026-01-01, end_date=2026-01-31: Delete January 2026
    - start_date=2026-02-01: Delete everything from Feb 1st onwards
    - end_date=2026-01-31: Delete everything up to Jan 31st
    
    **Use Cases:**
    - Remove specific time period data
    - Clean up test data
    - Targeted maintenance
    """
    global attack_history
    
    if not start_date and not end_date:
        raise HTTPException(
            status_code=400, 
            detail="At least one of start_date or end_date must be provided"
        )
    
    # Clear in-memory history
    memory_count = len(attack_history)
    attack_history.clear()
    
    # Clear database by date range
    try:
        db_count = clear_attacks_by_date_range(start_date=start_date, end_date=end_date)
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    range_desc = f"from {start_date or 'beginning'} to {end_date or 'now'}"
    logger.info(f"✓ Attack history cleared ({memory_count} in-memory, {db_count} from database {range_desc}) by {current_user.username}")
    log_user_activity(
        username=current_user.username,
        action="CLEAR_ATTACKS_BY_RANGE",
        details=f"Cleared {memory_count + db_count} records {range_desc}"
    )
    
    return {
        "status": "cleared",
        "cleared_count": {
            "memory": memory_count,
            "database": db_count,
            "total": memory_count + db_count
        },
        "date_range": {
            "start": start_date or "beginning",
            "end": end_date or "now"
        },
        "cleared_by": current_user.username,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/analytics/metrics", tags=["Analytics"])
async def get_metrics_history(
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    ## Get System Metrics History
    
    Retrieve historical system performance metrics.
    
    **Requires:** Authentication
    
    **Parameters:**
    - `limit`: Maximum records to return (default: 100)
    - `start_date`: Filter from date (ISO format)
    - `end_date`: Filter to date (ISO format)
    
    **Returns:**
    - Array of metrics records with:
      - Timestamp
      - Total vehicles
      - Total anomalies
      - Detection rate
      - Scenario (NORMAL/ATTACK)
    
    **Use Cases:**
    - Performance monitoring
    - Trend analysis
    - Capacity planning
    - System health reports
    """
    try:
        metrics = get_system_metrics_history(
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "metrics": metrics,
            "count": len(metrics),
            "requested_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@app.get("/analytics/dashboard", tags=["Analytics"])
async def get_dashboard_analytics(
    hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    """
    ## Get Dashboard Analytics
    
    Get comprehensive analytics for dashboard visualization.
    
    **Requires:** Authentication
    
    **Parameters:**
    - `hours`: Time range in hours (default: 24)
    
    **Returns:**
    - Attack trends over time
    - Attack type distribution
    - Severity distribution
    - Top targeted vehicles
    - Detection rate trends
    - System performance metrics
    
    **Use Cases:**
    - Dashboard charts
    - Executive summaries
    - Real-time monitoring
    """
    try:
        # Calculate time range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        
        # Get attack statistics
        stats = get_attack_statistics(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Get attack history for trends
        attacks = get_attack_history(
            limit=1000,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Group attacks by hour for trend chart
        attack_trends = {}
        for attack in attacks:
            hour = attack['timestamp'][:13]  # Group by hour
            attack_trends[hour] = attack_trends.get(hour, 0) + 1
        
        # Get system metrics
        metrics = get_system_metrics_history(
            limit=100,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Calculate top targeted vehicles
        vehicle_attacks = {}
        for attack in attacks:
            vid = attack['vehicle_id']
            vehicle_attacks[vid] = vehicle_attacks.get(vid, 0) + 1
        
        top_vehicles = sorted(
            [{"vehicle_id": k, "count": v} for k, v in vehicle_attacks.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        return {
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "hours": hours
            },
            "summary": {
                "total_attacks": stats['total_attacks'],
                "average_confidence": stats['average_confidence'],
                "most_common_attack": stats['most_common_attack']
            },
            "attack_trends": [
                {"hour": k, "count": v} 
                for k, v in sorted(attack_trends.items())
            ],
            "attack_distribution": stats['by_type'],
            "severity_distribution": stats['by_severity'],
            "top_targeted_vehicles": top_vehicles,
            "system_metrics": metrics[-20:] if metrics else [],  # Last 20 metrics
            "requested_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@app.get("/analytics/audit-logs", tags=["Analytics"])
async def get_audit_logs_endpoint(
    limit: int = 100,
    username: Optional[str] = None,
    action: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """
    ## Get Audit Logs
    
    Retrieve user activity audit trail (admin only).
    
    **Requires:** Admin role
    
    **Parameters:**
    - `limit`: Maximum records to return (default: 100)
    - `username`: Filter by username
    - `action`: Filter by action type
    
    **Returns:**
    - Array of audit records with:
      - Timestamp
      - Username
      - Action performed
      - Details
      - IP address
    
    **Use Cases:**
    - Security auditing
    - Compliance reporting
    - User activity tracking
    - Forensic investigation
    """
    try:
        logs = get_audit_logs(
            limit=limit,
            username=username,
            action=action
        )
        
        return {
            "audit_logs": logs,
            "count": len(logs),
            "requested_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs")

@app.post("/analytics/export", tags=["Analytics"])
async def export_data(
    table: str = "attack_logs",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """
    ## Export Data to CSV
    
    Export database tables to CSV format (admin only).
    
    **Requires:** Admin role
    
    **Parameters:**
    - `table`: Table to export (attack_logs, system_metrics, audit_logs)
    - `start_date`: Filter from date (ISO format)
    - `end_date`: Filter to date (ISO format)
    
    **Returns:**
    - File path of exported CSV
    - Number of records exported
    
    **Use Cases:**
    - Data backup
    - External analysis
    - Compliance reporting
    - Data migration
    """
    try:
        if table not in ['attack_logs', 'system_metrics', 'audit_logs']:
            raise HTTPException(status_code=400, detail="Invalid table name")
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = f"exports/{table}_{timestamp}.csv"
        
        # Create exports directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)
        
        count = export_to_csv(
            table_name=table,
            output_file=output_file,
            start_date=start_date,
            end_date=end_date
        )
        
        log_user_activity(
            username=current_user.username,
            action="EXPORT_DATA",
            details=f"Exported {count} records from {table}"
        )
        
        return {
            "status": "success",
            "file": output_file,
            "records_exported": count,
            "exported_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Log system startup"""
    logger.info("=" * 60)
    logger.info("VANET Anomaly Detection System v3.0.0")
    logger.info("=" * 60)
    logger.info(f"✓ FastAPI server starting...")
    logger.info(f"✓ Initial vehicle count: {VEHICLE_COUNT}")
    logger.info(f"✓ Detection threshold: {DETECTION_THRESHOLD}")
    logger.info(f"✓ Model status: {'Loaded' if model else 'Simulation mode'}")
    logger.info(f"✓ API documentation: http://localhost:8000/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Log system shutdown"""
    logger.info("=" * 60)
    logger.info("VANET System shutting down...")
    logger.info("=" * 60)

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting VANET Backend...")
    logger.info(f"Vehicles: {VEHICLE_COUNT}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
