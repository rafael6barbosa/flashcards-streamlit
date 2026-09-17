import os
import sqlite3
from datetime import datetime

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None

SQLITE_PATH = os.getenv('SQLITE_PATH', os.path.join('data', 'flashcards.db'))
DATABASE_URL = os.getenv('DATABASE_URL')


def get_backend():
    return 'postgres' if DATABASE_URL else 'sqlite'


def get_connection():
    backend = get_backend()
    if backend == 'postgres':
        if psycopg2 is None:
            raise RuntimeError('psycopg2-binary não está instalado. Rode: pip install psycopg2-binary')
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn

    os.makedirs(os.path.dirname(SQLITE_PATH) or '.', exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def _parse_sql_datetime(value):
    if value is None:
        return datetime.now()

    value = str(value)
    for fmt in (
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%d',
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.now()


def init_db():
    conn = get_connection()
    c = conn.cursor()
    backend = get_backend()

    if backend == 'postgres':
        c.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                id SERIAL PRIMARY KEY,
                collection_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id SERIAL PRIMARY KEY,
                deck_id INTEGER,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                tags TEXT DEFAULT '',
                FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
            )
        ''')
        c.execute("ALTER TABLE cards ADD COLUMN IF NOT EXISTS tags TEXT DEFAULT ''")
        c.execute('''
            CREATE TABLE IF NOT EXISTS card_reviews (
                id SERIAL PRIMARY KEY,
                card_id INTEGER,
                is_correct BOOLEAN NOT NULL,
                review_duration_ms INTEGER NOT NULL,
                reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tratak_sessions (
                id SERIAL PRIMARY KEY,
                duration_seconds INTEGER NOT NULL,
                practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        c.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                tags TEXT DEFAULT '',
                FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
            )
        ''')
        try:
            c.execute("ALTER TABLE cards ADD COLUMN tags TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
        c.execute('''
            CREATE TABLE IF NOT EXISTS card_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                is_correct BOOLEAN NOT NULL,
                review_duration_ms INTEGER NOT NULL,
                reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE
            )
        ''')
        c.execute('PRAGMA foreign_keys = ON;')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tratak_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration_seconds INTEGER NOT NULL,
                practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    conn.commit()
    conn.close()


def _insert_or_update_collection(conn, c, name, description):
    if get_backend() == 'postgres':
        c.execute(
            'INSERT INTO collections (name, description) VALUES (%s, %s)',
            (name, description),
        )
    else:
        c.execute(
            'INSERT INTO collections (name, description) VALUES (?, ?)',
            (name, description),
        )


# --- Collections ---
def get_collections():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, name, description FROM collections')
    result = c.fetchall()
    conn.close()
    return result


def add_collection(name, description):
    conn = get_connection()
    c = conn.cursor()
    try:
        if get_backend() == 'postgres':
            c.execute('INSERT INTO collections (name, description) VALUES (%s, %s)', (name, description))
        else:
            c.execute('INSERT INTO collections (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


# --- Decks ---
def get_decks(collection_id=None):
    conn = get_connection()
    c = conn.cursor()
    if collection_id is not None:
        if get_backend() == 'postgres':
            c.execute('SELECT id, collection_id, name, description FROM decks WHERE collection_id = %s', (collection_id,))
        else:
            c.execute('SELECT id, collection_id, name, description FROM decks WHERE collection_id = ?', (collection_id,))
    else:
        c.execute('SELECT id, collection_id, name, description FROM decks')
    result = c.fetchall()
    conn.close()
    return result


def add_deck(collection_id, name, description):
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute('INSERT INTO decks (collection_id, name, description) VALUES (%s, %s, %s)', (collection_id, name, description))
    else:
        c.execute('INSERT INTO decks (collection_id, name, description) VALUES (?, ?, ?)', (collection_id, name, description))
    conn.commit()
    conn.close()


def delete_collection(collection_id):
    """Deletes a collection and all its decks, cards, and reviews (CASCADE)."""
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute('DELETE FROM collections WHERE id = %s', (collection_id,))
    else:
        c.execute('DELETE FROM collections WHERE id = ?', (collection_id,))
    conn.commit()
    conn.close()


def delete_deck(deck_id):
    """Deletes a deck and all its cards and reviews (CASCADE)."""
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute('DELETE FROM decks WHERE id = %s', (deck_id,))
    else:
        c.execute('DELETE FROM decks WHERE id = ?', (deck_id,))
    conn.commit()
    conn.close()


# --- Cards ---
def get_cards(deck_id):
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute('SELECT id, deck_id, front, back, tags FROM cards WHERE deck_id = %s', (deck_id,))
    else:
        c.execute('SELECT id, deck_id, front, back, tags FROM cards WHERE deck_id = ?', (deck_id,))
    result = c.fetchall()
    conn.close()
    return result


def add_card(deck_id, front, back, tags=''):
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute('INSERT INTO cards (deck_id, front, back, tags) VALUES (%s, %s, %s, %s)', (deck_id, front, back, tags))
    else:
        c.execute('INSERT INTO cards (deck_id, front, back, tags) VALUES (?, ?, ?, ?)', (deck_id, front, back, tags))
    conn.commit()
    conn.close()


def delete_card(card_id):
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute('DELETE FROM cards WHERE id = %s', (card_id,))
    else:
        c.execute('DELETE FROM cards WHERE id = ?', (card_id,))
    conn.commit()
    conn.close()


def bulk_insert_cards(deck_id, cards_list):
    conn = get_connection()
    c = conn.cursor()
    for card in cards_list:
        front = card.get('front', '')
        back = card.get('back', '')
        tags = str(card.get('tags', ''))
        if get_backend() == 'postgres':
            c.execute('INSERT INTO cards (deck_id, front, back, tags) VALUES (%s, %s, %s, %s)', (deck_id, front, back, tags))
        else:
            c.execute('INSERT INTO cards (deck_id, front, back, tags) VALUES (?, ?, ?, ?)', (deck_id, front, back, tags))
    conn.commit()
    conn.close()


# --- Advanced Features: Spaced Repetition ---
def record_review(card_id, is_correct, duration_ms):
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute(
            'INSERT INTO card_reviews (card_id, is_correct, review_duration_ms) VALUES (%s, %s, %s)',
            (card_id, bool(is_correct), duration_ms),
        )
    else:
        c.execute(
            'INSERT INTO card_reviews (card_id, is_correct, review_duration_ms) VALUES (?, ?, ?)',
            (card_id, bool(is_correct), duration_ms),
        )
    conn.commit()
    conn.close()


def get_cards_prioritized(deck_id):
    """
    Returns cards ordered by a calculated priority weight:
    - Cards never seen (no reviews) are prioritized first.
    - Otherwise, weight incorporates days since last review and error rate.
    """
    conn = get_connection()
    c = conn.cursor()

    query = '''
    SELECT
        c.id, c.deck_id, c.front, c.back, c.tags,
        COALESCE(MAX(r.reviewed_at), '1970-01-01') as last_review,
        COUNT(r.id) as total_reviews,
        SUM(CASE WHEN COALESCE(r.is_correct, false) = false THEN 1 ELSE 0 END) as errors
    FROM cards c
    LEFT JOIN card_reviews r ON c.id = r.card_id
    WHERE c.deck_id = %s
    GROUP BY c.id, c.deck_id, c.front, c.back, c.tags
    '''
    if get_backend() == 'sqlite':
        query = '''
        SELECT
            c.id, c.deck_id, c.front, c.back, c.tags,
            COALESCE(MAX(r.reviewed_at), '1970-01-01') as last_review,
            COUNT(r.id) as total_reviews,
            SUM(CASE WHEN COALESCE(r.is_correct, 0) = 0 THEN 1 ELSE 0 END) as errors
        FROM cards c
        LEFT JOIN card_reviews r ON c.id = r.card_id
        WHERE c.deck_id = ?
        GROUP BY c.id, c.deck_id, c.front, c.back, c.tags
        '''
        c.execute(query, (deck_id,))
    else:
        c.execute(query, (deck_id,))

    results = c.fetchall()
    conn.close()

    prioritized = []
    for row in results:
        card_id, d_id, front, back, tags, last_review_str, total_reviews, errors = row

        errors = errors or 0
        total_reviews = total_reviews or 0

        if total_reviews == 0:
            weight = 9999.0
        else:
            last_rev_date = _parse_sql_datetime(last_review_str)
            days_since = (datetime.now() - last_rev_date).days
            errors_rate = errors / total_reviews if total_reviews > 0 else 0
            weight = days_since + (errors_rate * 10)

        prioritized.append({
            'id': card_id,
            'front': front,
            'back': back,
            'tags': tags,
            'weight': weight,
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

    if get_backend() == 'sqlite':
        query = '''
        SELECT
            COUNT(r.id) as total_reviews,
            SUM(CASE WHEN r.is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
            SUM(CASE WHEN r.is_correct = 0 THEN 1 ELSE 0 END) as incorrect_answers,
            AVG(r.review_duration_ms) as avg_duration_ms
        FROM card_reviews r
        JOIN cards c ON r.card_id = c.id
        WHERE c.deck_id = ?
        '''
        c.execute(query, (deck_id,))
    else:
        c.execute(query, (deck_id,))

    global_stats = c.fetchone()

    query_cards = '''
    SELECT
        c.id, c.front, MAX(r.reviewed_at) as last_seen
    FROM cards c
    LEFT JOIN card_reviews r ON c.id = r.card_id
    WHERE c.deck_id = %s
    GROUP BY c.id, c.front
    '''
    if get_backend() == 'sqlite':
        query_cards = '''
        SELECT
            c.id, c.front, MAX(r.reviewed_at) as last_seen
        FROM cards c
        LEFT JOIN card_reviews r ON c.id = r.card_id
        WHERE c.deck_id = ?
        GROUP BY c.id, c.front
        '''
        c.execute(query_cards, (deck_id,))
    else:
        c.execute(query_cards, (deck_id,))
    cards_stats = c.fetchall()

    conn.close()

    return {
        'global': global_stats,
        'cards': cards_stats,
    }


# --- Tratak ---
def save_tratak_session(duration_seconds):
    """Records a completed Tratak session."""
    conn = get_connection()
    c = conn.cursor()
    if get_backend() == 'postgres':
        c.execute('INSERT INTO tratak_sessions (duration_seconds) VALUES (%s)', (duration_seconds,))
    else:
        c.execute('INSERT INTO tratak_sessions (duration_seconds) VALUES (?)', (duration_seconds,))
    conn.commit()
    conn.close()


def get_tratak_history():
    """Returns all Tratak sessions ordered by most recent first."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, duration_seconds, practiced_at FROM tratak_sessions ORDER BY practiced_at DESC')
    result = c.fetchall()
    conn.close()
    return result


if __name__ == '__main__':
    init_db()
