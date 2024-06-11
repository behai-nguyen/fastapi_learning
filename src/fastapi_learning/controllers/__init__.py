"""
14/05/2024.
"""

from typing import Callable, Tuple

from mimetypes import types_map
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response

from fastapi.routing import APIRoute

from fastapi_learning.common.consts import FORMAT_HEADER

templates = Jinja2Templates(directory="src/fastapi_learning/templates")

def json_req(request: Request):
    if FORMAT_HEADER in request.headers:
        if request.headers[FORMAT_HEADER] == types_map['.json']:
            return True

    return False

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
            json_header: Tuple[bytes] = FORMAT_HEADER.encode(), types_map['.json'].encode()
            request.headers.__dict__["_list"].append(json_header)

            return await original_route_handler(request)
                
        return custom_route_handler