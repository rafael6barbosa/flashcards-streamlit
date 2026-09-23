from datetime import datetime, timezone
import json
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

# Load environment variables from .env
load_dotenv()


def get_connection():
    """Busca a URL de conexão do st.secrets ou os.getenv com suporte seguro a ambos."""
    db_url = None

    # Tenta ler do st.secrets de forma segura sem quebrar fora do contexto do Streamlit
    try:
        if "DATABASE_URL" in st.secrets:
            db_url = st.secrets["DATABASE_URL"]
    except Exception:
        pass

    # Fallback para .env local
    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError(
            "DATABASE_URL não foi encontrada nas variáveis de ambiente nem nos Secrets."
        )

    return psycopg2.connect(db_url)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Create Collections table
    c.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)

    # Create Decks table
    c.execute("""
        CREATE TABLE IF NOT EXISTS decks (
            id SERIAL PRIMARY KEY,
            collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            description TEXT
        )
    """)

    # Create Cards table
    c.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            tags TEXT DEFAULT ''
        )
    """)

    # Create Multiple-choice questions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
            pergunta TEXT NOT NULL,
            opcoes JSONB NOT NULL,
            resposta TEXT NOT NULL
        )
    """)

    # Create Reviews table
    c.execute("""
        CREATE TABLE IF NOT EXISTS card_reviews (
            id SERIAL PRIMARY KEY,
            card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
            is_correct BOOLEAN NOT NULL,
            review_duration_ms INTEGER NOT NULL,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Tratak Sessions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS tratak_sessions (
            id SERIAL PRIMARY KEY,
            duration_seconds INTEGER NOT NULL,
            practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    c.close()
    conn.close()


# --- Collections ---
def get_collections():
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("SELECT id, name, description FROM collections")
            return c.fetchall()


def add_collection(name, description):
    try:
        with get_connection() as conn:
            with conn.cursor() as c:
                c.execute(
                    "INSERT INTO collections (name, description) VALUES (%s, %s)",
                    (name, description),
                )
                conn.commit()
                return True
    except psycopg2.IntegrityError:
        return False


# --- Decks ---
def get_decks(collection_id=None):
    with get_connection() as conn:
        with conn.cursor() as c:
            if collection_id is not None:
                c.execute(
                    "SELECT id, collection_id, name, description FROM decks WHERE collection_id = %s",
                    (collection_id,),
                )
            else:
                c.execute(
                    "SELECT id, collection_id, name, description FROM decks"
                )
            return c.fetchall()


def add_deck(collection_id, name, description):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO decks (collection_id, name, description) VALUES (%s, %s, %s)",
                (collection_id, name, description),
            )
            conn.commit()


def delete_collection(collection_id):
    """Deletes a collection and all its decks, cards, and reviews (CASCADE)."""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "DELETE FROM collections WHERE id = %s", (collection_id,)
            )
            conn.commit()


def delete_deck(deck_id):
    """Deletes a deck and all its cards and reviews (CASCADE)."""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("DELETE FROM decks WHERE id = %s", (deck_id,))
            conn.commit()


# --- Cards ---
def get_cards(deck_id):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "SELECT id, deck_id, front, back, tags FROM cards WHERE deck_id = %s",
                (deck_id,),
            )
            return c.fetchall()


def add_card(deck_id, front, back, tags=""):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO cards (deck_id, front, back, tags) VALUES (%s, %s, %s, %s)",
                (deck_id, front, back, tags),
            )
            conn.commit()


def delete_card(card_id):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("DELETE FROM cards WHERE id = %s", (card_id,))
            conn.commit()


def bulk_insert_cards(deck_id, cards_list):
    with get_connection() as conn:
        with conn.cursor() as c:
            for card in cards_list:
                front = card.get("front", "")
                back = card.get("back", "")
                tags = str(card.get("tags", ""))
                c.execute(
                    "INSERT INTO cards (deck_id, front, back, tags) VALUES (%s, %s, %s, %s)",
                    (deck_id, front, back, tags),
                )
            conn.commit()


# --- Multiple-choice questions ---
def get_questions(deck_id):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "SELECT id, deck_id, pergunta, opcoes, resposta FROM questions WHERE deck_id = %s ORDER BY id",
                (deck_id,),
            )
            return c.fetchall()


def add_question(deck_id, pergunta, opcoes, resposta):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO questions (deck_id, pergunta, opcoes, resposta) VALUES (%s, %s, %s, %s)",
                (deck_id, pergunta, json.dumps(opcoes), resposta),
            )
            conn.commit()


def bulk_insert_questions(deck_id, questions_list):
    with get_connection() as conn:
        with conn.cursor() as c:
            for question in questions_list:
                c.execute(
                    "INSERT INTO questions (deck_id, pergunta, opcoes, resposta) VALUES (%s, %s, %s, %s)",
                    (
                        deck_id,
                        question["pergunta"],
                        json.dumps(question["opcoes"]),
                        question["resposta"],
                    ),
                )
            conn.commit()


def delete_question(question_id):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("DELETE FROM questions WHERE id = %s", (question_id,))
            conn.commit()


# --- Advanced Features: Spaced Repetition ---
def record_review(card_id, is_correct, duration_ms):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO card_reviews (card_id, is_correct, review_duration_ms) VALUES (%s, %s, %s)",
                (card_id, bool(is_correct), duration_ms),
            )
            conn.commit()


def get_cards_prioritized(deck_id):
    """Returns cards ordered by a calculated priority weight."""
    with get_connection() as conn:
        with conn.cursor() as c:
            query = """
            SELECT 
                c.id, c.deck_id, c.front, c.back, c.tags,
                COALESCE(MAX(r.reviewed_at), '1970-01-01 00:00:00') as last_review,
                COUNT(r.id) as total_reviews,
                SUM(CASE WHEN r.is_correct = FALSE THEN 1 ELSE 0 END) as errors
            FROM cards c
            LEFT JOIN card_reviews r ON c.id = r.card_id
            WHERE c.deck_id = %s
            GROUP BY c.id
            """
            c.execute(query, (deck_id,))
            results = c.fetchall()

    prioritized = []
    now = datetime.now(timezone.utc)

    for row in results:
        (
            card_id,
            d_id,
            front,
            back,
            tags,
            last_review_val,
            total_reviews,
            errors,
        ) = row

        errors = errors or 0
        total_reviews = total_reviews or 0

        if total_reviews == 0:
            weight = 9999.0  # Max priority for unseen cards
        else:
            if isinstance(last_review_val, datetime):
                last_rev_date = last_review_val
            else:
                try:
                    last_rev_date = datetime.strptime(
                        str(last_review_val), "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    last_rev_date = now

            if last_rev_date.tzinfo is None:
                last_rev_date = last_rev_date.replace(tzinfo=timezone.utc)

            days_since = (now - last_rev_date).days
            errors_rate = errors / total_reviews if total_reviews > 0 else 0

            weight = days_since + (errors_rate * 10)

        prioritized.append({
            "id": card_id,
            "front": front,
            "back": back,
            "tags": tags,
            "weight": weight,
        })

    prioritized.sort(key=lambda x: x["weight"], reverse=True)
    return prioritized


def get_deck_performance(deck_id):
    """Returns aggregated stats for a deck."""
    with get_connection() as conn:
        with conn.cursor() as c:
            query_global = """
            SELECT 
                COUNT(r.id) as total_reviews,
                SUM(CASE WHEN r.is_correct = TRUE THEN 1 ELSE 0 END) as correct_answers,
                SUM(CASE WHEN r.is_correct = FALSE THEN 1 ELSE 0 END) as incorrect_answers,
                AVG(r.review_duration_ms) as avg_duration_ms
            FROM card_reviews r
            JOIN cards c ON r.card_id = c.id
            WHERE c.deck_id = %s
            """
            c.execute(query_global, (deck_id,))
            global_stats = c.fetchone()

            query_cards = """
            SELECT 
                c.id, c.front, c.back, MAX(r.reviewed_at) as last_seen
            FROM cards c
            LEFT JOIN card_reviews r ON c.id = r.card_id
            WHERE c.deck_id = %s
            GROUP BY c.id
            """
            c.execute(query_cards, (deck_id,))
            cards_stats = c.fetchall()

    return {"global": global_stats, "cards": cards_stats}


# --- Tratak ---
def save_tratak_session(duration_seconds):
    """Records a completed Tratak session."""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO tratak_sessions (duration_seconds) VALUES (%s)",
                (duration_seconds,),
            )
            conn.commit()


def get_tratak_history():
    """Returns all Tratak sessions ordered by most recent first."""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "SELECT id, duration_seconds, practiced_at FROM tratak_sessions ORDER BY practiced_at DESC"
            )
            return c.fetchall()


if __name__ == "__main__":
    init_db()