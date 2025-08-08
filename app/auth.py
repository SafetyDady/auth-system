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

# Get SECRET_KEY with proper error handling and encoding
SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is required. "
        "Please set SECRET_KEY in your environment variables."
    )

# Ensure SECRET_KEY is a proper string
if isinstance(SECRET_KEY, bytes):
    SECRET_KEY = SECRET_KEY.decode('utf-8')

# Validate SECRET_KEY length for security
if len(SECRET_KEY) < 32:
    print(f"Warning: SECRET_KEY length is {len(SECRET_KEY)} characters. Recommended minimum is 32 characters.")

print(f"Auth config - SECRET_KEY length: {len(SECRET_KEY)} characters")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

print(f"Auth config - Algorithm: {ALGORITHM}, Token expire: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
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

