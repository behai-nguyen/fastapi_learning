"""
14/05/2024.
"""

from typing import Callable, Tuple

from mimetypes import types_map

from fastapi.templating import Jinja2Templates
from fastapi import Request, Response

from fastapi.routing import APIRoute

from fastapi_learning.common.consts import RESPONSE_FORMAT

def valid_logged_in_employee(data: dict):
    """
    Used by templates. See ./templates/admin/me.html.
    """

    if 'email' in data:
        return True
    return False

templates = Jinja2Templates(directory="src/fastapi_learning/templates")
# Added functions to be used by templates.
# 
templates.env.globals['valid_logged_in_employee'] = valid_logged_in_employee

def json_req(request: Request):
    if RESPONSE_FORMAT in request.headers:
        if request.headers[RESPONSE_FORMAT] == types_map['.json']:
            return True

    return False

async def html_req(request: Request):
    """
    References: 
        https://stackoverflow.com/a/64910954
        https://stackoverflow.com/a/76971147
    """
    if RESPONSE_FORMAT in request.headers:
        if request.headers[RESPONSE_FORMAT] == types_map['.html']:
            return True

    form_data = await request.form()
    return form_data.get(RESPONSE_FORMAT) == types_map['.html']

def is_logged_in(request: Request) -> bool:
    """
    Is the current session authenticated?
    """
    return request.session.get("access_token") != None

class JsonAPIRoute(APIRoute):
    """
    Adds header 'x-expected-format' with value 'application/json'
    to the incoming request before send it to the endpoint.

    Official documentation:
        https://fastapi.tiangolo.com/how-to/custom-request-and-route/
        Custom Request and APIRoute class

    And also in this thread: https://github.com/tiangolo/fastapi/issues/2727
        See answer https://github.com/tiangolo/fastapi/issues/2727#issuecomment-770202019        
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            json_header: Tuple[bytes] = RESPONSE_FORMAT.encode(), types_map['.json'].encode()
            request.headers.__dict__["_list"].append(json_header)

            return await original_route_handler(request)
                
        return custom_route_handler