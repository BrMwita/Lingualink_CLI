import click
from sqlalchemy import desc
from .helpers import create_database, get_session
from google.cloud import translate
from .models import User, Glossary, GlossaryTerm, Session, SessionParticipant, Translation


# Don't initialize Google Translate client
translate_client = None

def get_translate_client():
    """Initialize Google Translate client only when needed"""
    global translate_client
    if translate_client is None:
        try:
            from google.cloud import translate
            translate_client = translate.TranslationServiceClient()
        except Exception as e:
            print(f"Google Translate client initialization failed: {e}")
            translate_client = None
    return translate_client

@click.group()
def cli():
    """LinguaLink CLI - Real-time AR Translation for Global Professionals"""
    pass

@cli.command()
def init_db():
    """Initialize the database"""
    engine = create_database()
    click.echo("Database initialized successfully!")

@cli.command()
def seed():
    """Seed the database with sample data"""
    from .seed import seed_database
    seed_database()

@cli.command()
@click.option('--name', prompt='User name', help='Name of the user')
@click.option('--email', prompt='Email', help='Email of the user')
@click.option('--language', prompt='Primary language (e.g., en, fr, es)', 
              help='Primary language code')
def create_user(name, email, language):
    """Create a new user"""
    engine = create_database()
    session = get_session(engine)
    
    user = User(name=name, email=email, primary_language=language)
    session.add(user)
    session.commit()
    
    click.echo(f"User '{name}' created successfully with ID: {user.id}")
    session.close()

def translate_with_google(text, source_lang, target_lang, glossary_terms=None):
    """Translate text using Google Cloud Translation API"""
    try:
        # Set the project ID (replace with your actual project ID)
        project_id = "your-google-cloud-project-id"
        location = "global"
        
        # Create the client
        client = translate.TranslationServiceClient()
        parent = f"projects/{project_id}/locations/{location}"
        
        # Perform the translation
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "source_language_code": source_lang,
                "target_language_code": target_lang,
            }
        )
        
        # Get the translated text
        translated_text = response.translations[0].translated_text
        
        # Apply glossary terms if available
        if glossary_terms:
            for source_term, target_term in glossary_terms.items():
                if source_term.lower() in text.lower():
                    translated_text = translated_text.replace(source_term, target_term)
        
        return translated_text
        
    except Exception as e:
        click.echo(f"Translation error: {str(e)}")
        # Fallback to mock translation
        return mock_translation(text, source_lang, target_lang, glossary_terms)

def mock_translation(text, source_lang, target_lang, glossary_terms=None):
    """Fallback mock translation"""
    mock_translations = {
        ('en', 'fr'): {
            'hello': 'bonjour',
            'the patient needs heart surgery': 'le patient a besoin d\'une chirurgie cardiaque',
            'engine design': 'conception de moteur',
            'technical manual': 'manuel technique',
            'product specification': 'spécification du produit'
        },
        ('en', 'es'): {
            'hello': 'hola',
            'engine design analysis': 'análisis de diseño del motor',
            'technical documentation': 'documentación técnica',
            'manufacturing specs': 'especificaciones de fabricación',
            'whiteboard discussion': 'discusión en pizarra'
        },
        ('en', 'de'): {
            'hello': 'hallo',
            'technical manual': 'technisches Handbuch',
            'product design': 'Produktdesign',
            'engineering drawing': 'Technische Zeichnung'
        }
    }
    
    # Check if we have a mock translation
    translation_key = (source_lang, target_lang)
    lower_text = text.lower()
    
    if translation_key in mock_translations:
        for phrase, translation in mock_translations[translation_key].items():
            if phrase in lower_text:
                return translation
    
    # Fallback translation
    return f"[{target_lang} translation of: {text}]"

