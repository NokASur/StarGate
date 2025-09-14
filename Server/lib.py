import os
import hashlib

from datetime import datetime

CONNECTION_TIMEOUT = 80


def generate_password_hash(password):
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)


def connection_timeout_reached(timestamp: datetime) -> bool:
    return (datetime.now() - timestamp).total_seconds() > CONNECTION_TIMEOUT
