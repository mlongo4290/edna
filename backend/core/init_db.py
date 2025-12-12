"""Initialize admin user if not exists"""
import os
from logging import getLogger
from passlib.context import CryptContext

logger = getLogger(__name__)

# Use SHA256-crypt instead of bcrypt to avoid 72-byte limit
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def init_admin_user(db):
    """Create admin/admin user if not exists"""
    if db.user_exists('admin'):
        logger.info("Admin user already exists")
        return

    password_hash = pwd_context.hash('admin')
    
    if db.create_user('admin', password_hash, 'admin'):
        logger.info("Admin user created successfully")
    else:
        logger.error("Failed to create admin user")
