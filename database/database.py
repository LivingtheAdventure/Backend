import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables
load_dotenv()

# Read from .env
# HOST_NAME = os.getenv("HOST_NAME")
# PORT = os.getenv("PORT")
# USERNAME = os.getenv("USERNAME")
# PASSWORD = os.getenv("PASSWORD")
# DATABASE = os.getenv("DATABASE")

# PostgreSQL connection URL
# DATABASE_URL = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{DATABASE}"

# Vercel DataBase 
DATABASE_URL = os.getenv("DATABASE_URL_V")
# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal for DB interaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()