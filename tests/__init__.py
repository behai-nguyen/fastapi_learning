# 
# 15/05/2024.
# 
# Tests helper functions.
# 

from http import HTTPStatus

from fastapi import Response
from fastapi.testclient import TestClient

# 
# Note: import the main.py module so that conftest.py can
# import this, i.e. test_main.
# 
import main as test_main

def logout(last_response: Response, test_client: TestClient):
    """
    Logout test session. HTTP server session deleted from the 
    session store.
    """

    session_cookie = last_response.cookies.get('session')
    test_client.cookies = {'session': session_cookie}
    test_client.post('/auth/logout')

def login(username: str, password: str,
          test_client: TestClient) -> Response:
    """
    Log in a test session.
    """

    login_data = {
        'username': username,
        'password': password
    }
    response = test_client.post(  
        '/auth/token', 
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    assert response != None
    assert response.status_code == HTTPStatus.OK.value
    
    return response