from sqlalchemy.orm import Session
from .models import User
from .auth import verify_password, get_password_hash
from .schemas import UserCreate

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    try:
        user = get_user_by_username(db, username)
        if not user:
            print(f"User {username} not found")
            return False
        
        # Check if user has password_hash attribute (database column)
        if hasattr(user, 'password_hash'):
            password_field = user.password_hash
        elif hasattr(user, 'hashed_password'):
            password_field = user.hashed_password
        else:
            print(f"No password field found for user {username}")
            return False
            
        if not verify_password(password, password_field):
            print(f"Password verification failed for user {username}")
            return False
        return user
    except Exception as e:
        # Log the error but don't expose it
        print(f"Authentication error for user {username}: {str(e)}")
        return False

