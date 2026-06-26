import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session

# Load environment variables from the .env file
load_dotenv()

# Extract database environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_DATABASE = os.getenv("DB_DATABASE")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    if not all([DB_DATABASE, DB_USERNAME, DB_PASSWORD]):
        raise ValueError("Database credentials (DATABASE_URL or DB_DATABASE, DB_USERNAME, DB_PASSWORD) must be set in environment.")

    # Build the connection string for PostgreSQL
    DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

# Create SQLModel engine
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Initialize database tables defined in SQLModel models."""
    # Import models here to make sure they are registered on SQLModel.metadata
    import models
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency generator to yield database sessions."""
    with Session(engine) as session:
        yield session
