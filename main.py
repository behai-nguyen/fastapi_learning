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

import os

from fastapi import FastAPI, Request, Response

from fastapi.staticfiles import StaticFiles

from starsessions import SessionAutoloadMiddleware, SessionMiddleware
from starsessions.stores.redis import RedisStore

from fastapi_learning.controllers import auth, admin

app = FastAPI()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")
app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=RedisStore(REDIS_URL), cookie_https_only=False)

app.mount("/static", StaticFiles(directory="src/fastapi_learning/static"), name="static")

app.include_router(auth.router)
app.include_router(auth.api_router)
app.include_router(admin.router)
app.include_router(admin.api_router)

@app.get("/", response_model=None)
async def index(request: Request) -> Response | dict:
    from fastapi_learning.controllers.auth import login_page
    return await login_page(request)
