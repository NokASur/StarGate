import re

from datetime import datetime

CONNECTION_TIMEOUT = 3600


def acceptable_name(name: str) -> bool:
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{1,10}[a-zA-Z0-9]$'
    return bool(re.fullmatch(pattern, name))


def acceptable_password(password: str) -> bool:
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{1,10}[a-zA-Z0-9]$'
    return bool(re.fullmatch(pattern, password))


def connection_timeout_reached(timestamp: datetime) -> bool:
    return (datetime.now() - timestamp).total_seconds() > CONNECTION_TIMEOUT
