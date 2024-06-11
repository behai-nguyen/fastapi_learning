"""
14/05/2024.
"""

from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

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
