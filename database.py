"""
Database module for VANET system
Handles persistent storage of attacks, metrics, and audit logs
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = "vanet_data.db"


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                disabled INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Attack logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                vehicle_id INTEGER NOT NULL,
                position_x REAL NOT NULL,
                position_y REAL NOT NULL,
                attack_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                severity TEXT NOT NULL,
                reconstruction_error REAL NOT NULL,
                speed REAL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attack_timestamp 
            ON attack_logs(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attack_type 
            ON attack_logs(attack_type)
        """)
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_vehicles INTEGER NOT NULL,
                total_anomalies INTEGER NOT NULL,
                detection_rate REAL,
                scenario TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User activity audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
            ON audit_logs(timestamp)
        """)
        
        logger.info("✓ Database initialized successfully")


def log_attack(attack_data: Dict) -> int:
    """
    Log an attack to the database
    
    Args:
        attack_data: Dictionary containing attack information
        
    Returns:
        ID of the inserted record
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO attack_logs (
                timestamp, vehicle_id, position_x, position_y,
                attack_type, confidence, severity, reconstruction_error,
                speed, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            attack_data.get('timestamp', datetime.utcnow().isoformat()),
            attack_data['vehicle_id'],
            attack_data['position']['x'],
            attack_data['position']['y'],
            attack_data['attack_type'],
            attack_data['confidence'],
            attack_data['severity'],
            attack_data['reconstruction_error'],
            attack_data.get('speed'),
            json.dumps(attack_data.get('metadata', {}))
        ))
        
        return cursor.lastrowid


def log_system_metrics(metrics_data: Dict) -> int:
    """Log system metrics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO system_metrics (
                timestamp, total_vehicles, total_anomalies,
                detection_rate, scenario
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            metrics_data.get('timestamp', datetime.utcnow().isoformat()),
            metrics_data['total_vehicles'],
            metrics_data['total_anomalies'],
            metrics_data.get('detection_rate', 0.0),
            metrics_data['scenario']
        ))
        
        return cursor.lastrowid


def log_user_activity(username: str, action: str, details: str = None, ip_address: str = None):
    """Log user activity for audit trail"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_logs (
                timestamp, username, action, details, ip_address
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            username,
            action,
            details,
            ip_address
        ))


def get_attack_history(
    limit: int = 100,
    offset: int = 0,
    attack_type: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Get attack history with optional filters
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip (for pagination)
        attack_type: Filter by attack type
        severity: Filter by severity (LOW/MEDIUM/HIGH)
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        
    Returns:
        List of attack records
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM attack_logs WHERE 1=1"
        params = []
        
        if attack_type:
            query += " AND attack_type = ?"
            params.append(attack_type)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]


def get_attack_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict:
    """
    Get attack statistics
    
    Args:
        start_date: Start date for statistics (ISO format)
        end_date: End date for statistics (ISO format)
        
    Returns:
        Dictionary with statistics
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Base query
        where_clause = "WHERE 1=1"
        params = []
        
        if start_date:
            where_clause += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            where_clause += " AND timestamp <= ?"
            params.append(end_date)
        
        # Total attacks
        cursor.execute(f"SELECT COUNT(*) as total FROM attack_logs {where_clause}", params)
        total = cursor.fetchone()['total']
        
        # By attack type
        cursor.execute(f"""
            SELECT attack_type, COUNT(*) as count 
            FROM attack_logs {where_clause}
            GROUP BY attack_type
            ORDER BY count DESC
        """, params)
        by_type = {row['attack_type']: row['count'] for row in cursor.fetchall()}
        
        # By severity
        cursor.execute(f"""
            SELECT severity, COUNT(*) as count 
            FROM attack_logs {where_clause}
            GROUP BY severity
        """, params)
        by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        # Average confidence
        cursor.execute(f"""
            SELECT AVG(confidence) as avg_confidence 
            FROM attack_logs {where_clause}
        """, params)
        avg_confidence = cursor.fetchone()['avg_confidence'] or 0.0
        
        # Most targeted vehicle
        cursor.execute(f"""
            SELECT vehicle_id, COUNT(*) as count 
            FROM attack_logs {where_clause}
            GROUP BY vehicle_id
            ORDER BY count DESC
            LIMIT 1
        """, params)
        most_targeted = cursor.fetchone()
        
        return {
            'total_attacks': total,
            'by_type': by_type,
            'by_severity': by_severity,
            'average_confidence': round(avg_confidence, 2),
            'most_targeted_vehicle': most_targeted['vehicle_id'] if most_targeted else None,
            'most_common_attack': max(by_type, key=by_type.get) if by_type else None
        }


def get_system_metrics_history(
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """Get system metrics history"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM system_metrics WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]


def get_audit_logs(
    limit: int = 100,
    username: Optional[str] = None,
    action: Optional[str] = None
) -> List[Dict]:
    """Get user activity audit logs"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if username:
            query += " AND username = ?"
            params.append(username)
        
        if action:
            query += " AND action = ?"
            params.append(action)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]


def clear_all_attacks():
    """
    Clear ALL attack logs from database
    
    Returns:
        Number of attacks deleted
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Clear all attacks
        cursor.execute("DELETE FROM attack_logs")
        attacks_deleted = cursor.rowcount
        
        logger.info(f"Cleared all {attacks_deleted} attack logs")
        
        return attacks_deleted


