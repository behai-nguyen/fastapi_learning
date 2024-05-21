# 
# 15/05/2024.
# 
# Test authentication related routes.
# 
# venv\Scripts\pytest.exe -m auth_integration
# venv\Scripts\pytest.exe -k _integration_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m auth_integration --capture=no
# 

import pytest

from http import HTTPStatus

from fastapi_learning.common.consts import (
    INVALID_USERNAME_PASSWORD_MSG,
    # INVALID_AUTH_CREDENTIALS_MSG
    LOGGED_IN_SESSION_MSG,
)

from tests import logout, login

@pytest.mark.auth_integration
def test_integration_valid_login(test_client):
    """
    Test /auth/token path with a valid credential.
    """

    try:
        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password'
        }
        login_response = test_client.post(  
            '/auth/token', 
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        assert login_response != None
        assert login_response.status_code == HTTPStatus.OK.value

        status = login_response.json()
        assert status['access_token'] == 'behai_nguyen@hotmail.com'
        assert status['token_type'] == 'bearer'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.auth_integration
def test_integration_invalid_login(test_client):
    """
    Test /auth/token path with an invalid credential.
    """

    login_data = {
        'username': 'behai@example.com',
        'password': 'password'
    }
    response = test_client.post(  
        '/auth/token', 
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    assert response != None
    assert response.status_code == HTTPStatus.BAD_REQUEST.value

    status = response.json()
    assert status['detail'] == INVALID_USERNAME_PASSWORD_MSG

@pytest.mark.auth_integration
def test_integration_valid_login_twice(test_client):
    """
    Test posting to /auth/token twice, both times with valid credentials.
    """
    try:
        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password'
        }
        login_response = test_client.post(  
            '/auth/token', 
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        assert login_response != None
        assert login_response.status_code == HTTPStatus.OK.value

        # Set session (Id) for next request.
        # 
        # Need to set this to simulate the real environment.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.post(  
            '/auth/token', 
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )        

        # Not an error response.
        assert response != None
        assert response.status_code == HTTPStatus.OK.value
        assert response.json() == {"message": LOGGED_IN_SESSION_MSG}

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.auth_integration
def test_integration_logout_with_prior_login(test_client):
    """
    Test '/auth/logout' after a valid login.
    """

    # Login.
    login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

    # Set session (Id) for next request.
    session_cookie = login_response.cookies.get('session')
    test_client.cookies = {'session': session_cookie}

    response = test_client.post('/auth/logout')

    assert response != None
    assert response.status_code == HTTPStatus.OK.value

    assert ('<title>FastAPI Login</title>' in response.text) == True
    assert ('<h2>This session has not been logged in before</h2>' in response.text) == False

@pytest.mark.auth_integration
def test_integration_logout_without_prior_login(test_client):
    """
    Test '/auth/logout' without log in prior.
    """

    response = test_client.post('/auth/logout')

    assert response != None
    assert response.status_code == HTTPStatus.OK.value

    assert ('<title>FastAPI Login</title>' in response.text) == True
    assert ('<h2>This session has not been logged in before</h2>' in response.text) == True

@pytest.mark.auth_integration
def test_integration_root_path_get_login_page(test_client):
    """
    Test default path '/', response is login page HTML.

    Identical to test_integration_login_page().
    """

    response = test_client.get('/')
    assert response != None
    assert response.status_code == HTTPStatus.OK.value

    assert ('<title>FastAPI Login</title>' in response.text) == True
    assert ('<h2>This session has not been logged in before</h2>' in response.text) == False

@pytest.mark.auth_integration
def test_integration_get_login_page(test_client):
    """
    Test default path '/auth/login', response is login page HTML.

    Identical to test_integration_index_default_login_page().
    """

    response = test_client.get('/auth/login')
    assert response != None
    assert response.status_code == HTTPStatus.OK.value

    assert ('<title>FastAPI Login</title>' in response.text) == True
    assert ('<h2>This session has not been logged in before</h2>' in response.text) == False

@pytest.mark.auth_integration
def test_integration_get_login_page_while_logged_in(test_client):
    """    
    Test get login page '/auth/login' while already logged in.
    """
    try:
        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password'
        }
        login_response = test_client.post(  
            '/auth/token', 
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        assert login_response != None
        assert login_response.status_code == HTTPStatus.OK.value

        # Set session (Id) for next request.
        # 
        # Need to set this to simulate the real environment.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/auth/login')
        assert response != None
        assert response.status_code == HTTPStatus.OK.value

        # Not an error response.
        assert response != None
        assert response.status_code == HTTPStatus.OK.value
        assert response.json() == {"message": LOGGED_IN_SESSION_MSG}

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)
