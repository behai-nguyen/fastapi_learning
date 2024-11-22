# 
# 12/11/2024
#
# Redirect to login using custom exception handlers. 
#
# Reference: https://stackoverflow.com/a/76887329
#

from typing import Annotated, Union

from fastapi import HTTPException, Depends, status

from fastapi_learning import oauth2_scheme

from fastapi_learning.businesses.employees_mgr import EmployeesManager
from fastapi_learning.models.employees import LoggedInEmployee

from fastapi_learning.controllers import attempt_decoding_access_token

from fastapi_learning.common.consts import (
    NOT_AUTHENTICATED_MSG,
    INVALID_AUTH_CREDENTIALS_MSG,
)

class RequiresLogin(Exception):
    """
    Exception to redirect to login route.
    """
    pass

async def get_logged_in_user(token: Annotated[str, Depends(oauth2_scheme)]) \
    -> Union[HTTPException | LoggedInEmployee]:

    """
    Dependency for endpoint handlers which require authenticated session.
    """
    
    token_data = attempt_decoding_access_token(token)

    if isinstance(token_data, HTTPException):
        raise RequiresLogin(NOT_AUTHENTICATED_MSG)
    
    op_status = EmployeesManager().select_by_email(token_data.user_name)

    if op_status.code != status.HTTP_200_OK:
        raise RequiresLogin(INVALID_AUTH_CREDENTIALS_MSG)

    return LoggedInEmployee(**op_status.data[0])