def clear_old_data(days: int = 30):
    """
    Clear data older than specified days
    
    Args:
        days: Number of days to keep (default: 30)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        cutoff_str = cutoff_date.isoformat()
        
        # Clear old attacks
        cursor.execute("DELETE FROM attack_logs WHERE timestamp < ?", (cutoff_str,))
        attacks_deleted = cursor.rowcount
        
        # Clear old metrics
        cursor.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_str,))
        metrics_deleted = cursor.rowcount
        
        logger.info(f"Cleared {attacks_deleted} old attack logs and {metrics_deleted} old metrics")
        
        return {
            'attacks_deleted': attacks_deleted,
            'metrics_deleted': metrics_deleted
        }


def clear_attacks_by_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Clear attack logs within a specific date range
    
    Args:
        start_date: Start date (ISO format) - if None, no lower bound
                   If date only (YYYY-MM-DD), starts at 00:00:00
        end_date: End date (ISO format) - if None, no upper bound
                 If date only (YYYY-MM-DD), ends at 23:59:59
        
    Returns:
        Number of attacks deleted
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "DELETE FROM attack_logs WHERE 1=1"
        params = []
        
        if start_date:
            # If date only (YYYY-MM-DD), add time 00:00:00
            if len(start_date) == 10:  # Date only format
                start_date = f"{start_date}T00:00:00"
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            # If date only (YYYY-MM-DD), add time 23:59:59 to include entire day
            if len(end_date) == 10:  # Date only format
                end_date = f"{end_date}T23:59:59"
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        attacks_deleted = cursor.rowcount
        
        logger.info(f"Cleared {attacks_deleted} attack logs (range: {start_date or 'beginning'} to {end_date or 'now'})")
        
        return attacks_deleted


def export_to_csv(table_name: str, output_file: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Export table data to CSV
    
    Args:
        table_name: Name of table to export
        output_file: Output CSV file path
        start_date: Optional start date filter
        end_date: Optional end date filter
    """
    import csv
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = f"SELECT * FROM {table_name} WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if rows:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows([dict(row) for row in rows])
            
            logger.info(f"Exported {len(rows)} rows to {output_file}")
            return len(rows)
        
        return 0


# ============================================================================
# USER PERSISTENCE FUNCTIONS
# ============================================================================

def load_users_from_db() -> Dict:
    """
    Load all users from database into memory dictionary
    
    Returns:
        Dictionary of users {username: {user_data}}
    """
    users = {}
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            
            for row in rows:
                users[row['username']] = {
                    'username': row['username'],
                    'hashed_password': row['hashed_password'],
                    'full_name': row['full_name'],
                    'role': row['role'],
                    'disabled': bool(row['disabled'])
                }
            
            logger.info(f"✓ Loaded {len(users)} users from database")
    except Exception as e:
        logger.error(f"Failed to load users from database: {e}")
    
    return users


def save_user_to_db(username: str, hashed_password: str, full_name: str, role: str, disabled: bool = False):
    """
    Save or update a user in the database
    
    Args:
        username: Username
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        role: User role (admin/operator)
        disabled: Whether account is disabled
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO users (username, hashed_password, full_name, role, disabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, hashed_password, full_name, role, int(disabled), datetime.utcnow().isoformat()))
        
        logger.info(f"✓ Saved user '{username}' to database")


def delete_user_from_db(username: str):
    """
    Delete a user from the database
    
    Args:
        username: Username to delete
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        logger.info(f"✓ Deleted user '{username}' from database")


def update_user_password_in_db(username: str, hashed_password: str):
    """
    Update user's password in database
    
    Args:
        username: Username
        hashed_password: New hashed password
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET hashed_password = ?, updated_at = ?
            WHERE username = ?
        """, (hashed_password, datetime.utcnow().isoformat(), username))
        logger.info(f"✓ Updated password for user '{username}' in database")


def update_user_in_db(old_username: str, new_username: str, full_name: str):
    """
    Update user information in database
    
    Args:
        old_username: Current username
        new_username: New username
        full_name: New full name
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        if old_username == new_username:
            # Just update full name
            cursor.execute("""
                UPDATE users 
                SET full_name = ?, updated_at = ?
                WHERE username = ?
            """, (full_name, datetime.utcnow().isoformat(), old_username))
        else:
            # Update username and full name
            cursor.execute("""
                UPDATE users 
                SET username = ?, full_name = ?, updated_at = ?
                WHERE username = ?
            """, (new_username, full_name, datetime.utcnow().isoformat(), old_username))
        
        logger.info(f"✓ Updated user '{old_username}' in database")


def toggle_user_disabled_in_db(username: str, disabled: bool):
    """
    Toggle user disabled status in database
    
    Args:
        username: Username
        disabled: New disabled status
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET disabled = ?, updated_at = ?
            WHERE username = ?
        """, (int(disabled), datetime.utcnow().isoformat(), username))
        logger.info(f"✓ Updated disabled status for user '{username}' in database")


# Initialize database on module import
try:
    init_database()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

