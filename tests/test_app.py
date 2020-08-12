import pytest

from app import db, create_app

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


def register(client, username, email, password='password', confirmation='password'):
    return client.post(
        '/register', data=dict(
            username=username,  email=email, password=password,
            password_confirmation=confirmation),
        follow_redirects=True)


def login(client, user_id, password='password'):
    return client.post(
        '/login', data=dict(user_id=user_id, password=password),
        follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_index_page(client):
    register(client, 'sam', 'sam@example.com')
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
