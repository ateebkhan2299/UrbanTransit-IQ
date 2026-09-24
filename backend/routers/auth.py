import hashlib
import hmac
import json
import base64
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models_db import User, AuditLog
from backend.schemas import UserLogin, Token, UserOut, AuditLogSchema

SECRET_KEY = "urbantransit_iq_super_secret_jwt_key_2026"

router = APIRouter(prefix="/api/auth", tags=["auth"])
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        # Fallback to sha256 temporarily to support seeded demo users who have sha256 hashes
        import hashlib
        return hashlib.sha256(plain_password.encode('utf-8')).hexdigest() == hashed_password


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data_str: str) -> bytes:
    rem = len(data_str) % 4
    if rem > 0:
        data_str += '=' * (4 - rem)
    return base64.urlsafe_b64decode(data_str.encode('utf-8'))

def create_access_token(data: dict, expires_delta_seconds: int = 86400) -> str:
    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = data.copy()
    payload['exp'] = int(time.time()) + expires_delta_seconds

    header_b64 = base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = base64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))

    signing_input = f'{header_b64}.{payload_b64}'.encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = base64url_encode(signature)

    return f'{header_b64}.{payload_b64}.{sig_b64}'

def decode_access_token(token_str: str) -> dict:
    parts = token_str.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid token format')
    header_b64, payload_b64, sig_b64 = parts

    signing_input = f'{header_b64}.{payload_b64}'.encode('utf-8')
    expected_sig = base64url_encode(hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest())

    if not hmac.compare_digest(sig_b64, expected_sig):
        raise ValueError('Invalid signature')

    payload_bytes = base64url_decode(payload_b64)
    payload = json.loads(payload_bytes.decode('utf-8'))

    if 'exp' in payload and time.time() > payload['exp']:
        raise ValueError('Token expired')

    return payload

def log_audit(db: Session, username: str, role: str, action: str, endpoint: str, details: Optional[str] = None):
    audit_entry = AuditLog(
        username=username,
        role=role,
        action=action,
        endpoint=endpoint,
        details=details
    )
    db.add(audit_entry)
    db.commit()

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authentication token")
    
    token = authorization.split(" ")[1]
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User account inactive or not found")
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access forbidden: requires one of roles {allowed_roles}")
        return current_user
    return role_checker

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    log_audit(db, user.username, user.role, "USER_LOGIN", "/api/auth/login", "Successful authentication")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name
        }
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )

@admin_router.get("/audit-trail", response_model=List[AuditLogSchema])
def get_audit_trail(db: Session = Depends(get_db), current_user: User = Depends(require_roles(["Admin", "Evaluator"]))):
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(100).all()
    return [
        AuditLogSchema(
            id=l.id,
            username=l.username,
            role=l.role,
            action=l.action,
            endpoint=l.endpoint,
            details=l.details,
            timestamp=str(l.timestamp)
        )
        for l in logs
    ]
