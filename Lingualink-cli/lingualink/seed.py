from .helpers import create_database, get_session
from .models import User, Glossary, GlossaryTerm, Session, SessionParticipant, Translation

def seed_database():
    """Seed the database with sample data"""
    engine = create_database()
    session = get_session(engine)
    
    # Create users
    users = [
        User(name="Alice Johnson", email="alice@example.com", primary_language="en"),
        User(name="Bob Smith", email="bob@example.com", primary_language="fr"),
        User(name="Carlos Rodriguez", email="carlos@example.com", primary_language="es")
    ]
    session.add_all(users)
    
    # Create glossaries
    medical_glossary = Glossary(
        name="Medical Terms EN-FR", 
        industry="medical", 
        source_language="en", 
        target_language="fr"
    )
    
    engineering_glossary = Glossary(
        name="Engineering Terms EN-ES", 
        industry="engineering", 
        source_language="en", 
        target_language="es"
    )
    
    session.add_all([medical_glossary, engineering_glossary])
    session.flush()
    
    # Create glossary terms
    medical_terms = [
        GlossaryTerm(glossary_id=medical_glossary.id, source_term="heart", target_translation="cœur"),
        GlossaryTerm(glossary_id=medical_glossary.id, source_term="surgery", target_translation="chirurgie"),
        GlossaryTerm(glossary_id=medical_glossary.id, source_term="diagnosis", target_translation="diagnostic")
    ]
    
    engineering_terms = [
        GlossaryTerm(glossary_id=engineering_glossary.id, source_term="engine", target_translation="motor"),
        GlossaryTerm(glossary_id=engineering_glossary.id, source_term="design", target_translation="diseño"),
        GlossaryTerm(glossary_id=engineering_glossary.id, source_term="analysis", target_translation="análisis")
    ]
    
    session.add_all(medical_terms + engineering_terms)
    
    # Create a collaborative session
    collaboration_session = Session(
        name="Quarterly Review Meeting",
        user_id=users[0].id
    )
    session.add(collaboration_session)
    session.flush()
    
    # Add participants to the session
    participants = [
        SessionParticipant(session_id=collaboration_session.id, user_id=users[0].id, language="en"),
        SessionParticipant(session_id=collaboration_session.id, user_id=users[1].id, language="fr"),
        SessionParticipant(session_id=collaboration_session.id, user_id=users[2].id, language="es")
    ]
    session.add_all(participants)
    
    # Create some translation history
    translations = [
        Translation(
            user_id=users[0].id,
            source_text="The patient needs heart surgery",
            source_language="en",
            target_language="fr",
            translated_text="Le patient a besoin d'une chirurgie cardiaque",
            glossary_id=medical_glossary.id
        ),
        Translation(
            user_id=users[0].id,
            source_text="Engine design analysis",
            source_language="en",
            target_language="es",
            translated_text="Análisis de diseño del motor",
            glossary_id=engineering_glossary.id
        )
    ]
    session.add_all(translations)
    
    # Commit all changes
    session.commit()
    print("Database seeded successfully!")
    session.close()

if __name__ == "__main__":
    seed_database()