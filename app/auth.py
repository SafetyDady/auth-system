from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from dotenv import load_dotenv
import os

load_dotenv()

# Get SECRET_KEY with simple handling
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is required. "
        "Please set SECRET_KEY in your environment variables."
    )

# Ensure SECRET_KEY is a proper string (no base64 decoding)
if isinstance(SECRET_KEY, bytes):
    SECRET_KEY = SECRET_KEY.decode('utf-8')

# Remove any quotes if present
SECRET_KEY = SECRET_KEY.strip('"').strip("'")

print(f"Auth config - SECRET_KEY loaded successfully, length: {len(SECRET_KEY)} characters")
print(f"Auth config - SECRET_KEY type: {type(SECRET_KEY)}")
print(f"Auth config - SECRET_KEY first 10 chars: {SECRET_KEY[:10]}...")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

print(f"Auth config - Algorithm: {ALGORITHM}, Token expire: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔍 DEBUG: verify_password called")
        logger.info(f"🔍 DEBUG: plain_password length: {len(plain_password)}")
        logger.info(f"🔍 DEBUG: hashed_password length: {len(hashed_password) if hashed_password else 0}")
        logger.info(f"🔍 DEBUG: hashed_password starts with: {hashed_password[:10] if hashed_password else 'None'}...")
        
        # Check if hashed_password looks like bcrypt hash
        if hashed_password and hashed_password.startswith('$2b$'):
            logger.info(f"🔍 DEBUG: Hash format looks like bcrypt")
        else:
            logger.warning(f"⚠️ DEBUG: Hash format doesn't look like bcrypt: {hashed_password[:20] if hashed_password else 'None'}")
        
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info(f"🔍 DEBUG: pwd_context.verify result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"🚨 DEBUG: Password verification error: {str(e)}")
        logger.error(f"🚨 DEBUG: Exception type: {type(e).__name__}")
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        # Ensure SECRET_KEY is string before encoding
        secret_key = str(SECRET_KEY) if SECRET_KEY else None
        if not secret_key:
            raise ValueError("SECRET_KEY is None or empty")
            
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"JWT token creation error: {str(e)}")
        print(f"SECRET_KEY type: {type(SECRET_KEY)}, length: {len(str(SECRET_KEY)) if SECRET_KEY else 0}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

def verify_token(token: str):
    try:
        # Ensure SECRET_KEY is string before decoding
        secret_key = str(SECRET_KEY) if SECRET_KEY else None
        if not secret_key:
            raise ValueError("SECRET_KEY is None or empty")
            
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError as e:
        print(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    from .models import User
    
    token = credentials.credentials
    username = verify_token(token)
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

