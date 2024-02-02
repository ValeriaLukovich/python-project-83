from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    get_flashed_messages
)
import psycopg2
import os
from datetime import date
from dotenv import load_dotenv
from urllib.parse import urlparse
import validators
from psycopg2.extras import NamedTupleCursor


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def first_page():
    messages = get_flashed_messages()
    return render_template('index.html', messages=messages)


@app.get('/urls')
def get_urls():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute('SELECT * FROM urls')
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('show_urls.html', urls=urls)


@app.post('/urls')
def post_url():
    url_new = request.form.get('url')
    if not url_new:
        flash('URL обязателен')
        return redirect(url_for('first_page'))
    elif not validators.url(url_new):
        flash('Некорректный URL')
        return redirect(url_for('first_page'))
    flash('Страница успешно добавлена')
    url_norm = f"{urlparse(url_new).scheme}://{urlparse(url_new).netloc}"
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute('SELECT * FROM urls WHERE name = %s', (url_norm,))
    url = cur.fetchone()
    if url:
        id = url.id
    else:
        post_date = date.today()
        cur.execute("""
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id;
            """,
                    (url_norm, post_date))
        _id = cur.fetchone()
        id = _id.id
    cur.close()
    conn.close()
    return redirect(url_for('get_url', id=id))


@app.get('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages()
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute(
        'SELECT * FROM urls WHERE id = %s',
        (id,))
    url = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('show_url.html', url=url, messages=messages)


if __name__ == '__main__':
    app.run()
