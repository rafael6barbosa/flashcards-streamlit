import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db


def migrate_sqlite_to_postgres():
    if not db.DATABASE_URL:
        raise ValueError('Defina DATABASE_URL antes de executar a migração.')

    if db.get_backend() != 'postgres':
        raise RuntimeError('A migração só funciona quando DATABASE_URL está configurado e apontando para o Postgres.')

    db.init_db()

    sqlite_file = db.SQLITE_PATH
    if not os.path.exists(sqlite_file):
        raise FileNotFoundError(f'Arquivo SQLite não encontrado: {sqlite_file}')

    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_conn.row_factory = sqlite3.Row
    postgres_conn = db.get_connection()
    cursor = postgres_conn.cursor()

    tables = ['collections', 'decks', 'cards', 'card_reviews', 'tratak_sessions']

    for table in tables:
        try:
            cursor.execute(f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE')
        except Exception:
            cursor.execute(f'DELETE FROM {table}')

        rows = sqlite_conn.execute(f'SELECT * FROM {table}').fetchall()
        if not rows:
            continue

        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_sql = ', '.join(columns)
        insert_sql = f'INSERT INTO {table} ({column_sql}) VALUES ({placeholders})'

        cursor.executemany(insert_sql, [tuple(row[col] for col in columns) for row in rows])

    postgres_conn.commit()
    sqlite_conn.close()
    postgres_conn.close()

    print('Migração concluída com sucesso.')


if __name__ == '__main__':
    migrate_sqlite_to_postgres()
