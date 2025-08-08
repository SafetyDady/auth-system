import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get database URL with fallback options
DATABASE_URL = (
    os.getenv("DATABASE_URL") or 
    os.getenv("DATABASE_PUBLIC_URL") or
    os.getenv("DATABASE_PRIVATE_URL")
)

if not DATABASE_URL:
    raise ValueError(
        "No database URL found. Please set DATABASE_URL, DATABASE_PUBLIC_URL, or DATABASE_PRIVATE_URL"
    )

print(f"Connecting to database: {DATABASE_URL[:50]}...")

try:
    # Create engine with connection pooling and error handling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debugging
    )
    
    # Test connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("✅ Database connection successful")
    
except Exception as e:
    print(f"❌ Database connection failed: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()