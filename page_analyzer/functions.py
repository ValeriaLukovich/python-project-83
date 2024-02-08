import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import date
from bs4 import BeautifulSoup
import requests
from flask import flash


def make_connection(db):
    try:
        conn = psycopg2.connect(db)
        return conn
    except psycopg2.Error as e:
        message = f'Can\'t connect to the database! Error: {e}'
        raise Exception(message)


def get_url_by_id(conn, id):
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute('SELECT * FROM urls WHERE id = %s', (id,))
    url = cur.fetchone()
    return url


def get_url_by_name(conn, url):
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute('SELECT * FROM urls WHERE name = %s', (url,))
    url_new = cur.fetchone()
    return url_new


def make_check(url, id):
    headers = {'user-agent': 'my-app/0.0.1'}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке')
        return
    r_status = response.status_code
    src = response.text
    soup = BeautifulSoup(src, 'html.parser')
    s_h1 = soup.h1.string if soup.h1 else ''
    s_title = soup.title.string if soup.title else ''
    s_description = soup.find("meta", attrs={"name": "description"})['content']
    last_check = date.today()
    return {
        "url_id": id,
        "status_code": r_status,
        "h1": s_h1,
        "title": s_title,
        "description": s_description,
        "created_at": last_check,
    }
