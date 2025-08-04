import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User
from schemas import UserCreate
from users import create_user, get_user_by_username

def create_initial_users():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Define initial users
        initial_users = [
            {
                "username": "superadmin",
                "email": "superadmin@example.com",
                "password": "superadmin123",
                "role": "superadmin"
            },
            {
                "username": "admin1",
                "email": "admin1@example.com", 
                "password": "admin1123",
                "role": "admin1"
            },
            {
                "username": "admin2",
                "email": "admin2@example.com",
                "password": "admin2123", 
                "role": "admin2"
            }
        ]
        
        for user_data in initial_users:
            # Check if user already exists
            existing_user = get_user_by_username(db, user_data["username"])
            if not existing_user:
                user_create = UserCreate(**user_data)
                user = create_user(db, user_create)
                print(f"Created user: {user.username} with role: {user.role}")
            else:
                print(f"User {user_data['username']} already exists")
                
    except Exception as e:
        print(f"Error creating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_users()
    print("Initial users creation completed!")

