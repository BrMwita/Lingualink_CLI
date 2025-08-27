import os
import sys

# Prevent Google auth from interfering with tests
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lingualink.models import Base, User, Glossary

@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_user_creation(session):
    user = User(name="Test User", email="test@example.com", primary_language="en")
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.name == "Test User"

def test_glossary_creation(session):
    glossary = Glossary(name="Test Glossary", industry="test", 
                       source_language="en", target_language="fr")
    session.add(glossary)
    session.commit()
    
    assert glossary.id is not None
    assert glossary.name == "Test Glossary"