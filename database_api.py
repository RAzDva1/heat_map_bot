import psycopg2
import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL', '')
print("DATABASE_URL", DATABASE_URL)


def ensure_connection(func):
    def inner(*args, **kwargs):
        with psycopg2.connect(DATABASE_URL) as conn:
            res = func(conn=conn, *args, **kwargs)
            return res

    return inner


@ensure_connection
def init_db(conn, force: bool = False):
    c = conn.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS user_mail')

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_mail (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            is_mailing  BOOL NOT NULL,
            time_add    TIMESTAMP NOT NULL,
            lang_code   VARCHAR(10),
            first_name  VARCHAR(50)
        )
    ''')
    conn.commit()


@ensure_connection
def add_user(conn, user_id: int, lang_code: str, first_name: str):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_mail WHERE user_id = %s', (user_id,))
    num = c.fetchone()
    if not num[0]:
        c.execute('INSERT INTO user_mail (user_id, is_mailing, time_add, lang_code, first_name) '
                  'VALUES (%s, %s, %s, %s, %s)',
                  (user_id, False, datetime.datetime.now(), lang_code, first_name))
        conn.commit()


@ensure_connection
def change_state_email(conn, user_id: int, is_mailing: bool):
    c = conn.cursor()
    c.execute('UPDATE  user_mail SET is_mailing=%s WHERE user_id = %s', (is_mailing, user_id,))
    conn.commit()


@ensure_connection
def select_users_for_mail(conn):
    c = conn.cursor()
    c.execute('SELECT user_id FROM user_mail WHERE is_mailing = True')
    return c.fetchall()


@ensure_connection
def add_chat_for_init(conn):
    c = conn.cursor()
    c.execute('INSERT INTO user_mail (user_id, is_mailing, time_add, lang_code) VALUES (%s, %s, %s, %s)',
              (-484322978, True, datetime.datetime.now(), "ru"))
    conn.commit()


@ensure_connection
def get_count_all_users(conn):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_mail')
    return c.fetchone()


@ensure_connection
def get_count_active_users(conn):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_mail WHERE is_mailing = TRUE')
    return c.fetchone()


@ensure_connection
def get_count_russian_users(conn):
    c = conn.cursor()
    c.execute(r'SELECT COUNT(*) FROM user_mail WHERE lang_code = %s', ('ru', ))
    return c.fetchone()
