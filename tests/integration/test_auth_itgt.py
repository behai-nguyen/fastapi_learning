# 
# 15/05/2024.
# 
# Test authentication related routes.
#
# Reference: https://stackoverflow.com/a/71428106
# 
# venv\Scripts\pytest.exe -m auth_integration
# venv\Scripts\pytest.exe -k _integration_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m auth_integration --capture=no
# 

import importlib

from mimetypes import types_map

import pytest

from fastapi import status as http_status

from fastapi_learning import TokenData
from fastapi_learning.common.jwt_utils import decode_access_token

from fastapi_learning.common.consts import (
    RESPONSE_FORMAT,
    LOGIN_PAGE_TITLE,
    HOME_PAGE_TITLE,
    BAD_LOGIN_MSG,
    INVALID_USERNAME_PASSWORD_MSG
)

from tests import test_main

from tests import logout, login

@pytest.mark.auth_integration
def test_integration_login_bad_email_html(test_client):
    """
    Test /auth/token path with a valid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        login_data = {
            'username': '@hotmail.com',
            'password': 'password',
            'x-expected-format': 'text/html',
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        # Login page.
        assert (f'<title>{LOGIN_PAGE_TITLE}</title>' in login_response.text) == True
        assert (f'<h4>{BAD_LOGIN_MSG}</h4>' in login_response.text) == True

    finally:
        pass

@pytest.mark.auth_integration
def test_integration_login_bad_email_json(test_client):
    """
    Test /auth/token path with a valid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}

        login_data = {
            'username': '@hotmail.com',
            'password': 'password'
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_400_BAD_REQUEST

        json = login_response.json()
        # assert json['status_code'] == http_status.HTTP_400_BAD_REQUEST
        assert json['detail'] == BAD_LOGIN_MSG

    finally:
        pass

@pytest.mark.auth_integration
def test_integration_login_bad_password_json(test_client):
    """
    Test /auth/token path with a valid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}

        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': '0123456789-0123456789-0123456789-0123456789'
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_400_BAD_REQUEST

        json = login_response.json()
        # assert json['status_code'] == http_status.HTTP_400_BAD_REQUEST
        assert json['detail'] == BAD_LOGIN_MSG

    finally:
        pass

@pytest.mark.auth_integration
def test_integration_valid_login_html(test_client):
    """
    Test /auth/token path with a valid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password',
            'x-expected-format': 'text/html',
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        # Home page.
        assert (f'<title>{HOME_PAGE_TITLE}</title>' in login_response.text) == True
        assert ('<button type="submit" class="btn btn-primary">Logout</button>' in login_response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.auth_integration
def test_integration_valid_login_json(test_client):
    """
    Test /auth/token path with a valid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}

        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password'
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        status = login_response.json()

        token_data = decode_access_token(status['access_token'])
        assert isinstance(token_data, TokenData) == True

        assert token_data.user_name == 'behai_nguyen@hotmail.com'
        assert status['token_type'] == 'bearer'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.auth_integration
def test_integration_invalid_username_login_html(test_client):
    """
    Test /auth/token path with an invalid username.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    login_data = {
        'username': 'behai@example.com',
        'password': 'password',
        'x-expected-format': 'text/html',
    }
    response = test_client.post('/auth/token', data=login_data)

    assert response != None
    # Return data is HTML. status_code can only be 200.
    # assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert response.status_code == http_status.HTTP_200_OK

    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert ('<h4>Incorrect username or password</h4>' in response.text) == True

@pytest.mark.auth_integration
def test_integration_invalid_password_login_html(test_client):
    """
    Test /auth/token path with an invalid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    login_data = {
        'username': 'behai_nguyen@hotmail.com',
        'password': 'xxxx',
        'x-expected-format': 'text/html',
    }
    response = test_client.post('/auth/token', data=login_data)

    assert response != None
    # Return data is HTML. status_code can only be 200.
    # assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert response.status_code == http_status.HTTP_200_OK

    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert ('<h4>Incorrect username or password</h4>' in response.text) == True

@pytest.mark.auth_integration
def test_integration_invalid_username_login_json(test_client):
    """
    Test /auth/token path with an invalid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    # Expect JSON response.
    test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

    login_data = {
        'username': 'behai@example.com',
        'password': 'password'
    }
    response = test_client.post('/auth/token', data=login_data)

    assert response != None
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST

    status = response.json()
    assert status['detail'] == INVALID_USERNAME_PASSWORD_MSG

@pytest.mark.auth_integration
def test_integration_invalid_password_login_json(test_client):
    """
    Test /auth/token path with an invalid credential.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    # Expect JSON response.
    test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

    login_data = {
        'username': 'behai_nguyen@hotmail.com',
        'password': 'xxxx'
    }
    response = test_client.post('/auth/token', data=login_data)

    assert response != None
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST

    status = response.json()
    assert status['detail'] == INVALID_USERNAME_PASSWORD_MSG

@pytest.mark.auth_integration
def test_integration_valid_login_twice(test_client):
    """
    Test posting to /auth/token twice, both times with valid credentials.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password',
            'x-expected-format': 'text/html',
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        # Set session (Id) for next request.
        # 
        # Need to set this to simulate the real environment.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.post('/auth/token', data=login_data)

        # Not an error response.
        # The second login, redirect to home page.
        assert ('<title>Learn FastAPI Home</title>' in login_response.text) == True
        assert ('<button type="submit" class="btn btn-primary">Logout</button>' in login_response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.auth_integration
def test_integration_logout_with_prior_login(test_client):
    """
    Test '/auth/logout' after a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    # Login.
    login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

    # Set session (Id) for next request.
    session_cookie = login_response.cookies.get('session')
    test_client.cookies = {'session': session_cookie}

    response = test_client.post('/auth/logout')

    assert response != None
    assert response.status_code == http_status.HTTP_200_OK

    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert ('<h2>This session has not been logged in before</h2>' in response.text) == False

@pytest.mark.auth_integration
def test_integration_logout_without_prior_login(test_client):
    """
    Test '/auth/logout' without log in prior.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    response = test_client.post('/auth/logout')

    assert response != None
    assert response.status_code == http_status.HTTP_200_OK

    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert ('<h4>This session has not been logged in before</h4>' in response.text) == True

@pytest.mark.auth_integration
def test_integration_root_path_get_login_page(test_client):
    """
    Test default path '/', response is login page HTML.

    Identical to test_integration_login_page().
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    response = test_client.get('/')
    assert response != None
    assert response.status_code == http_status.HTTP_200_OK

    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert ('<h2>This session has not been logged in before</h2>' in response.text) == False

@pytest.mark.auth_integration
def test_integration_get_login_page(test_client):
    """
    Test default path '/auth/login', response is login page HTML.

    Identical to test_integration_index_default_login_page().
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    response = test_client.get('/auth/login')
    assert response != None
    assert response.status_code == http_status.HTTP_200_OK

    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert ('<h2>This session has not been logged in before</h2>' in response.text) == False

@pytest.mark.auth_integration
def test_integration_get_login_page_while_logged_in(test_client):
    """    
    Test get login page '/auth/login' while already logged in.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password'
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        # Set session (Id) for next request.
        # 
        # Need to set this to simulate the real environment.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/auth/login')
        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # Not an error response.
        assert response != None
        assert response.status_code == http_status.HTTP_200_OK
        # Should get home page.
        assert ('<title>Learn FastAPI Home</title>' in response.text) == True
        assert ('<button type="submit" class="btn btn-primary">Logout</button>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)
