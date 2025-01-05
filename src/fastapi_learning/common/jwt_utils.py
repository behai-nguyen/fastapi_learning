"""
14/09/2024.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError

from fastapi_learning import TokenData
from fastapi_learning.common.consts import INVALID_CREDENTIALS_MSG

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
                seconds=int(os.environ.get('ACCESS_TOKEN_EXPIRE_SECONDS'))
            )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get('SECRET_KEY'), 
                             algorithm=os.environ.get('ALGORITHM'))
    return encoded_jwt

def decode_access_token(token: str, verify_exp: bool=True) -> Union[TokenData, HTTPException]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=INVALID_CREDENTIALS_MSG,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY'), 
                             algorithms=[os.environ.get('ALGORITHM')],
                             options={'verify_exp': verify_exp})
        
        username: str = payload.get("sub")
        if username is None:
            return credentials_exception
        
        usernumber: int = int(payload.get("emp_no")) if 'emp_no' in payload else None
        if usernumber is None:
            return credentials_exception
        
        return TokenData(user_name=username, user_number=usernumber, 
                         scopes=payload.get("scopes", []), session_id=payload.get("session_id"))

    except InvalidTokenError:
        return credentials_exception
