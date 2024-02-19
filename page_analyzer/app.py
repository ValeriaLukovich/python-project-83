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
from page_analyzer.validate import validate_url, normalize_url
from page_analyzer.html import make_check
from page_analyzer.database import (
    get_url_by_id,
    get_url_by_name,
    show_url,
    show_urls_check,
    add_url,
    add_check
)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def first_page():
    messages = get_flashed_messages()
    return render_template('index.html', messages=messages)


@app.get('/urls')
def get_urls():
    messages = get_flashed_messages()
    urls = show_urls_check()
    return render_template(
        'show_urls.html',
        messages=messages,
        urls=urls,
    )


@app.post('/urls')
def post_url():
    url_new = request.form.get('url')
    error_message = validate_url(url_new)
    if error_message:
        flash(error_message)
        return render_template('index.html'), 422
    url_norm = normalize_url(url_new)
    url = get_url_by_name(url_norm)
    if url:
        flash('Страница уже существует')
        id = url.id
    else:
        flash('Страница успешно добавлена')
        id = add_url(url_norm)
    return redirect(url_for('get_url', id=id))


@app.get('/urls/<int:id>')
def get_url(id):
    url = get_url_by_id(id)
    if not url:
        return abort(404)
    messages = get_flashed_messages(with_categories=True)
    checks = show_url(id)
    return render_template(
        'show_url.html',
        url=url,
        messages=messages,
        checks=checks
    )


@app.post('/urls/<int:url_id>/checks')
def get_check(url_id):
    url = get_url_by_id(url_id)
    check_dict = make_check(url.name, url.id)
    if check_dict['status_code'][0] != 200:
        flash('Произошла ошибка при проверке')
    else:
        flash('Страница успешно проверена')
    add_check(check_dict)
    return redirect(url_for('get_url', id=url.id))


if __name__ == '__main__':
    app.run()
