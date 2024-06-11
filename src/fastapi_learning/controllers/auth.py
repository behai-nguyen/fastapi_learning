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
)

from fastapi_learning.models.employees import (
    UserInDB,
    fake_users_db, 
    password_match,
)

from fastapi_learning.controllers import templates

from fastapi_learning.common.consts import (
    LOGIN_PAGE_TITLE,
    HOME_PAGE_TITLE,
    INVALID_USERNAME_PASSWORD_MSG,
    NOT_LOGGED_IN_SESSION_MSG,
    ALREADY_LOGGED_IN_MSG,
    LOG_IN_CONTINUE_MSG,
    LOGGED_IN_SESSION_MSG,
)

from . import json_req, JsonAPIRoute

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
        case 3: context.update({"message": INVALID_USERNAME_PASSWORD_MSG})
        case _: pass

    return context

def __is_logged_in(request: Request) -> bool:
    return request.session.get("access_token") != None

def __login_page(request: Request, state: int=0) -> HTMLResponse: 
    return templates.TemplateResponse(request=request, 
                name="auth/login.html", context=__login_page_context(state))

def __home_page(request: Request) -> HTMLResponse: 
    return templates.TemplateResponse(request=request, 
                name="auth/home.html", context={"title": HOME_PAGE_TITLE})

@router.get("/login", response_model=None)
async def login_page(request: Request, state: int = 0) -> HTMLResponse:
    return RedirectResponse(url=router.url_path_for('home_page')) \
        if __is_logged_in(request) \
        else __login_page(request=request, state=state)

@router.get("/home", response_model=None)
async def home_page(request: Request) -> HTMLResponse:
    return RedirectResponse(url=f"{router.url_path_for('login_page')}?state=2") \
        if not __is_logged_in(request) \
        else __home_page(request=request)

@router.post("/token")
async def login(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

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

    def bad_login():
        if json_req(request):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=INVALID_USERNAME_PASSWORD_MSG)
        else:
            return RedirectResponse(url=f"{router.url_path_for('login_page')}?state=3", 
                                    status_code=status.HTTP_303_SEE_OTHER)

    if __is_logged_in(request): 
        return {"detail": LOGGED_IN_SESSION_MSG} if json_req(request) \
            else RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER)

    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        return bad_login()
    
    user = UserInDB(**user_dict)
    if not password_match(user.hashed_password, form_data.password):
        return bad_login()
    
    request.session["access_token"] = user.username

    return {"access_token": user.username, "token_type": "bearer"} \
        if json_req(request) \
        else RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER)

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
