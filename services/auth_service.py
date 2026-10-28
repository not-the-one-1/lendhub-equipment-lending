import hashlib
import hmac
import re
import secrets
import sqlite3
from database.repositories import users_repo as users
from services.errors import ValidationError, PermissionDenied

ITERATIONS = 260_000

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), ITERATIONS).hex()
    return f'pbkdf2_sha256${ITERATIONS}${salt}${digest}'

def verify_password(password, encoded):
    try:
        method, iterations, salt, digest = encoded.split('$')
        if method != 'pbkdf2_sha256' or not 100_000 <= int(iterations) <= 2_000_000:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(iterations)).hex()
        return hmac.compare_digest(actual, digest)
    except (ValueError, TypeError, AttributeError):
        return False

def validate_identity(name, email):
    if not name.strip():
        raise ValidationError('Enter a name.')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email.strip()):
        raise ValidationError('Enter a valid email address.')

class AuthService:
    def __init__(self, db):
        self.db, self._user_id = db, None

    def login(self, email, password):
        with self.db.read() as conn:
            user = users.by_email(conn, email.strip())
        if not user or not verify_password(password, user['password_hash']):
            raise ValidationError('Email or password is incorrect.')
        self._user_id = user['id']
        return self.current_user

    @property
    def current_user(self):
        if self._user_id is None:
            return None
        with self.db.read() as conn:
            user = users.get(conn, self._user_id)
        if user:
            user.pop('password_hash', None)
        return user

    def require(self, *roles, conn=None):
        user = users.get(conn, self._user_id) if conn and self._user_id else self.current_user
        if not user or (roles and user['role'] not in roles):
            raise PermissionDenied('Your role does not have permission for this action.')
        return user

    def logout(self):
        self._user_id = None

    def change_password(self, old, new):
        if len(new) < 8:
            raise ValidationError('Use at least 8 characters for the new password.')
        with self.db.transaction() as conn:
            user = self.require(conn=conn)
            if not verify_password(old, user['password_hash']):
                raise ValidationError('The current password is incorrect.')
            users.update(conn, user['id'], password_hash=hash_password(new))

    def create_student(self, code, name, email, password, department='', phone=''):
        self.require('admin')
        validate_identity(name, email)
        if not code.strip() or len(password) < 8:
            raise ValidationError('Enter a student number and a password of at least 8 characters.')
        try:
            with self.db.transaction() as conn:
                return users.create(conn, code=code.strip(), name=name.strip(), email=email.strip().lower(), password_hash=hash_password(password), department=department.strip(), phone=phone.strip())
        except sqlite3.IntegrityError as exc:
            raise ValidationError('This email or student number is already in use.') from exc
