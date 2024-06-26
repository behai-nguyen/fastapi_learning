"""
14/05/2024.
"""

from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends,     
    HTTPException, 
    status,
    Request,
)

from fastapi_learning import oauth2_scheme

from fastapi.responses import RedirectResponse

from fastapi_learning.controllers import templates

from fastapi_learning.models.employees import (
    User,
    fake_decode_token,
    UserInDB,
)

from fastapi_learning.common.consts import (
    INVALID_AUTH_CREDENTIALS_MSG,
    NOT_AUTHENTICATED_MSG,
    ME_PAGE_TITLE,
)

from . import json_req, JsonAPIRoute

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

api_router = APIRouter(route_class=JsonAPIRoute,
    prefix="/api",
    tags=["API"],
)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # OAuth2PasswordBearer auto_error has been set to False. 
    # The return value is None instead of an HTTPException.
    # This is the same exception raised by OAuth2PasswordBearer. 
    # We are taking control of the authentication flow.    
    if token == None:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NOT_AUTHENTICATED_MSG,
            headers={"WWW-Authenticate": "Bearer"},
        )        

    user = fake_decode_token(token)
    if not user:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_AUTH_CREDENTIALS_MSG,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
    
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

@router.get("/me")
async def read_users_me(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)]
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
      The ``detail`` field value is either ``NOT_AUTHENTICATED_MSG`` 
      or ``INVALID_AUTH_CREDENTIALS_MSG``.

    - ``HTML``: The response ``status_code`` is ``HTTP_200_OK``. The 
      HTML text is the login page with the message ``LOG_IN_CONTINUE_MSG``.
    """

    def page_me():
        user_dict = vars(current_user)
        user_dict.update({"title": ME_PAGE_TITLE})

        return templates.TemplateResponse(request=request, name="admin/me.html", 
                context=user_dict)
        
    if isinstance(current_user, UserInDB):        
        return current_user if json_req(request) else page_me()
    else:
        if json_req(request): 
            raise current_user  
        else: 
            return RedirectResponse(url='/auth/login?state=2')

#=================================== /api ==================================

@api_router.get("/me")
async def read_users_me_api(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    This endpoint is equivalent to ``/admin/me``, with the incoming request 
    header ``x-expected-format`` set to ``application/json``.

    For documentation, please refer to the method [read_users_me](docs#/Admin/read_users_me_admin_me_get).
    """
    
    return await read_users_me(request, current_user)
