"""SQLite database for device cache"""
from sqlite3 import connect, Row
from pathlib import Path
from typing import List, Optional

from classes.device import Device


class DeviceDatabase:
    """Manages device cache in SQLite"""
    
    def __init__(self, db_path: str = "data/edna.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    name TEXT PRIMARY KEY,
                    host TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    last_backup TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_type ON devices(device_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_seen ON devices(last_backup)
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def upsert_devices(self, devices: List[Device]):
        """Insert or update devices from input sources"""
        with connect(self.db_path) as conn:
            for device in devices:
                conn.execute("""
                    INSERT INTO devices (name, host, device_type, last_backup)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(name) DO UPDATE SET
                        host = excluded.host,
                        device_type = excluded.device_type,
                        last_backup = CURRENT_TIMESTAMP
                """, (
                    device.name,
                    device.host,
                    device.device_type
                ))
            
            conn.commit()
    
    def get_all_devices(self) -> List[Device]:
        """Get all devices from database"""
        with connect(self.db_path) as conn:
            conn.row_factory = Row
            cursor = conn.execute("""
                SELECT name, host, device_type, last_backup
                FROM devices
                ORDER BY name
            """)
            
            return [
                Device(
                    name=row['name'],
                    host=row['host'],
                    device_type=row['device_type'],
                    last_backup=row['last_backup'].replace(' ', 'T') + 'Z' if row['last_backup'] else None
                )
                for row in cursor.fetchall()
            ]
    
    def get_device(self, name: str) -> Optional[Device]:
        """Get single device by name"""
        with connect(self.db_path) as conn:
            conn.row_factory = Row
            cursor = conn.execute("""
                SELECT name, host, device_type, last_backup
                FROM devices
                WHERE name = ?
            """, (name,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Device(
                name=row['name'],
                host=row['host'],
                device_type=row['device_type'],
                last_backup=row['last_backup'].replace(' ', 'T') + 'Z' if row['last_backup'] else None
            )
    
    def remove_stale_devices(self, hours: int = 24):
        """Remove devices not seen in X hours"""
        with connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM devices
                WHERE last_backup < datetime('now', '-{} hours')
            """.format(hours))
            
            conn.commit()    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username"""
        with connect(self.db_path) as conn:
            conn.row_factory = Row
            cursor = conn.execute("""
                SELECT username, password_hash, role
                FROM users
                WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return dict(row)
    
    def create_user(self, username: str, password_hash: str, role: str = "user") -> bool:
        """Create a new user"""
        try:
            with connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                """, (username, password_hash, role))
                conn.commit()
            return True
        except Exception:
            return False
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        with connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 1 FROM users WHERE username = ?
            """, (username,))
            return cursor.fetchone() is not None