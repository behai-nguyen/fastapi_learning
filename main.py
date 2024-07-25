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
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

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

from fastapi_learning.controllers import auth, admin

prepare_logging_and_start_listeners()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger().info("fastapi_learning startup complete.")

    yield

    logger().info("fastapi_learning is shutting down...")
    logger().info("Logging queue listener will stop listening...")

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

@app.get("/", response_model=None)
async def index(request: Request) -> Response | dict:
    from fastapi_learning.controllers.auth import login_page
    return await login_page(request)

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
