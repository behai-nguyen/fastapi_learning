# 
# 04/10/2024.
# 
# Test authorisation related routes and scope permissions.
#
# Reference: https://stackoverflow.com/a/71428106
# 
# venv\Scripts\pytest.exe -m scope_permission_itgt
# venv\Scripts\pytest.exe -k _scope_permission_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m scope_permission_itgt --capture=no
# 

import importlib

import pytest

from fastapi import status as http_status
from mimetypes import types_map

from fastapi_learning import TokenData
from fastapi_learning.common.jwt_utils import decode_access_token

from tests import test_main

from fastapi_learning.common.consts import (
    RESPONSE_FORMAT,
    INVALID_PERMISSIONS_MSG,
)

from tests import logout, login

@pytest.mark.scope_permission_itgt
def test_scope_permission_login_01(test_client):
    """
    User 'behai_nguyen@hotmail.com' is assigend two scopes: 'user:read' and
    'user:write'.

    Assertain that after logging in, the user gets assigned scopes as defined 
    in ./src/fastapi_learning/businesses/employees_mgr.py's MOCK_USER_SCOPES.

    Note: see test module tests\integration\test_auth_itgt.py for complete 
    authorisation (log in) tests.    
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

        assert len(token_data.scopes) == 2
        assert token_data.scopes[0] == 'user:read'
        assert token_data.scopes[1] == 'user:write'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.scope_permission_itgt
def test_scope_permission_login_02(test_client):
    """
    User 'moss.shanbhogue.10045@gmail.com' has no scope.

    Assertain that after logging in, the user gets assigned scopes as defined 
    in ./src/fastapi_learning/businesses/employees_mgr.py's MOCK_USER_SCOPES.

    Note: see test module tests\integration\test_auth_itgt.py for complete 
    authorisation (log in) tests.    
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}

        login_data = {
            'username': 'moss.shanbhogue.10045@gmail.com',
            'password': 'password'
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        status = login_response.json()

        token_data = decode_access_token(status['access_token'])
        assert isinstance(token_data, TokenData) == True

        assert len(token_data.scopes) == 0

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.scope_permission_itgt
def test_scope_permission_login_03(test_client):
    """
    User 'kazuhisa.ranta.10199@gmail.com' has not been explicitly assigned
    any scopes, therefore, getting assigned the default scope 'user:read'.

    Assertain that after logging in, the user gets assigned scopes as defined 
    in ./src/fastapi_learning/businesses/employees_mgr.py's MOCK_USER_SCOPES.

    Note: see test module tests\integration\test_auth_itgt.py for complete 
    authorisation (log in) tests.    
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}

        login_data = {
            'username': 'kazuhisa.ranta.10199@gmail.com',
            'password': 'password'
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        status = login_response.json()

        token_data = decode_access_token(status['access_token'])
        assert isinstance(token_data, TokenData) == True

        assert len(token_data.scopes) == 1
        assert token_data.scopes[0] == 'user:read'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

# The following tests is about authorisation related routes 
# using users whose don't have sufficient permissions for the 
# request endpoints.
#
# Note: other integration test modules also include scope 
# permissions checking, test users used in those modules have
# sufficient scopes. The sole purpose of this module, therefore,
# is to assertain requests denied as expected when users don't
# have sufficient scopes.

@pytest.mark.scope_permission_itgt
def test_scope_permission_invalid_json(test_client):
    """
    Test /admin/me path after a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}
        
        # Login.
        # See ./src/fastapi_learning/businesses/employees_mgr.py's MOCK_USER_SCOPES.
        login_response = login('moss.shanbhogue.10045@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/admin/me')

        assert response != None
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED

        status = response.json()
        print(status)
        assert status['detail'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.scope_permission_itgt
def test_scope_permission_invalid_html(test_client):
    """
    Test /admin/me path after a valid login.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Expect HTML response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.html']}
        
        # Login.
        # See ./src/fastapi_learning/businesses/employees_mgr.py's MOCK_USER_SCOPES.
        login_response = login('moss.shanbhogue.10045@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/admin/me')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # Error page.
        assert ('<h2>It\'s on me... Please contact support, quoting the below message:</h2>' \
                in response.text) == True
        assert ('<h2 class="text-danger fw-bold">Not enough permissions</h2>' \
                in response.text) == True
        assert ('<a class="link-opacity-100" href="/auth/home">Home</a>' \
                in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.scope_permission_itgt
def test_scope_permission_api_me(test_client):
    """
    Test /api/me path after a valid login.
    The response is always in JSON format.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login.
        # See ./src/fastapi_learning/businesses/employees_mgr.py's MOCK_USER_SCOPES.
        login_response = login('moss.shanbhogue.10045@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/api/me')

        assert response != None
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED

        status = response.json()
        print(status)
        assert status['detail'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)
