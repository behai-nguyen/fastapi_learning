"""
14/05/2024.

Eventually it will be the "employees" table in "employees" MySQL 
test database by Oracle Corporation: https://github.com/datacharmer/test_db.

See also: 

1. https://github.com/behai-nguyen/bh_database/tree/main/examples/fastapir

2. https://behainguyen.wordpress.com/2024/01/14/rust-actix-web-endpoints-which-accept-both-application-x-www-form-urlencoded-and-application-json-content-types/#step-two-update-employees-table
"""

from typing import Union
from pydantic import BaseModel

from argon2 import PasswordHasher

class User(BaseModel):
    username: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None

class UserInDB(User):
    hashed_password: str

"""
Note on 'hashed_password' field value: it's Argon2 hashed version of 'password'.
It was hashed by https://argon2.online/, using "Argon2id".

The Python implementation of Argon2 is https://pypi.org/project/argon2-cffi/,
but we are not using this library yet.
"""
fake_users_db = {
    "behai_nguyen@hotmail.com": {
        "username": "behai_nguyen@hotmail.com",
        "first_name": "Be Hai",
        "last_name": "Doe",
        "hashed_password": "$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA",
    },
    "pranav.furedi.10198@gmail.com": {
        "username": "pranav.furedi.10198@gmail.com",
        "first_name": "Pranav",
        "last_name": "Furedi",
        "hashed_password": "$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA",
    },
}

def password_match(hashed_password, password: str):
    try:
        return PasswordHasher().verify(hashed_password, password)
    except:
        return False

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user
