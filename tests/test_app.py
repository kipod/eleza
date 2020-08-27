import pytest

from app import create_app
from app.database import db
from .login import login, logout, register

app = create_app(environment='testing')


@pytest.fixture
def client():
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_index_page(client):
    response = register(client, 'sam', 'sam@example.com')
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    logout(client)
    response = login(client, 'sam')
    assert b'Login successful.' in response.data
    response = client.get('/')
    assert response.status_code == 200


def test_registration_page(client):
    response = client.get('/register')
    assert response.status_code == 200


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_registration(client):
    # Valid data should register successfully.
    response = register(client, 'alice', 'alice@example.com')
    assert b'Registration successful. You are logged in.' in response.data
    # Password/Confirmation mismatch should fail.
    response = register(client, 'bob', 'bob@example.org', 'password', 'Password')
    assert b'The given data was invalid.' in response.data
    # Existing username registration should fail.
    response = register(client, 'alice', 'alice01@example.com')
    assert b'The given data was invalid.' in response.data
    # Existing email registration should fail.
    response = register(client, 'alicia', 'alice@example.com')
    assert b'The given data was invalid.' in response.data


def test_login_and_logout(client):
    # Access to logout view before login should fail.
    response = logout(client)
    assert response.status_code == 200
    response = client.get('/demo', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data
    # New user will be automatically logged in.
    register(client, 'sam', 'sam@example.com')
    # Should successfully logout the currently logged in user.
    response = logout(client)
    assert b'You were logged out.' in response.data
    # Incorrect login credentials should fail.
    response = login(client, 'sam@example.com', 'wrongpassword')
    assert b'Wrong user ID or password.' in response.data
    # Correct credentials should login
    response = login(client, 'sam')
    assert b'Login successful.' in response.data
