import psycopg2
from psycopg2.extras import NamedTupleCursor, RealDictCursor
from datetime import date
from bs4 import BeautifulSoup
import requests
from flask import flash


def make_connection(db):
    conn = psycopg2.connect(db)
    return conn


def get_url_by_id(db, id):
    conn = make_connection(db)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute('SELECT * FROM urls WHERE id = %s;', (id,))
    url = cur.fetchone()
    return url


def get_url_by_name(db, url):
    conn = make_connection(db)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute('SELECT * FROM urls WHERE name = %s;', (url,))
    url_new = cur.fetchone()
    cur.close()
    conn.close()
    return url_new


def show_url(db, id):
    conn = make_connection(db)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute(
        'SELECT * FROM url_checks WHERE url_id = %s ORDER by id DESC;', (id,)
    )
    checks = cur.fetchall()
    cur.close()
    conn.close()
    return checks


def show_urls_check(db):
    conn = make_connection(db)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT id, name FROM urls ORDER by id DESC;')
    urls = cur.fetchall()
    for url in urls:
        cur.execute("""
            SELECT url_id, status_code, created_at
            FROM url_checks WHERE url_id = %s ORDER BY created_at;
        """, (url['id'], )
        )
        check = cur.fetchone()
        if check:
            url['created_at'] = check['created_at']
            url['status_code'] = check['status_code']
    cur.close()
    conn.close()
    return urls


def add_url(db, url):
    post_date = date.today()
    conn = make_connection(db)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute(
        'INSERT INTO urls(name, created_at) VALUES(%s, %s) RETURNING id;',
        (url, post_date)
    )
    _id = cur.fetchone()
    id = _id.id
    conn.commit()
    conn.close()
    return id


def html_parser(src):
    soup = BeautifulSoup(src, 'html.parser')
    s_h1 = soup.h1.string if soup.h1 else ''
    s_title = soup.title.string if soup.title else ''
    description = soup.find("meta", attrs={"name": "description"})
    if description:
        description = description['content']
    else:
        description = ''
    return {
        "h1": s_h1,
        "title": s_title,
        "description": description,
    }


def make_check(url, url_id):
    headers = {'user-agent': 'my-app/0.0.1'}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        return
    if response.status_code != 200:
        flash('Произошла ошибка при проверке')
    src = response.text
    parsing_results = html_parser(src)
    parsing_results["url_id"] = url_id
    parsing_results["status_code"] = response.status_code,
    parsing_results["created_at"] = date.today()
    return parsing_results


def add_check(db, check_dict):
    conn = make_connection(db)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute("""
        INSERT INTO url_checks (url_id, status_code,
        h1, title, description, created_at)
        VALUES (%(url_id)s, %(status_code)s, %(h1)s,
        %(title)s, %(description)s, %(created_at)s);
        """,
                check_dict)
    conn.commit()
    conn.close()
