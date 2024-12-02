# 
# 20/05/2024.
# 
# Test authentication related routes.
#
# Reference: https://stackoverflow.com/a/71428106
# 
# venv\Scripts\pytest.exe -m admin_integration
# venv\Scripts\pytest.exe -k _integration_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m admin_integration --capture=no
# 

import importlib

import pytest

from fastapi import status as http_status

from argon2 import PasswordHasher

from mimetypes import types_map

from tests import test_main

from fastapi_learning.common.jwt_utils import create_access_token

from fastapi_learning.common.consts import (
    RESPONSE_FORMAT,
    NOT_AUTHENTICATED_MSG,
    INVALID_AUTH_CREDENTIALS_MSG,
    INVALID_CREDENTIALS_MSG,
)

from tests import logout, login

@pytest.mark.admin_integration
def test_integration_valid_admin_own_detail_json(test_client):
    """
    Test /admin/me path after a valid login.

    JSON Response:
        {
            "status": {
                "code": 200,
                "text": ""
            },
            "data": {
                "birth_date": "09/12/1978",
                "email": "behai_nguyen@hotmail.com",
                "emp_no": 500222,
                "first_name": "Be Hai",
                "gender": "M",
                "hire_date": "01/11/2022",
                "last_name": "Nguyen",
                "password": "$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA",
                "scopes": [
                    "user:read",
                    "user:write"
                ]
            }
        }
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}

        # Login.
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/admin/me')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        
        # Should always check for this.
        assert status['status']['code'] == http_status.HTTP_200_OK
        assert status['status']['text'] == ''

        assert ('data' in status) == True
        user = status['data']

        assert user['email'] == 'behai_nguyen@hotmail.com'
        assert user['first_name'] == 'Be Hai'
        assert user['last_name'] == 'Nguyen'
        assert PasswordHasher().verify(user['password'], 'password') == True

        assert len(user['scopes']) == 2
        assert user['scopes'][0] == 'user:read'
        assert user['scopes'][1] == 'user:write'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.admin_integration
def test_integration_valid_admin_own_detail_html(test_client):
    """
    Test /admin/me path after a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login.
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/admin/me')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin me.html page.
        assert ('<div class="col-3">behai_nguyen@hotmail.com</div>' in response.text) == True
        assert ('<div class="col-3">Be Hai</div>' in response.text) == True
        assert ('<div class="col-3">Nguyen</div>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.admin_integration
def test_integration_not_auth_admin_own_detail_json(test_client):
    """
    Test /admin/me path without a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    # Expect JSON response.
    test_client.headers = {RESPONSE_FORMAT: types_map['.json']}
    
    # No valid login.
    response = test_client.get('/admin/me')

    # See:
    #     @app.exception_handler(RequiresLogin)
    #     async def requires_login(request: Request, _: Exception):
    assert response != None
    # assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert response.status_code == http_status.HTTP_200_OK

    status = response.json()
    assert status != None
    
    # Should always check for this.
    assert status['status']['code'] == http_status.HTTP_401_UNAUTHORIZED
    assert status['status']['text'] == NOT_AUTHENTICATED_MSG

@pytest.mark.admin_integration
def test_integration_not_auth_admin_own_detail_html(test_client):
    """
    Test /admin/me path without a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    # No valid login.
    response = test_client.get('/admin/me')

    assert response != None
    # Can't set http_status.HTTP_401_UNAUTHORIZED.value!
    assert response.status_code == http_status.HTTP_200_OK

    # Login page.
    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert (f'<h4>{NOT_AUTHENTICATED_MSG}</h4>' in response.text) == True

@pytest.mark.admin_integration
def test_integration_invalid_credentials_admin_own_detail_json(test_client):
    """
    Test /admin/me path without a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    access_token = create_access_token(data={"sub": "behai_", 'emp_no': 8000})

    # 'Authorization' is the credential.
    # Expect JSON response.
    test_client.headers = {RESPONSE_FORMAT: types_map['.json'],
                           'Authorization': f'Bearer {access_token}'}
    
    # No valid login.
    response = test_client.get('/admin/me')

    # See:
    #     @app.exception_handler(RequiresLogin)
    #     async def requires_login(request: Request, _: Exception):
    assert response != None
    # assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert response.status_code == http_status.HTTP_200_OK

    status = response.json()
    
    status = response.json()
    assert status != None
    
    # Should always check for this.
    assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
    assert status['status']['text'] == INVALID_AUTH_CREDENTIALS_MSG

@pytest.mark.admin_integration
def test_integration_invalid_credentials_admin_own_detail_html(test_client):
    """
    Test /admin/me path without a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    # 'Authorization' is the credential.
    test_client.headers = {'Authorization': 'Bearer behai_'}
    
    # No valid login.
    response = test_client.get('/admin/me')

    assert response != None
    # Can't set http_status.HTTP_401_UNAUTHORIZED!
    assert response.status_code == http_status.HTTP_200_OK

    print(f"\n{response.text}\n")

    # Login page.
    assert ('<title>Learn FastAPI Login</title>' in response.text) == True
    assert (f'<h4>{INVALID_CREDENTIALS_MSG}</h4>' in response.text) == True
