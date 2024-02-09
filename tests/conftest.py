import pytest
from page_analyzer.app import first_page


@pytest.fixture()
def app():
    app = first_page()
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
