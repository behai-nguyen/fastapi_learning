"""
14/05/2024.
"""

from typing import Annotated, Union

from fastapi import (
    APIRouter, 
    Depends,     
    Security,
    Request,
    HTTPException,
)

from fastapi.security import SecurityScopes

from bh_apistatus.result_status import make_status

from fastapi_learning.controllers import (
    verify_user_scopes,
    templates,
)

from fastapi_learning.models.employees import LoggedInEmployee

from fastapi_learning.common.consts import (
    ME_PAGE_TITLE,
    INVALID_PERMISSIONS_MSG,
)

from fastapi_learning.common.queue_logging import logger

from fastapi_learning.controllers.required_login import (
    get_logged_in_user,
    delete_cached_logged_in_user,
)

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
        user = Depends(get_logged_in_user),
) -> Union[HTTPException | LoggedInEmployee]:
    """
    Current user is the logged in user.

    get_logged_in_user() is called to verify an authenticated session and 
    retrieve the logged-in user. Then based on the logged-in user's scopes,
    verify that they have sufficient permissions to view their own details, 
    otherwise return HTTPException with appropriate error.
    """

    res, exception = await verify_user_scopes(security_scopes, user, INVALID_PERMISSIONS_MSG)
    if not res: 
        logger.debug(INVALID_PERMISSIONS_MSG)
        return exception

    return user

@router.get("/me")
@api_router.get("/me")
async def read_users_me(
    request: Request, 
    current_user: Annotated[LoggedInEmployee, 
                            Security(get_current_user, scopes=["user:read"])]
):
    """
    Implements both ``/admin/me`` and ``/api/me``. 
    
    For ``/admin/me``: The default return format is ``HTML``.

    For ``/api/me``: The incoming request header ``x-expected-format`` set 
    to ``application/json``.

    This returns the currently logged-in user’s information in either 
    ``JSON`` or ``HTML`` format.

    - The default return format is ``HTML``.

    - If the request header ``x-expected-format`` is present and its value 
      is ``application/json``, then the return format is ``JSON``.

    There are two possible error conditions:

    - Not logged in: The users have not yet authenticated.

    - Invalid credentials: The requests contain an ``Authorization`` 
      header with an invalid token, such as ``Bearer behai_``.

    See ./tests/integration/test_admin_itgt.py for more detail on possible 
    responses.
    """

    def page_me():
        user_dict = vars(current_user)
        user_dict.update({"title": ME_PAGE_TITLE})

        return templates.TemplateResponse(request=request, name="admin/me.html", 
                context={'data': user_dict})

    # get_current_user(...) creates a cached session entry for logged in user.
    #    A cached entry is always created for a valid login, regardless of 
    #    whether or not the user has user:read scope to read their own details.
    delete_cached_logged_in_user(request)

    if isinstance(current_user, LoggedInEmployee):
        logger.debug('Returning a valid logged-in user.')

        return make_status().add_data(vars(current_user)).as_dict() \
            if json_req(request) else page_me()

    else:
        logger.debug(current_user.detail)

        if json_req(request):
            return make_status(code=current_user.status_code, text=current_user.detail).as_dict()
        else: 
            return templates.TemplateResponse(request=request, name="admin/me.html", 
                    context={'data': vars(current_user)})
