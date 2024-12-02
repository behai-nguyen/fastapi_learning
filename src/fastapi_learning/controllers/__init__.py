"""
14/05/2024.
"""

from typing import (
    Union, 
    Callable, 
    Tuple,
)

from mimetypes import types_map

from fastapi.templating import Jinja2Templates
from fastapi import (
    HTTPException, 
    status,
    Request, 
    Response,
)

from fastapi.security import SecurityScopes

from fastapi.routing import APIRoute

from fastapi_learning.common.queue_logging import logger
from fastapi_learning import TokenData
from fastapi_learning.common.consts import (
    NOT_AUTHENTICATED_MSG,
    RESPONSE_FORMAT,
)
from fastapi_learning.models.employees import LoggedInEmployee
from fastapi_learning.common.jwt_utils import decode_access_token
from fastapi_learning.common.scope_utils import has_required_permissions

logger = logger()

def valid_logged_in_employee(data: dict) -> bool:
    """
    Template method. 
    See ./templates/admin/me.html.
    """

    if 'email' in data:
        return True
    return False

def enable_no_scopes_ui() -> bool:
    """
    Template method. 
    Display UI elements which send requests to the server even though
    the logged in user does not have sufficient scopes to run the 
    endpoint handler methods.    
    """

    import os
    from bh_utils.conversions import str_to_bool

    return str_to_bool(os.environ.get('ENABLE_NO_SCOPES_UI'))

def get_ui_states(checked_scopes: list[str], assigned_scopes: list[str]) -> list[str]:
    """A UI state is 'disabled' or enabled (a blank string).

    :param list[str] checked_scopes: Input. A list of scopes whose UI states are to
        be determined.

    :param list[str] assigned_scopes: Input. Scopes which are assigned to the 
        logged-in user 

    :return: list of string whose values are 'disabled' or blank. The total number of 
        elements equal to the length of :param list[str] checked_scopes:.
    """

    if enable_no_scopes_ui(): 
        return ['' for x in range(len(checked_scopes))]
    
    res: list[str] = []
    for s in checked_scopes:
        res.append('') if has_required_permissions([s], assigned_scopes) else res.append('disabled')

    return res

async def verify_user_scopes(security_scopes: SecurityScopes, 
                             logged_in_user: LoggedInEmployee, 
                             failed_msg: str) -> tuple:
    """
    Check if users have scopes given the required scopes and user JWT.

    Return: 
        (bool, permissions checking result)
        (bool, [HTTPException | None])

        Only possible return values:

        (False, HTTPException)
        (True, None)
    """

    if not has_required_permissions(security_scopes.scopes, logged_in_user.scopes): 
        logger.debug(failed_msg)

        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        else:
            authenticate_value = "Bearer"

        exception = credentials_exception(authenticate_value=authenticate_value)
        exception.detail = failed_msg

        return (False, exception)
    
    return (True, None)

templates = Jinja2Templates(directory="src/fastapi_learning/templates")
# Added functions to be used by templates.
# 
templates.env.globals['valid_logged_in_employee'] = valid_logged_in_employee
templates.env.globals['enable_no_scopes_ui'] = enable_no_scopes_ui
templates.env.globals['get_ui_states'] = get_ui_states

def credentials_exception(detail: str=NOT_AUTHENTICATED_MSG, 
                          authenticate_value: str="Bearer") -> HTTPException:
    return HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = detail,
        headers = {"WWW-Authenticate": authenticate_value},
    )

def attempt_decoding_access_token(token: str) -> Union[TokenData, HTTPException]:
    # OAuth2PasswordBearer auto_error has been set to False. 
    # The return value is None instead of an HTTPException.
    # This is the same exception raised by OAuth2PasswordBearer. 
    # We are taking control of the authentication flow.    
    if token == None:
        exception = credentials_exception()
        logger.debug(exception.detail)
        return exception
    
    return decode_access_token(token)

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

def set_access_token(request: Request, token: str):
    request.session["access_token"] = token

def get_access_token(request: Request) -> Union[str | None]:
    return request.session.get("access_token")

def delete_access_token(request: Request):
    request.session.pop("access_token", None)

def no_access_token(request: Request) -> bool:
    return request.session.get("access_token") == None

def set_login_redirect_code(request: Request, code: int):
    request.session["login_redirect_code"] = code

def get_login_redirect_code(request: Request, delete_also: bool=False) -> int:
    code: int = int(request.session.get("login_redirect_code", status.HTTP_200_OK))
    if delete_also: request.session.pop("login_redirect_code", None)
    return code

def delete_login_redirect_code(request: Request):
    request.session.pop("login_redirect_code", None)

def set_login_redirect_message(request: Request, message: str):
    request.session["login_redirect_msg"] = message

def get_login_redirect_message(request: Request, delete_also: bool=False) -> str:
    msg: str = request.session.get("login_redirect_msg", "")
    if delete_also: request.session.pop("login_redirect_msg", None)
    return msg

def delete_login_redirect_message(request: Request):
    request.session.pop("login_redirect_msg", None)

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