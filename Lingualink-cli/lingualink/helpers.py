from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def create_database(db_url='sqlite:///lingualink.db'):
    """Create database and tables"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Create a session for database operations"""
    Session = sessionmaker(bind=engine)
    return Session()