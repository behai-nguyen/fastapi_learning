# 
# 17/10/2024.
# 
# Test ENABLE_NO_SCOPES_UI option and user scopes availability.
#
# Reference: https://stackoverflow.com/a/71428106
# 
# venv\Scripts\pytest.exe -m scope_ui_itgt
# venv\Scripts\pytest.exe -k _scope_ui_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m scope_ui_itgt --capture=no
# 

import os
import importlib

import pytest

from fastapi import status as http_status

from tests import test_main

from tests import logout

@pytest.mark.scope_ui_itgt
def test_scope_ui_home_html_01(test_client):
    """
    Test home page via /auth/token path.

    When ENABLE_NO_SCOPES_UI is True, UI elements are enabled even though
    logged in user has no appropriate scopes.

    User 'moss.shanbhogue.10045@gmail.com' has no assigned scopes.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    original_enable_no_scopes_ui = os.environ.get('ENABLE_NO_SCOPES_UI')

    try:
        os.environ['ENABLE_NO_SCOPES_UI'] = 'True'

        login_data = {
            'username': 'moss.shanbhogue.10045@gmail.com',
            'password': 'password',
            'x-expected-format': 'text/html',
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        # Home page: UI elements are not disabled.
        button = '<button type="button" id="meBtn" class="btn btn-link" >My Info as JSON</button>'
        assert (button in login_response.text) == True
        button = '<button type="submit" class="btn btn-primary" >My Info</button>'
        assert (button in login_response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)
        os.environ['ENABLE_NO_SCOPES_UI'] = original_enable_no_scopes_ui

@pytest.mark.scope_ui_itgt
def test_scope_ui_home_html_02(test_client):
    """
    Test home page via /auth/token path.

    When ENABLE_NO_SCOPES_UI is False, UI elements are disabled when 
    logged in user has no appropriate scopes.

    User 'moss.shanbhogue.10045@gmail.com' has no assigned scopes.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    original_enable_no_scopes_ui = os.environ.get('ENABLE_NO_SCOPES_UI')

    try:
        os.environ['ENABLE_NO_SCOPES_UI'] = 'False'

        login_data = {
            'username': 'moss.shanbhogue.10045@gmail.com',
            'password': 'password',
            'x-expected-format': 'text/html',
        }
        login_response = test_client.post('/auth/token', data=login_data)

        assert login_response != None
        assert login_response.status_code == http_status.HTTP_200_OK

        # Home page: UI elements are disabled.
        button = '<button type="button" id="meBtn" class="btn btn-link" disabled>My Info as JSON</button>'
        assert (button in login_response.text) == True
        button = '<button type="submit" class="btn btn-primary" disabled>My Info</button>'
        assert (button in login_response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)
        os.environ['ENABLE_NO_SCOPES_UI'] = original_enable_no_scopes_ui