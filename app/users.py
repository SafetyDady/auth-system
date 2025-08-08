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
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔍 DEBUG: Starting authentication for user: {username}")
        
        # Step 1: Query user from database
        user = get_user_by_username(db, username)
        logger.info(f"🔍 DEBUG: Database query result - User found: {user is not None}")
        
        if not user:
            logger.warning(f"❌ DEBUG: User {username} not found in database")
            return False
        
        # Step 2: Log user attributes
        user_attrs = [attr for attr in dir(user) if not attr.startswith('_')]
        logger.info(f"🔍 DEBUG: User object attributes: {user_attrs}")
        
        # Step 3: Check password field
        password_field = None
        if hasattr(user, 'password_hash'):
            password_field = user.password_hash
            logger.info(f"🔍 DEBUG: Using password_hash field")
        elif hasattr(user, 'hashed_password'):
            password_field = user.hashed_password
            logger.info(f"🔍 DEBUG: Using hashed_password field")
        else:
            logger.error(f"❌ DEBUG: No password field found for user {username}")
            return False
        
        # Step 4: Log password field info
        logger.info(f"🔍 DEBUG: Password field length: {len(password_field) if password_field else 0}")
        logger.info(f"🔍 DEBUG: Password field starts with: {password_field[:10] if password_field else 'None'}...")
        
        # Step 5: Verify password
        logger.info(f"🔍 DEBUG: Starting password verification")
        password_valid = verify_password(password, password_field)
        logger.info(f"🔍 DEBUG: Password verification result: {password_valid}")
        
        if not password_valid:
            logger.warning(f"❌ DEBUG: Password verification failed for user {username}")
            return False
            
        logger.info(f"✅ DEBUG: Authentication successful for user {username}")
        return user
        
    except Exception as e:
        logger.error(f"🚨 DEBUG: Authentication error for user {username}: {str(e)}")
        logger.error(f"🚨 DEBUG: Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"🚨 DEBUG: Traceback: {traceback.format_exc()}")
        return False

