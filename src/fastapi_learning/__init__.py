"""
14/05/2024.
"""

from typing import Optional

from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

"""
Might have to define more when required.
"""
APP_SCOPES = {
    'user:read': 'Current logged in user can read their own information only.',
    'user:write': 'Current logged in user can update their own information only.',
    'admin:read': 'Current logged in user can read others\' information.',
    'admin:write': 'Current logged in user can update others\' information.',
    'super:*': 'Current logged in user has access to all functionalities.'
}

APP_SCOPE_DEPENDENCIES = [
    {
        'scope': 'user:read', 
        'included_scopes': []
    },
    {
        'scope': 'user:write', 
        'included_scopes': ['user:read']
    },
    {
        'scope': 'admin:read', 
        'included_scopes': ['user:read']
    },
    {
        'scope': 'admin:write', 
        'included_scopes': ['user:read', 'user:write', 'admin:read']
    },
    {
        'scope': 'super:*', 
        'included_scopes': ['user:read', 'user:write', 'admin:read', 'admin:write']
    }
]

class Token(BaseModel):
    access_token: str
    token_type: str
    detail: str

class TokenData(BaseModel):
    user_name: str | None = None
    scopes: list[str] = []

"""
When we create an instance of the OAuth2PasswordBearer class we pass 
in the tokenUrl parameter. This parameter contains the URL that the 
client (the frontend running in the user's browser) will use to send 
the username and password in order to get a token.

Here tokenUrl="token" refers to a relative URL token that we haven't 
created yet. As it's a relative URL, it's equivalent to ./token.
"""
class OAuth2PasswordBearerRedis(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:

        ret_value = request.session.get("access_token")

        if ret_value != None:
            return ret_value
    
        return await super().__call__(request)
    
oauth2_scheme = OAuth2PasswordBearerRedis(tokenUrl="/auth/token", auto_error=False)

# Pass in scopes=APP_SCOPES to list all scopes on 
# the Swagger Authorize screen.
# 
# oauth2_scheme = OAuth2PasswordBearerRedis(tokenUrl="/auth/token", 
#                                          auto_error=False,
#                                          scopes=APP_SCOPES)