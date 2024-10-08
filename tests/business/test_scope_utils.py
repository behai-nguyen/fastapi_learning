"""
Test scopes / permissions utility functions in module common\scope_utils.py.

venv\Scripts\pytest.exe -m scope_permission
venv\Scripts\pytest.exe -k _scope_ -v

Use --capture=no to enable print output. I.e.:

venv\Scripts\pytest.exe -m scope_permission --capture=no
"""

import pytest

from fastapi_learning.common.scope_utils import has_required_permissions

@pytest.mark.scope_permission
def test_scope_has_required_permissions_no_assigned_scopes(app):
    REQUIRED_SCOPES = ['user:read']
    ASSIGNED_SCOPES = []
    res = has_required_permissions(REQUIRED_SCOPES, ASSIGNED_SCOPES)
    assert res == False, "Should be False."

@pytest.mark.scope_permission
def test_scope_has_required_permissions(app):
    REQUIRED_SCOPES = ['user:write']
    ASSIGNED_SCOPES = ['super:*']
    res = has_required_permissions(REQUIRED_SCOPES, ASSIGNED_SCOPES)
    assert res == True, "1. Should be True."

    REQUIRED_SCOPES = ['user:write']
    ASSIGNED_SCOPES = ['user:read', 'admin:read']
    res = has_required_permissions(REQUIRED_SCOPES, ASSIGNED_SCOPES)
    assert res == False, "2. Should be False."

    REQUIRED_SCOPES = ['admin:read', 'admin:write']
    ASSIGNED_SCOPES = ['user:read', 'user:write']
    res = has_required_permissions(REQUIRED_SCOPES, ASSIGNED_SCOPES)
    assert res == False, "3. Should be False."

    REQUIRED_SCOPES = ['user:read', 'user:write', 'admin:read', 'admin:write']
    ASSIGNED_SCOPES = ['super:*']
    res = has_required_permissions(REQUIRED_SCOPES, ASSIGNED_SCOPES)
    assert res == True, "4. Should be True."

    REQUIRED_SCOPES = ['user:read', 'user:write', 'admin:read', 'admin:write']
    ASSIGNED_SCOPES = ['user:read', 'user:write', 'admin:read', 'admin:write']
    res = has_required_permissions(REQUIRED_SCOPES, ASSIGNED_SCOPES)
    assert res == True, "5. Should be True."

@pytest.mark.scope_permission
def test_scope_has_required_permissions_not_handled(app):
    #
    # 'super:*' includes 'user:read', 'user:write', 'admin:read', 'admin:write'.
    # So logically, has_required_permissions(...) should return a True, but 
    # it does not look into each required scope included scopes list and also 
    # checks invidiual included scopes against the assigned scopes.
    # 
    # Therefore, it return False. 
    #
    REQUIRED_SCOPES = ['super:*']
    ASSIGNED_SCOPES = ['user:read', 'user:write', 'admin:read', 'admin:write']

    res = has_required_permissions(REQUIRED_SCOPES, ASSIGNED_SCOPES)
    assert res == False, "Should be False."