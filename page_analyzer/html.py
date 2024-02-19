from bs4 import BeautifulSoup
import requests
from datetime import date


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
    src = response.text
    parsing_results = html_parser(src)
    parsing_results["url_id"] = url_id
    parsing_results["status_code"] = response.status_code,
    parsing_results["created_at"] = date.today()
    return parsing_results
