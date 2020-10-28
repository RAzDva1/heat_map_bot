import sqlite3
import datetime


def ensure_connection(func):
    def inner(*args, **kwargs):
        with sqlite3.connect('telegram_bot.db') as conn:
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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            is_mailing  BOOL NOT NULL,
            time_add    DATETIME NOT NULL,
            lang_code   VARCHAR(10)
        )
    ''')
    conn.commit()


@ensure_connection
def add_user(conn, user_id: int, lang_code: str):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_mail WHERE user_id == (?)', (user_id, ))
    num = c.fetchone()
    if not num[0]:
        c.execute('INSERT INTO user_mail (user_id, is_mailing, time_add, lang_code) VALUES (?, ?, ?, ?)',
              (user_id, False,  datetime.datetime.now(), lang_code))
        conn.commit()


@ensure_connection
def change_state_email(conn, user_id: int, is_mailing: bool):
    c = conn.cursor()
    c.execute('UPDATE  user_mail SET is_mailing=(?) WHERE user_id == (?)', (is_mailing, user_id, ))
    conn.commit()


@ensure_connection
def change_state_email(conn, user_id: int, is_mailing: bool):
    c = conn.cursor()
    c.execute('UPDATE  user_mail SET is_mailing=(?) WHERE user_id == (?)', (is_mailing, user_id, ))
    conn.commit()


@ensure_connection
def select_users_for_mail(conn):
    c = conn.cursor()
    c.execute('SELECT user_id FROM user_mail WHERE is_mailing = (?)', (True, ))
    conn.commit()
    return c.fetchall()
