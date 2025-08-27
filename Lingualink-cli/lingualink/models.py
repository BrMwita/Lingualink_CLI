from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Association table for many-to-many relationship between users and glossaries
user_glossary = Table(
    'user_glossary',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('glossary_id', Integer, ForeignKey('glossaries.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    primary_language = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="user")
    glossaries = relationship("Glossary", secondary=user_glossary, back_populates="users")
    translations = relationship("Translation", back_populates="user")
    
    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"

class Glossary(Base):
    __tablename__ = 'glossaries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    industry = Column(String(50))
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_glossary, back_populates="glossaries")
    terms = relationship("GlossaryTerm", back_populates="glossary")
    
    def __repr__(self):
        return f"<Glossary(name='{self.name}', industry='{self.industry}')>"

class GlossaryTerm(Base):
    __tablename__ = 'glossary_terms'
    
    id = Column(Integer, primary_key=True)
    glossary_id = Column(Integer, ForeignKey('glossaries.id'), nullable=False)
    source_term = Column(String(200), nullable=False)
    target_translation = Column(String(200), nullable=False)
    
    # Relationships
    glossary = relationship("Glossary", back_populates="terms")
    
    def __repr__(self):
        return f"<GlossaryTerm(source='{self.source_term}', target='{self.target_translation}')>"

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Integer, default=1)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    participants = relationship("SessionParticipant", back_populates="session")
    
    def __repr__(self):
        return f"<Session(name='{self.name}', user_id={self.user_id})>"

class SessionParticipant(Base):
    __tablename__ = 'session_participants'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    language = Column(String(10), nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="participants")
    user = relationship("User")
    
    def __repr__(self):
        return f"<SessionParticipant(session_id={self.session_id}, user_id={self.user_id})>"

class Translation(Base):
    __tablename__ = 'translations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    source_text = Column(Text, nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    glossary_id = Column(Integer, ForeignKey('glossaries.id'))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="translations")
    glossary = relationship("Glossary")
    
    def __repr__(self):
        return f"<Translation(source='{self.source_text[:20]}...', target='{self.translated_text[:20]}...')>"