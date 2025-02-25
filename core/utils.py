import re
import bcrypt

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def validate_password(stored_hash: bytes, password: str) -> bool:
    password_bytes = password.encode('utf-8')
    if type(stored_hash) == str:
        stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_hash)

def validate_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_phone(phone: str) -> bool:
    phone_regex = r'^\d{10}$'
    return re.match(phone_regex, phone) is not None
