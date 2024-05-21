"""
14/05/2024.
"""

from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends,     
    HTTPException, 
    status,
)

from fastapi_learning import oauth2_scheme

from fastapi_learning.models.employees import (
    User,
    fake_decode_token,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

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
    return current_user

@router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
