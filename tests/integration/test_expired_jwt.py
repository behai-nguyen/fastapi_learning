# 
# 25/09/2024.
# 
# Test expired access token.
#
# venv\Scripts\pytest.exe -m expired_jwt
# venv\Scripts\pytest.exe -k _expired_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m expired_jwt --capture=no
# 

import os
from datetime import timedelta
import time

import importlib

import pytest

from fastapi import status as http_status
from mimetypes import types_map

from fastapi_learning.common.jwt_utils import create_access_token

from fastapi_learning.common.consts import (
    RESPONSE_FORMAT,
    INVALID_CREDENTIALS_MSG,
)

from tests import (
    test_main, 
    logout, 
    login,
)

@pytest.mark.expired_jwt
def test_expired_jwt_json_response(test_client):
    """
    Test /admin/me path with an expired token. The response is in JSON.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    # Create a valid access token that expires in 2 seconds.
    access_token_expires = timedelta(seconds=2)
    access_token = create_access_token(data={'sub': 'behai_nguyen@hotmail.com'}, 
                                       expires_delta=access_token_expires)
    # Waits out for the access token to expire.
    time.sleep(3)

    # 'Authorization' is the credential.
    # Expect JSON response.
    test_client.headers = {RESPONSE_FORMAT: types_map['.json'],
                        'Authorization': f'Bearer {access_token}'}
    
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
    assert status['status']['text'] == INVALID_CREDENTIALS_MSG

@pytest.mark.expired_jwt
def test_expired_jwt_html_response(test_client):
    """
    Test /admin/me path with an expired token. 
    The response is the HTML login page.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    original_expire_seconds = os.environ.get('ACCESS_TOKEN_EXPIRE_SECONDS')

    try:
        # Login access token expires in 2 seconds.
        os.environ['ACCESS_TOKEN_EXPIRE_SECONDS'] = '2'

        # Login.
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # Waits out for the access token to expire.
        time.sleep(3)

        response = test_client.get('/admin/me')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # The login.html page with a specific message.
        assert ('<title>Learn FastAPI Login</title>' in response.text) == True
        assert (f'<h4>{INVALID_CREDENTIALS_MSG}</h4>' in response.text) == True
        assert ('<input type="email" ' in response.text) == True
        assert (' id="password" name="password" ' in response.text) == True
        
    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)
        os.environ['ACCESS_TOKEN_EXPIRE_SECONDS'] = original_expire_seconds