@cli.command()
@click.option('--user-id', prompt='User ID', type=int, help='ID of the user')
@click.option('--text', prompt='Text to translate', help='Text to be translated')
@click.option('--source-lang', prompt='Source language', help='Source language code')
@click.option('--target-lang', prompt='Target language', help='Target language code')
@click.option('--glossary-id', default=None, type=int, help='Glossary ID to use for translation')
def translate_text(user_id, text, source_lang, target_lang, glossary_id):
    """Translate text using Google Translate API"""
    engine = create_database()
    session = get_session(engine)
    
    # Get glossary terms if glossary specified
    glossary_terms = {}
    if glossary_id:
        glossary = session.query(Glossary).filter_by(id=glossary_id).first()
        if glossary:
            click.echo(f"Using glossary: {glossary.name}")
            glossary_terms = {term.source_term: term.target_translation 
                             for term in glossary.terms}
    
    # Use Google Translate API
    translated_text = translate_with_google(text, source_lang, target_lang, glossary_terms)
    
    # Save the translation to history
    translation = Translation(
        user_id=user_id,
        source_text=text,
        source_language=source_lang,
        target_language=target_lang,
        translated_text=translated_text,
        glossary_id=glossary_id
    )
    session.add(translation)
    session.commit()
    
    click.echo(f"Translated text: {translated_text}")
    click.echo(f"Translation saved with ID: {translation.id}")
    session.close()

@cli.command()
@click.option('--user-id', prompt='User ID', type=int, help='ID of the user')
def translation_history(user_id):
    """View translation history for a user"""
    engine = create_database()
    session = get_session(engine)
    
    translations = session.query(Translation).filter_by(user_id=user_id).order_by(desc(Translation.created_at)).all()
    
    if not translations:
        click.echo("No translation history found.")
        return
    
    for i, trans in enumerate(translations, 1):
        click.echo(f"{i}. [{trans.created_at}] {trans.source_language} -> {trans.target_language}")
        click.echo(f"   Source: {trans.source_text}")
        click.echo(f"   Translation: {trans.translated_text}")
        if trans.glossary_id:
            glossary = session.query(Glossary).filter_by(id=trans.glossary_id).first()
            click.echo(f"   Glossary: {glossary.name if glossary else 'Unknown'}")
        click.echo()
    
    session.close()

@cli.command()
def list_glossaries():
    """List all available glossaries"""
    engine = create_database()
    session = get_session(engine)
    
    glossaries = session.query(Glossary).all()
    
    if not glossaries:
        click.echo("No glossaries found.")
        return
    
    for glossary in glossaries:
        click.echo(f"ID: {glossary.id}, Name: {glossary.name}")
        click.echo(f"   Industry: {glossary.industry}, Languages: {glossary.source_language}->{glossary.target_language}")
        click.echo(f"   Terms: {len(glossary.terms)}")
        click.echo()
    
    session.close()

@cli.command()
@click.option('--session-name', prompt='Session name', help='Name of the collaborative session')
@click.option('--user-id', prompt='User ID', type=int, help='ID of the user creating the session')
def create_session(session_name, user_id):
    """Create a new collaborative session"""
    engine = create_database()
    session = get_session(engine)
    
    new_session = Session(name=session_name, user_id=user_id)
    session.add(new_session)
    session.flush()
    
    # Add the creator as a participant
    creator = session.query(User).filter_by(id=user_id).first()
    if creator:
        participant = SessionParticipant(
            session_id=new_session.id,
            user_id=user_id,
            language=creator.primary_language
        )
        session.add(participant)
    
    session.commit()
    
    click.echo(f"Session '{session_name}' created successfully with ID: {new_session.id}")
    click.echo("Share this session ID with other participants to join.")
    session.close()

@cli.command()
@click.option('--session-id', prompt='Session ID', type=int, help='ID of the session to join')
@click.option('--user-id', prompt='User ID', type=int, help='ID of the user joining the session')
def join_session(session_id, user_id):
    """Join an existing collaborative session"""
    engine = create_database()
    session = get_session(engine)
    
    # Check if session exists
    existing_session = session.query(Session).filter_by(id=session_id, is_active=1).first()
    if not existing_session:
        click.echo("Session not found or is no longer active.")
        session.close()
        return
    
    # Check if user exists
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        click.echo("User not found.")
        session.close()
        return
    
    # Check if user is already in the session
    existing_participant = session.query(SessionParticipant).filter_by(
        session_id=session_id, user_id=user_id
    ).first()
    
    if existing_participant:
        click.echo("User is already a participant in this session.")
        session.close()
        return
    
    # Add user to session
    participant = SessionParticipant(
        session_id=session_id,
        user_id=user_id,
        language=user.primary_language
    )
    session.add(participant)
    session.commit()
    
    click.echo(f"User '{user.name}' successfully joined session '{existing_session.name}'")
    session.close()

if __name__ == '__main__':
    cli()