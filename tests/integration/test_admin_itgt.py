# 
# 20/05/2024.
# 
# Test authentication related routes.
# 
# venv\Scripts\pytest.exe -m admin_integration
# venv\Scripts\pytest.exe -k _integration_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m admin_integration --capture=no
# 

import pytest

from http import HTTPStatus

from tests import logout, login

@pytest.mark.admin_integration
def test_integration_valid_admin_own_detail(test_client):
    """
    Test /admin/me path after a valid login.
    """

    try:
        # Login.
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/admin/me')

        assert response != None
        assert response.status_code == HTTPStatus.OK.value

        status = response.json()
        assert status['username'] == 'behai_nguyen@hotmail.com'
        assert status['first_name'] == 'Be Hai'
        assert status['last_name'] == 'Doe'
        assert status['hashed_password'] == '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.admin_integration
def test_integration_invalid_admin_own_detail(test_client):
    """
    Test /admin/me path without a valid login.
    """

    # No valid login.
    response = test_client.get('/admin/me')

    assert response != None
    assert response.status_code == HTTPStatus.UNAUTHORIZED.value

    status = response.json()

    # This is identical to the response seen in Swagger UI.
    # I don't know where in the code it is from.
    assert status['detail'] == 'Not authenticated'
