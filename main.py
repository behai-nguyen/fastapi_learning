# 26/04/2024.
#
# This code is from the official tutorial section:
#     https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/
#
# with some modifications.
# 
# To run:
#     (venv) <path to venv Scripts/bin>/uvicorn main:app --host 0.0.0.0 --port 5000
#
# To access Swagger UI:
#     http://localhost:5000/docs
#

from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

"""
Note on 'hashed_password' field value: it's Argon2 hashed version of 'password'.
It was hashed by https://argon2.online/.

The Python implementation of Argon2 is https://pypi.org/project/argon2-cffi/,
but we are not using this library yet.
"""
fake_users_db = {
    "behai_nguyen@hotmail.com": {
        "username": "behai_nguyen@hotmail.com",
        "first_name": "Be Hai",
        "last_name": "Doe",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
    "pranav.furedi.10198@gmail.com": {
        "username": "pranav.furedi.10198@gmail.com",
        "first_name": "Pranav",
        "last_name": "Furedi",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/fastapi_learning/static"), name="static")
templates = Jinja2Templates(directory="src/fastapi_learning/templates")

def fake_hash_password(password: str):
    return "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

"""
When we create an instance of the OAuth2PasswordBearer class we pass 
in the tokenUrl parameter. This parameter contains the URL that the 
client (the frontend running in the user's browser) will use to send 
the username and password in order to get a token.

Here tokenUrl="token" refers to a relative URL token that we haven't 
created yet. As it's a relative URL, it's equivalent to ./token.
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    # if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(request=request, 
        name="auth/login.html", context={"title": "FastAPI Login"})