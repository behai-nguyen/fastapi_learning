"""
14/05/2024.
"""

from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends,     
    HTTPException, 
    Security,
    status,
    Request,
    status,
)

from fastapi.security import SecurityScopes

from fastapi_learning import oauth2_scheme

from fastapi.responses import RedirectResponse

from fastapi_learning.controllers import (
    is_logged_in,
    templates,
)

from fastapi_learning.models.employees import LoggedInEmployee

from fastapi_learning.businesses.employees_mgr import EmployeesManager

from fastapi_learning.common.jwt_utils import decode_access_token

from fastapi_learning.common.consts import (
    NOT_AUTHENTICATED_MSG,
    INVALID_AUTH_CREDENTIALS_MSG,
    ME_PAGE_TITLE,
    INVALID_PERMISSIONS_MSG,
)

from fastapi_learning.common.queue_logging import logger
from fastapi_learning.common.scope_utils import has_required_permissions

from . import json_req, JsonAPIRoute

logger = logger()

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

api_router = APIRouter(route_class=JsonAPIRoute,
    prefix="/api",
    tags=["API"],
)

async def get_current_user(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)]):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=NOT_AUTHENTICATED_MSG,
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    # OAuth2PasswordBearer auto_error has been set to False. 
    # The return value is None instead of an HTTPException.
    # This is the same exception raised by OAuth2PasswordBearer. 
    # We are taking control of the authentication flow.    
    if token == None:
        logger.debug(NOT_AUTHENTICATED_MSG)
        return credentials_exception
    
    token_data = decode_access_token(token)
    
    if isinstance(token_data, HTTPException):
        return token_data

    op_status = EmployeesManager().select_by_email(token_data.user_name)

    # Enables this to simulate token became invalid after logged in.
    # op_status = EmployeesManager().select_by_email('token@gmail.com')
    if op_status.code != status.HTTP_200_OK:
        logger.debug(INVALID_AUTH_CREDENTIALS_MSG)
        credentials_exception.detail = INVALID_AUTH_CREDENTIALS_MSG
        return credentials_exception

    if not has_required_permissions(security_scopes.scopes, token_data.scopes): 
        logger.debug(INVALID_PERMISSIONS_MSG)
        credentials_exception.detail = INVALID_PERMISSIONS_MSG
        return credentials_exception

    return LoggedInEmployee(**op_status.data[0])

@router.get("/me")
async def read_users_me(
    request: Request,
    current_user: Annotated[LoggedInEmployee, 
                            Security(get_current_user, scopes=["user:read"])]
):
    """
    This returns the currently logged-in user’s information in either 
    ``JSON`` or ``HTML`` format.

    - The default return format is ``HTML``.

    - If the request header ``x-expected-format`` is present and its value 
      is ``application/json``, then the return format is ``JSON``.

    There are two possible error conditions:

    - Not logged in: The users have not yet authenticated.

    - Invalid credentials: The requests contain an ``Authorization`` 
      header with an invalid token, such as ``Bearer behai_``.

    When an error occurs, the return format is:

    - ``JSON``: The response ``status_code`` is ``HTTP_401_UNAUTHORIZED``. 
      The ``detail`` field value is a text message.

    - ``HTML``: The response ``status_code`` is ``HTTP_200_OK``. The 
      HTML text is the login page with the message ``LOG_IN_CONTINUE_MSG``.
    """

    def page_me():
        user_dict = vars(current_user)
        user_dict.update({"title": ME_PAGE_TITLE})

        return templates.TemplateResponse(request=request, name="admin/me.html", 
                context={'data': user_dict})
        
    if isinstance(current_user, LoggedInEmployee):
        logger.debug('Returning a valid logged-in user.')

        return current_user if json_req(request) else page_me()
    else:
        logger.debug('No valid logged-in user found.')

        if json_req(request): 
            raise current_user
        else: 
            if is_logged_in(request):                
                # This error:
                # {'status_code': 401, 'detail': 'Invalid authentication credentials', 'headers': {'WWW-Authenticate': 'Bearer'}}
                # should not happen. It happens if the email in the database changed while                 
                # user logged in.
                #
                return templates.TemplateResponse(request=request, name="admin/me.html", 
                        context={'data': vars(current_user)})
            else:
                return RedirectResponse(url='/auth/login?state=2')

#=================================== /api ==================================

@api_router.get("/me")
async def read_users_me_api(
    request: Request,
    current_user: Annotated[LoggedInEmployee, 
                            Security(get_current_user, scopes=["user:read"])]
):
    """
    This endpoint is equivalent to ``/admin/me``, with the incoming request 
    header ``x-expected-format`` set to ``application/json``.

    For documentation, please refer to the method [read_users_me](docs#/Admin/read_users_me_admin_me_get).
    """
    
    return await read_users_me(request, current_user)
