import psycopg2
from psycopg2.extras import NamedTupleCursor, RealDictCursor
from datetime import date
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def cursor_init(cursor_t=NamedTupleCursor):
    def cursor_type(func):
        def wrapper(*args, **kwargs):
            conn = psycopg2.connect(DATABASE_URL)
            with conn:
                with conn.cursor(cursor_factory=cursor_t) as cur:
                    res = func(cur, *args, **kwargs)
            conn.commit()
            conn.close()
            return res
        return wrapper
    return cursor_type


@cursor_init(cursor_t=NamedTupleCursor)
def get_url_by_id(cur, id):
    cur.execute('SELECT * FROM urls WHERE id = %s;', (id,))
    url = cur.fetchone()
    return url


@cursor_init(cursor_t=NamedTupleCursor)
def get_url_by_name(cur, url):
    cur.execute('SELECT * FROM urls WHERE name = %s;', (url,))
    url_new = cur.fetchone()
    return url_new


@cursor_init(cursor_t=NamedTupleCursor)
def show_url(cur, id):
    cur.execute(
        'SELECT * FROM url_checks WHERE url_id = %s ORDER by id DESC;', (id,)
    )
    checks = cur.fetchall()
    return checks


@cursor_init(cursor_t=NamedTupleCursor)
def add_url(cur, url):
    post_date = date.today()
    cur.execute(
        'INSERT INTO urls(name, created_at) VALUES(%s, %s) RETURNING id;',
        (url, post_date)
    )
    _id = cur.fetchone()
    id = _id.id
    return id


@cursor_init(cursor_t=RealDictCursor)
def show_urls_check(cur):
    cur.execute("""
        SELECT DISTINCT urls.id, name , url_checks.created_at,
        url_checks.status_code
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        ORDER BY urls.id DESC;
    """)
    urls = cur.fetchall()
    return urls


@cursor_init(cursor_t=NamedTupleCursor)
def add_check(cur, check_dict):
    cur.execute("""
        INSERT INTO url_checks (url_id, status_code,
        h1, title, description, created_at)
        VALUES (%(url_id)s, %(status_code)s, %(h1)s,
        %(title)s, %(description)s, %(created_at)s);
        """,
                check_dict)
