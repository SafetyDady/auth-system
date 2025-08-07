from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-here")
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user from database
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def require_roles(allowed_roles: List[str]):
    """Dependency to require specific roles"""
    def role_checker(current_user = Depends(get_current_user)):
        # Normalize role (admin1, admin2 -> admin)
        user_role = current_user.role
        if user_role in ['admin1', 'admin2']:
            user_role = 'admin'
            
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {allowed_roles}"
            )
        return current_user
    return role_checker

# Role shortcuts
require_admin_or_superadmin = require_roles(["admin", "superadmin"])
require_superadmin = require_roles(["superadmin"])

