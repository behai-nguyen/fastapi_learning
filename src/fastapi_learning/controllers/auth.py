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
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse,
)

from bh_apistatus.result_status import (
    ResultStatus, 
    make_status,
)

from fastapi_learning import Token

from fastapi_learning.models.employees import LoggedInEmployee
from fastapi_learning.businesses.employees_mgr import EmployeesManager

from fastapi_learning.controllers import (
    templates,
    json_req,
    set_access_token,
    get_access_token,
    delete_access_token,
    no_access_token,
    set_login_redirect_code,
    get_login_redirect_code,
    delete_login_redirect_code,
    set_login_redirect_message,
    get_login_redirect_message,
    delete_login_redirect_message,
)

from fastapi_learning.common.jwt_utils import create_access_token

from fastapi_learning.common.consts import (
    LOGIN_REDIRECT_STATE_CERTAIN,
    LOGIN_PAGE_TITLE,
    HOME_PAGE_TITLE,
    LOGIN_ERROR_MSG,
    BAD_LOGIN_MSG,
    INVALID_USERNAME_PASSWORD_MSG,
    NOT_LOGGED_IN_SESSION_MSG,
    LOGGED_IN_SESSION_MSG,
)

from fastapi_learning.common.queue_logging import logger

from fastapi_learning.controllers.required_login import get_logged_in_user

from . import (
    html_req, 
    JsonAPIRoute,
)

logger = logger()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

api_router = APIRouter(route_class=JsonAPIRoute,
    prefix="/api",
    tags=["API"],
)

def __login_response(request: Request) -> HTMLResponse: 
    logger.debug('Delivering the login response.')

    message = get_login_redirect_message(request, delete_also=True)

    # The login page request is ALWAYS HTML.
    # But there is only a single login redirect route, other JSON requests 
    # which require authenticated session also get redirected here when 
    # their sessions are not authenticated, hence has to respond in JSON.
    if json_req(request):
        return JSONResponse(make_status(code=get_login_redirect_code(request, delete_also=True), 
                                        text=message).as_dict())

    return templates.TemplateResponse(request=request, 
                name="auth/login.html", 
                context={"title": LOGIN_PAGE_TITLE, 
                         "message": message})

@router.get("/login")
async def login_page(request: Request, state: int = 0) -> HTMLResponse:
    """
    HTML response: Return the login page.
    """

    logger.debug(f'Attempt to deliver the login page, state: {state}.')

    if state == LOGIN_REDIRECT_STATE_CERTAIN:
        delete_access_token(request)
        return __login_response(request=request)

    # Prepares to check if this is an authenticated session.
    # access_token is None is not an error condition: user has not 
    # logged in before, just deliver the login HTML page.
    access_token = get_access_token(request)
    if access_token == None:
        return __login_response(request=request)
    
    data = await get_logged_in_user(request, access_token)
    if isinstance(data, HTTPException):
        delete_access_token(request)
        set_login_redirect_code(request, data.status_code)
        set_login_redirect_message(request, str(data))
        return __login_response(request=request)
    
    return RedirectResponse(url=router.url_path_for('home_page'))

@router.get("/home")
async def home_page(request: Request,
                    user = Depends(get_logged_in_user)) -> HTMLResponse:
    """
    HTML response: Return the home page.
    """

    logger.debug('Attempt to deliver the home page.')

    return templates.TemplateResponse(request=request, name="auth/home.html", 
                                      context={"title": HOME_PAGE_TITLE, 
                                               "data": {"user_number": user.emp_no, 
                                                        "user_scopes": user.scopes}})

@router.post("/token")
async def login(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    """
    Authenticate users.

    The response from this method can be in either ``JSON`` or 
    ``HTML`` format.

    - The default return format is ``HTML``.

    - If the request header ``x-expected-format`` is present and its value 
      is ``application/json``, then the return format is ``JSON``.

    When successfully logged in, depending on the requested return format:

    - ``HTML``: Returns the home page.

    - ``JSON``: Returns the following JSON: 
      ``{"access_token": <token>, "token_type": "bearer"}``.

    See ./tests/integration/test_auth_itgt.py for more details on possible 
    responses.
    """

    logger.debug('Attempt to log in...')

    async def bad_login(op_status: ResultStatus):
        # code 500: invalid email value or password value or database retrieval failed.
        # code 401: email or password does not match.
        match op_status.code:
            case status.HTTP_401_UNAUTHORIZED: message = INVALID_USERNAME_PASSWORD_MSG
            case status.HTTP_500_INTERNAL_SERVER_ERROR: message = BAD_LOGIN_MSG
            case _: message = LOGIN_ERROR_MSG

        set_login_redirect_code(request, op_status.code)
        set_login_redirect_message(request, message)

        if await html_req(request):
            return RedirectResponse(url=f"{router.url_path_for('login_page')}?state={LOGIN_REDIRECT_STATE_CERTAIN}", 
                                    status_code=status.HTTP_303_SEE_OTHER)        
        else:
            # return make_status(code=status.HTTP_400_BAD_REQUEST, text=message).as_dict()
            return make_status(code=op_status.code, text=message).as_dict()

    # Check if the session is authenticated and is still valid.
    access_token = get_access_token(request)
    if access_token != None:
        data = await get_logged_in_user(request, access_token)

        if isinstance(data, LoggedInEmployee):
            return RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER) \
                if await html_req(request) else \
                    make_status().add_data(
                        vars(Token(access_token=request.session["access_token"], 
                                   token_type="bearer", detail=LOGGED_IN_SESSION_MSG))
                    ).as_dict()
    
    op_status = EmployeesManager().login(form_data.username, form_data.password)

    if op_status.code != status.HTTP_200_OK:
        return await bad_login(op_status)
    
    access_token = create_access_token(data={'sub': op_status.data[0]['email'],
                                             'emp_no': op_status.data[0]['emp_no'],
                                             'scopes': op_status.data.scopes})

    set_access_token(request, access_token)

    return RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER) \
        if await html_req(request) else \
            make_status().add_data(
                vars(Token(access_token=access_token, token_type="bearer", detail=""))
            ).as_dict()

@router.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """
    Logs out and redirects to the login route ``/auth/login``.
    """

    def __clean_session(request: Request):
        delete_login_redirect_code(request)
        delete_login_redirect_message(request)
        delete_access_token(request)

    logger.debug('Attempt to log out...')

    set_login_redirect_message(request, NOT_LOGGED_IN_SESSION_MSG) \
        if no_access_token(request) else __clean_session(request)

    return RedirectResponse(url=f"{router.url_path_for('login_page')}?state={LOGIN_REDIRECT_STATE_CERTAIN}",
                            status_code=status.HTTP_303_SEE_OTHER)

#=================================== /api ==================================

@api_router.post("/login")
async def login_api(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    """
    This endpoint is equivalent to ``/auth/token``, with the incoming request 
    header ``x-expected-format`` set to ``application/json``.

    For documentation, please refer to the method [login](docs#/Auth/login_auth_token_post).
    """

    return await login(request, form_data)
