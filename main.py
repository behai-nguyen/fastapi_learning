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
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

from starsessions import SessionAutoloadMiddleware, SessionMiddleware
from starsessions.stores.redis import RedisStore

from fastapi_learning.common.queue_logging import (
    logger,
    prepare_logging_and_start_listeners,
    logging_stop_listeners,
    RequestLoggingMiddleware,
)

from bh_database.core import Database

from fastapi_learning.controllers import (
    auth, 
    admin,
    employees_admin,
    set_login_redirect_code,
    set_login_redirect_message,
)

from fastapi_learning.controllers.required_login import RequiresLogin

prepare_logging_and_start_listeners()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger_fn = logger()

    logger_fn.info("fastapi_learning attempting to start...")

    Database.disconnect()

    # It is the responsibility of the caller to handle this exception.
    try:
        Database.connect(os.environ.get('SQLALCHEMY_DATABASE_URI'), 
                         os.environ.get('SQLALCHEMY_DATABASE_SCHEMA'))
    except Exception as e:
        logger_fn.exception(str(e))
        logger_fn.error('Attempt to terminate the application now.')
        # raise RuntimeError(...) flushes any pending loggings and 
        # also terminates the application.        
        raise RuntimeError('Failed to connect to the target database.')

    logger_fn.info("fastapi_learning startup complete.")

    yield

    logger_fn.info("fastapi_learning is shutting down...")
    logger_fn.info("Logging queue listener will stop listening...")

    logging_stop_listeners()

app = FastAPI(lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

load_dotenv( os.path.join(os.getcwd(), '.env') )

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")
app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=RedisStore(REDIS_URL), cookie_https_only=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('ALLOW_ORIGINS').split(', '),
    allow_credentials=os.environ.get('ALLOW_CREDENTIALS'),
    allow_methods=os.environ.get('ALLOW_METHODS').split(', '),
    allow_headers=os.environ.get('ALLOW_HEADERS').split(', '),
    max_age=os.environ.get('MAX_AGE'),
)

app.mount("/static", StaticFiles(directory="src/fastapi_learning/static"), name="static")

app.include_router(auth.router)
app.include_router(auth.api_router)
app.include_router(admin.router)
app.include_router(admin.api_router)
app.include_router(employees_admin.router)

@app.get("/", response_model=None)
async def index(request: Request) -> Response | dict:
    from fastapi_learning.controllers.auth import login_page
    return await login_page(request)

# Redirect to login using custom exception handlers.
# See https://stackoverflow.com/a/76887329
@app.exception_handler(RequiresLogin)
async def requires_login(request: Request, e: HTTPException):
    from fastapi_learning.common.consts import LOGIN_REDIRECT_STATE_CERTAIN

    set_login_redirect_code(request, e.status_code)
    set_login_redirect_message(request, e.detail)
    return RedirectResponse(url=f"/auth/login?state={LOGIN_REDIRECT_STATE_CERTAIN}")

#
# Remove the code block below to use the command:
#
#    (venv) <venv path> uvicorn main:app --host 0.0.0.0 --port 5000 --ssl-keyfile ./cert/key.pem --ssl-certfile ./cert/cert.pem
#
# The command to run with the below code block:
#
#    (venv) <venv path> python main.py
#
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, \
                ssl_keyfile="./cert/key.pem", ssl_certfile="./cert/cert.pem")
