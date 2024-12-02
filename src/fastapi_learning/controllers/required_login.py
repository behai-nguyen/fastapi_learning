# 
# 12/11/2024
#
# Redirect to login using custom exception handlers. 
#
# Reference: https://stackoverflow.com/a/76887329
#

from typing import Annotated, Union

from fastapi import HTTPException, Depends, status, Request

from fastapi_learning import oauth2_scheme

from fastapi_learning.businesses.employees_mgr import EmployeesManager
from fastapi_learning.models.employees import LoggedInEmployee

from fastapi_learning.controllers import attempt_decoding_access_token

from fastapi_learning.common.consts import INVALID_AUTH_CREDENTIALS_MSG

class RequiresLogin(HTTPException):
    """
    Exception to redirect to login route.
    """
    pass

async def get_logged_in_user(request: Request,
                             token: Annotated[str, Depends(oauth2_scheme)]) \
    -> Union[HTTPException | LoggedInEmployee]:

    """
    Dependency for endpoint handlers which require authenticated session.
    """
    
    token_data = attempt_decoding_access_token(token)

    if isinstance(token_data, HTTPException):
        raise RequiresLogin(token_data.status_code, token_data.detail)
    
    op_status = EmployeesManager().select_by_email(token_data.user_name)

    if op_status.code != status.HTTP_200_OK:
        raise RequiresLogin(op_status.code, INVALID_AUTH_CREDENTIALS_MSG)
    
    # To be retrieved by method async def get_cached_logged_in_user(...).
    logged_in_user = LoggedInEmployee(**op_status.data[0], scopes=token_data.scopes)
    request.session["logged_in_user"] = logged_in_user.model_dump_json()
    
    return logged_in_user
    
async def get_cached_logged_in_user(request: Request) -> LoggedInEmployee:
    """
    Retrieve the cached logged-in user in session stored by get_logged_in_user(...).
    The intention is this method is called in the same request after verifying the 
    session is authenticated and not expired.
    """

    import json

    return LoggedInEmployee( **json.loads(request.session["logged_in_user"]) )
