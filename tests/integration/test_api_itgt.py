# 
# 09/06/2024.
# 
# Test API related routes.
#
# venv\Scripts\pytest.exe -m api_integration
# venv\Scripts\pytest.exe -k _api_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m api_integration --capture=no
# 
# Note: Tests in module have all been covered in:
# 
#     tests\integration\test_auth_itgt.py
#     tests\integration\test_admin_itgt.py
#
# The primary objective of these tests is the 
# F:\fastapi_learning\src\fastapi_learning\controllers\__init__.py
# JsonAPIRoute class: i.e. setting incoming request header
#     x-expected-format = 'application/json'
# 
# before actually calling the endpoint.
#
# Therefore, tests are for valid cases, no point repeating 
# duplicate tests.
#

import importlib

import pytest

from fastapi import status as http_status

from fastapi_learning import TokenData
from fastapi_learning.common.jwt_utils import decode_access_token

from tests import test_main

from tests import logout, login

@pytest.mark.api_integration
def test_integration_valid_login(test_client):
    """
    Test /api/login path with a valid credential.
    """

    importlib.reload(test_main)

    try:
        login_data = {
            'username': 'behai_nguyen@hotmail.com',
            'password': 'password'
        }
        login_response = test_client.post('/api/login', data=login_data)

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

@pytest.mark.api_integration
def test_integration_valid_admin_own_detail(test_client):
    """
    Test /api/me path after a valid login.
    """

    importlib.reload(test_main)

    try:
        # Login.
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/api/me')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status['email'] == 'behai_nguyen@hotmail.com'
        assert status['first_name'] == 'Be Hai'
        assert status['last_name'] == 'Nguyen'
        assert status['password'] == '$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)