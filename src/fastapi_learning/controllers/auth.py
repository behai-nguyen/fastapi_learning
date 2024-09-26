"""
14/05/2024.
"""

from typing import (
    Annotated,
    Union,
)

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
)

from bh_apistatus.result_status import ResultStatus

from fastapi_learning import Token

from fastapi_learning.businesses.employees_mgr import EmployeesManager

from fastapi_learning.controllers import (
    is_logged_in,
    templates,
)

from fastapi_learning.common.jwt_utils import create_access_token

from fastapi_learning.common.consts import (
    LOGIN_PAGE_TITLE,
    HOME_PAGE_TITLE,
    LOGIN_ERROR_MSG,
    BAD_LOGIN_MSG,
    INVALID_USERNAME_PASSWORD_MSG,
    NOT_LOGGED_IN_SESSION_MSG,
    LOG_IN_CONTINUE_MSG,
    LOGGED_IN_SESSION_MSG,
)

from fastapi_learning.common.queue_logging import logger

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

def __login_page_context(state: int) -> dict:
    context = {"title": LOGIN_PAGE_TITLE}
    match state:
        case 1: context.update({"message": NOT_LOGGED_IN_SESSION_MSG})
        case 2: context.update({"message": LOG_IN_CONTINUE_MSG})
        # case 3: context.update({"message": INVALID_USERNAME_PASSWORD_MSG})
        case status.HTTP_401_UNAUTHORIZED: context.update({"message": INVALID_USERNAME_PASSWORD_MSG})
        case status.HTTP_500_INTERNAL_SERVER_ERROR: context.update({"message": BAD_LOGIN_MSG})
        case _: pass

    return context

def __login_page(request: Request, state: int=0) -> HTMLResponse: 
    logger.debug('Delivering the login page.')

    return templates.TemplateResponse(request=request, 
                name="auth/login.html", context=__login_page_context(state))

def __home_page(request: Request) -> HTMLResponse: 
    logger.debug('Delivering the home page.')

    return templates.TemplateResponse(request=request, 
                name="auth/home.html", context={"title": HOME_PAGE_TITLE})

@router.get("/login", response_model=None)
async def login_page(request: Request, state: int = 0) -> HTMLResponse:
    logger.debug('Attempt to deliver the login page.')

    return RedirectResponse(url=router.url_path_for('home_page')) \
        if is_logged_in(request) \
        else __login_page(request=request, state=state)

@router.get("/home", response_model=None)
async def home_page(request: Request) -> HTMLResponse:
    logger.debug('Attempt to deliver the home page.')

    return RedirectResponse(url=f"{router.url_path_for('login_page')}?state=2") \
        if not is_logged_in(request) \
        else __home_page(request=request)

@router.post("/token")
async def login(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Union[Token, None]:

    """
    The response from this method can be in either ``JSON`` or 
    ``HTML`` format.

    - The default return format is ``HTML``.

    - If the request header ``x-expected-format`` is present and its value 
      is ``application/json``, then the return format is ``JSON``.

    When successfully logged in, depending on the requested return format:

    - ``HTML``: Returns the home page.

    - ``JSON``: Returns the following JSON: 
      ``{"access_token": <token>, "token_type": "bearer"}``.

    There are two possible failure conditions:

    - Invalid username: The submitted username does not match any in 
      the database.

    - Invalid password: The submitted password does not match the password 
      in the database for the given username.

    When login fails, depending on the requested return format:

    - ``HTML``: The response ``status_code`` is ``HTTP_200_OK``. The 
      HTML text is the login page with the message ``INVALID_USERNAME_PASSWORD_MSG``.
    
    - ``JSON``: The response ``status_code`` is ``HTTP_400_BAD_REQUEST``. 
      The ``detail`` field value is ``INVALID_USERNAME_PASSWORD_MSG``.    
    """

    logger.debug('Attempt to log in...')

    async def bad_login(op_status: ResultStatus):
        # code 500: invalid email value or password value or database retrieval failed.
        # code 401: email or password does not match.
        match op_status.code:
            case status.HTTP_401_UNAUTHORIZED: message = INVALID_USERNAME_PASSWORD_MSG
            case status.HTTP_500_INTERNAL_SERVER_ERROR: message = BAD_LOGIN_MSG
            case _: message = LOGIN_ERROR_MSG

        if await html_req(request):
            return RedirectResponse(url=f"{router.url_path_for('login_page')}?state={op_status.code}", 
                                    status_code=status.HTTP_303_SEE_OTHER)        
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=message)

    if is_logged_in(request): 
        logger.debug(LOGGED_IN_SESSION_MSG)

        return RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER) \
            if await html_req(request) else \
                Token(access_token=request.session["access_token"], token_type="bearer", detail=LOGGED_IN_SESSION_MSG)

    op_status = EmployeesManager().login(form_data.username, form_data.password)

    if op_status.code != status.HTTP_200_OK:
        return await bad_login(op_status)
    
    access_token = create_access_token(data={"sub": op_status.data[0]['email']})

    request.session["access_token"] = access_token

    return RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER) \
        if await html_req(request) else Token(access_token=access_token, token_type="bearer", detail="")

@router.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """
    Logs out and redirects to the login route ``/auth/login``.

    There are two possible error conditions:

    - Not logged in: The users have not yet authenticated.

    - Invalid credentials: The requests contain an ``Authorization`` 
      header with an invalid token, such as ``Bearer behai_``.

    When an error occurs, the returned login page will contain the text 
    ``NOT_LOGGED_IN_SESSION_MSG``.
    """

    logger.debug('Attempt to log out...')

    inc_not_login_msg = 1 if request.session.get("access_token") == None else 0
    
    request.session.clear()
    
    return RedirectResponse(url=f"{router.url_path_for('login_page')}?state={inc_not_login_msg}",
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
