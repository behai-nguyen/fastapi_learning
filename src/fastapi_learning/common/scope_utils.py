"""
02/10/2024.
"""

from fastapi_learning import APP_SCOPE_DEPENDENCIES

def has_required_permissions(required_scopes: list, assigned_scopes: list) -> bool:
    """Check that all scopes in required_scopes list are in assigned_scopes or
    in each assigned scope included scopes.

    :param list required_scopes: individual specific scopes required for 
        a specific operation.

    :param list assigned_scopes: assigned scopes and their included scopes.

    :return: bool. True if all required scopes appear in assigned scopes or 
    their included scopes.
    """

    total_assigned_scopes = len(assigned_scopes)
    
    # No assigned scopes. No permissions to run this request.
    if total_assigned_scopes == 0: return False

    for required_scope in required_scopes:
        for idx, assigned_scope in enumerate(assigned_scopes):
            # The current required scope is in the user assigned scope list.
            # This permission requirement passes, check the next required scope.
            if required_scope == assigned_scope:
                break
            # Does the assigned_scope's included_scopes list has the required_scope
            # scope?
            else:
                # Expect one entry in the scope list.
                scope = [item for item in APP_SCOPE_DEPENDENCIES if item['scope'] == assigned_scope]
                # This should not happen: but it needs to be handled just in case.
                if len(scope) == 0: return False

                matched = False
                for included_scope in scope[0]['included_scopes']:
                    if included_scope == required_scope: 
                        matched = True
                        break

                # Nothing matched and if at the end of the assigned_scopes -- 
                # does not have permission for the requested operation.                
                if ( not matched ) and ( idx == (total_assigned_scopes - 1) ): 
                    return matched

    return True
