from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get DATABASE_URL with proper error handling
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to DATABASE_PUBLIC_URL if DATABASE_URL is not set
    DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL")
    
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set DATABASE_URL or DATABASE_PUBLIC_URL in your environment variables."
    )

print(f"Connecting to database: {DATABASE_URL[:50]}...")  # Log first 50 chars for debugging

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

