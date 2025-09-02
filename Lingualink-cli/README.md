# LinguaLink CLI

A command-line interface application that simulates the backend of a real-time AR translation system for global professionals.

## Features

- User management with language preferences
- Industry-specific translation glossaries
- Collaborative session management
- Translation history tracking
- SQLAlchemy ORM with 6 related tables

## Installation

1. Clone the repository
2. Install dependencies: `pipenv install`
3. Activate virtual environment: `pipenv shell`
4. Initialize database: `python -m lingualink.cli init-db`
5. Seed with sample data: `python -m lingualink.cli seed`

## Usage

Run the CLI application: `python -m lingualink.cli [command]`

Available commands:
- `create-user`: Create a new user
- `translate-text`: Simulate text translation
- `translation-history`: View user's translation history
- `list-glossaries`: List available glossaries
- `create-session`: Create a collaborative session
- `join-session`: Join an existing session

## Testing

Run tests: `python -m pytest tests/`

## Video Demonstration

Watch the full demo of LinguaLink CLI Manager:

[![LinguaLink CLI Demo](https://www.loom.com/share/e811c9ec027d45e1baeecd9a517e3a96?sid=7af64d25-3e06-4bd5-bea3-a31df6c2485c)

**Click the image above to watch the full video demonstration**