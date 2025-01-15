import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from .model import Base

# Load environment variables from .env
load_dotenv()

# Get the database URL from the environment
database_url = os.getenv('DATABASE_URL')

# Create the engine
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Database initialization function with retry logic
def init_db():
    tries = 10
    for attempt in range(tries):
        try:
            with engine.connect() as connection:
                print("Database connection established!")
                Base.metadata.create_all(bind=engine)
                print("Database initialized!")
                return True
        except OperationalError:
            print(f"Attempt {attempt + 1} failed: Database connection failed. Retrying...")
            time.sleep(3)

    raise Exception("Failed to connect to the database after multiple retries")
