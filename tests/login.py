""" Common login/logout test rutines
"""


def register(client, username="testuser", email="test@test.co", password='password', confirmation='password'):
    return client.post(
        '/register', data=dict(
            username=username,  email=email, password=password,
            password_confirmation=confirmation),
        follow_redirects=True)


def login(client, user_id="test@test.co", password='password'):
    return client.post(
        '/login', data=dict(user_id=user_id, password=password),
        follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)
