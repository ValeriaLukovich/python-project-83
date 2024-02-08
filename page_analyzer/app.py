from flask import (
    Flask,
    abort,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    get_flashed_messages
)
import os
from datetime import date
from dotenv import load_dotenv
from urllib.parse import urlparse
import validators
from psycopg2.extras import NamedTupleCursor
from page_analyzer.functions import get_url_by_id
from page_analyzer.functions import get_url_by_name
from page_analyzer.functions import make_connection
from page_analyzer.functions import make_check


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
    conn = make_connection(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute('SELECT * FROM urls ORDER by id DESC')
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
    url_norm = f"{urlparse(url_new).scheme}://{urlparse(url_new).netloc}"
    conn = make_connection(DATABASE_URL)
    url = get_url_by_name(conn, url_norm)
    if url:
        flash('Страница уже существует')
        id = url.id
    else:
        flash('Страница успешно добавлена')
        post_date = date.today()
        cur = conn.cursor(cursor_factory=NamedTupleCursor)
        cur.execute(
            'INSERT INTO urls(name, created_at) VALUES(%s, %s) RETURNING id;',
            (url_norm, post_date))
        _id = cur.fetchone()
        id = _id.id
    conn.commit()
    conn.close()
    return redirect(url_for('get_url', id=id))


@app.get('/urls/<int:id>')
def get_url(id):
    conn = make_connection(DATABASE_URL)
    url = get_url_by_id(conn, id)
    if not url:
        return abort(404)
    messages = get_flashed_messages(with_categories=True)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute(
        'SELECT * FROM url_checks WHERE url_id = %s ORDER by id DESC', (id,)
    )
    checks = cur.fetchall()
    conn.close()
    return render_template(
        'show_url.html',
        url=url,
        messages=messages,
        checks=checks
    )


@app.post('/urls/<id>/checks')
def get_check(id):
    flash('Страница успешно проверена')
    conn = make_connection(DATABASE_URL)
    url = get_url_by_id(conn, id)
    check_dict = make_check(url.name, url.id)
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
    return redirect(url_for('get_url', id=id))


if __name__ == '__main__':
    app.run()
