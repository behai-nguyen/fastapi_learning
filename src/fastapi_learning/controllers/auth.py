"""
14/05/2024.
"""

from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Request,
    Response,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse

from starsessions import load_session

from fastapi_learning.models.employees import (
    UserInDB,
    fake_users_db, 
    fake_hash_password,
)

from fastapi_learning.controllers import templates

from fastapi_learning.common.consts import (
    LOGIN_PAGE_TITLE,
    INVALID_USERNAME_PASSWORD_MSG,
    NOT_LOGGED_IN_SESSION_MSG,
    LOGGED_IN_SESSION_MSG,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

def __login_page_context(inc_not_login_msg=False):
    context = {"title": LOGIN_PAGE_TITLE}
    if inc_not_login_msg:
        context.update({"message": NOT_LOGGED_IN_SESSION_MSG})

    return context

def __is_logged_in(request: Request) -> bool:
    return request.session.get("access_token") != None

@router.get("/login", response_model=None)
async def login_form(request: Request) -> Response | dict:

    return {"message": LOGGED_IN_SESSION_MSG} if __is_logged_in(request) \
        else templates.TemplateResponse(request=request, 
                name="auth/login.html", context=__login_page_context()) \

@router.post("/token")
async def login(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    if __is_logged_in(request): 
        return {"message": LOGGED_IN_SESSION_MSG}

    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail=INVALID_USERNAME_PASSWORD_MSG)
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail=INVALID_USERNAME_PASSWORD_MSG)
    
    request.session["access_token"] = user.username

    return {"access_token": user.username, "token_type": "bearer"}

@router.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    
    context = __login_page_context(
        inc_not_login_msg=request.session.get("access_token")==None)
    
    request.session.clear()
    
    return templates.TemplateResponse(request=request, name="auth/login.html", context=context)
