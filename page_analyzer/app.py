from flask import Flask
from flask import render_template
from flask import request
import psycopg2
import os
import datetime
import validators
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)


@app.route('/')
def first_page():
    return render_template('index.html')


@app.route('/urls/<id>')
def show_url():
    url = request.args.get('url')
    date = datetime.date()
    if not validators.url('url'):
        return render_template(
            'notval.html',
            url=url,
        )
    with conn.cursor() as curs:
        curs.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s)",
            (url, date))
    return render_template(
        'show_url.html',
        url=url,
    )


@app.route('/urls')
def show_urls():
    with conn.cursor() as curs:
        curs.execute("SELECT * FROM urls;")
        all_urls = curs.fetchall()
    conn.close()
    return all_urls


if __name__ == '__main__':
    app.run()
