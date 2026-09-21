import os
import psycopg2
import streamlit as st  # <--- Adicione esta linha
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, timezone



# Load environment variables from .env
load_dotenv()


def get_connection():
    # Tenta pegar do st.secrets (Streamlit Cloud), se não achar pega do os.getenv (local)
    db_url = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL"))
    
    if not db_url:
        raise ValueError("DATABASE_URL não foi encontrada nas variáveis de ambiente nem nos Secrets.")
        
    return psycopg2.connect(db_url)


def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Create Collections table
    c.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    
    # Create Decks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id SERIAL PRIMARY KEY,
            collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Create Cards table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            tags TEXT DEFAULT ''
        )
    ''')
    
    # Create Reviews table
    c.execute('''
        CREATE TABLE IF NOT EXISTS card_reviews (
            id SERIAL PRIMARY KEY,
            card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
            is_correct BOOLEAN NOT NULL,
            review_duration_ms INTEGER NOT NULL,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Tratak Sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tratak_sessions (
            id SERIAL PRIMARY KEY,
            duration_seconds INTEGER NOT NULL,
            practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    c.close()
    conn.close()

# --- Collections ---
def get_collections():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, name, description FROM collections')
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def add_collection(name, description):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO collections (name, description) VALUES (%s, %s)', (name, description))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        c.close()
        conn.close()

# --- Decks ---
def get_decks(collection_id=None):
    conn = get_connection()
    c = conn.cursor()
    if collection_id is not None:
        c.execute('SELECT id, collection_id, name, description FROM decks WHERE collection_id = %s', (collection_id,))
    else:
        c.execute('SELECT id, collection_id, name, description FROM decks')
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def add_deck(collection_id, name, description):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO decks (collection_id, name, description) VALUES (%s, %s, %s)', (collection_id, name, description))
    conn.commit()
    c.close()
    conn.close()

def delete_collection(collection_id):
    """Deletes a collection and all its decks, cards, and reviews (CASCADE)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM collections WHERE id = %s', (collection_id,))
    conn.commit()
    c.close()
    conn.close()

def delete_deck(deck_id):
    """Deletes a deck and all its cards and reviews (CASCADE)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM decks WHERE id = %s', (deck_id,))
    conn.commit()
    c.close()
    conn.close()

# --- Cards ---
def get_cards(deck_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, deck_id, front, back, tags FROM cards WHERE deck_id = %s', (deck_id,))
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def add_card(deck_id, front, back, tags=''):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO cards (deck_id, front, back, tags) VALUES (%s, %s, %s, %s)', (deck_id, front, back, tags))
    conn.commit()
    c.close()
    conn.close()

def delete_card(card_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM cards WHERE id = %s', (card_id,))
    conn.commit()
    c.close()
    conn.close()

def bulk_insert_cards(deck_id, cards_list):
    conn = get_connection()
    c = conn.cursor()
    for card in cards_list:
        front = card.get('front', '')
        back = card.get('back', '')
        tags = str(card.get('tags', ''))
        c.execute('INSERT INTO cards (deck_id, front, back, tags) VALUES (%s, %s, %s, %s)', (deck_id, front, back, tags))
    conn.commit()
    c.close()
    conn.close()

# --- Advanced Features: Spaced Repetition ---
def record_review(card_id, is_correct, duration_ms):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO card_reviews (card_id, is_correct, review_duration_ms) VALUES (%s, %s, %s)',
        (card_id, bool(is_correct), duration_ms)
    )
    conn.commit()
    c.close()
    conn.close()

def get_cards_prioritized(deck_id):
    """
    Returns cards ordered by a calculated priority weight.
    """
    conn = get_connection()
    c = conn.cursor()
    
    query = '''
    SELECT 
        c.id, c.deck_id, c.front, c.back, c.tags,
        COALESCE(MAX(r.reviewed_at), '1970-01-01 00:00:00') as last_review,
        COUNT(r.id) as total_reviews,
        SUM(CASE WHEN r.is_correct = FALSE THEN 1 ELSE 0 END) as errors
    FROM cards c
    LEFT JOIN card_reviews r ON c.id = r.card_id
    WHERE c.deck_id = %s
    GROUP BY c.id
    '''
    c.execute(query, (deck_id,))
    results = c.fetchall()
    c.close()
    conn.close()
    

    prioritized = []
    for row in results:
        card_id, d_id, front, back, tags, last_review_val, total_reviews, errors = row
        
        errors = errors or 0
        total_reviews = total_reviews or 0
        
        if total_reviews == 0:
            weight = 9999.0 # Max priority for unseen cards
        else:
            if isinstance(last_review_val, datetime):
                last_rev_date = last_review_val
            else:
                try:
                    last_rev_date = datetime.strptime(str(last_review_val), '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    last_rev_date = datetime.now(timezone.utc)
                
            # Garante que ambas as datas tenham fuso horário para permitir a subtração
            now = datetime.now(timezone.utc)
            if last_rev_date.tzinfo is None:
                last_rev_date = last_rev_date.replace(tzinfo=timezone.utc)

            days_since = (now - last_rev_date).days
            errors_rate = errors / total_reviews if total_reviews > 0 else 0
            
            weight = days_since + (errors_rate * 10)
            
        prioritized.append({
            'id': card_id,
            'front': front,
            'back': back,
            'tags': tags,
            'weight': weight
        })

        
    prioritized.sort(key=lambda x: x['weight'], reverse=True)
    return prioritized

def get_deck_performance(deck_id):
    """
    Returns aggregated stats for a deck.
    """
    conn = get_connection()
    c = conn.cursor()
    
    query = '''
    SELECT 
        COUNT(r.id) as total_reviews,
        SUM(CASE WHEN r.is_correct = TRUE THEN 1 ELSE 0 END) as correct_answers,
        SUM(CASE WHEN r.is_correct = FALSE THEN 1 ELSE 0 END) as incorrect_answers,
        AVG(r.review_duration_ms) as avg_duration_ms
    FROM card_reviews r
    JOIN cards c ON r.card_id = c.id
    WHERE c.deck_id = %s
    '''
    c.execute(query, (deck_id,))
    global_stats = c.fetchone()
    
    query_cards = '''
    SELECT 
        c.id, c.front, c.back, MAX(r.reviewed_at) as last_seen
    FROM cards c
    LEFT JOIN card_reviews r ON c.id = r.card_id
    WHERE c.deck_id = %s
    GROUP BY c.id
    '''
    c.execute(query_cards, (deck_id,))
    cards_stats = c.fetchall()
    
    c.close()
    conn.close()
    
    return {
        'global': global_stats,
        'cards': cards_stats
    }

# --- Tratak ---
def save_tratak_session(duration_seconds):
    """Records a completed Tratak session."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO tratak_sessions (duration_seconds) VALUES (%s)',
        (duration_seconds,)
    )
    conn.commit()
    c.close()
    conn.close()

def get_tratak_history():
    """Returns all Tratak sessions ordered by most recent first."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, duration_seconds, practiced_at FROM tratak_sessions ORDER BY practiced_at DESC')
    result = c.fetchall()
    c.close()
    conn.close()
    return result

if __name__ == '__main__':
    init_db()