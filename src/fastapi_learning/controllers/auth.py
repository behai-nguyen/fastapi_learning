"""
14/05/2024.
"""

from typing import Annotated

# from mimetypes import types_map

from urllib.parse import urlparse

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse,
)

from bh_apistatus.result_status import (
    ResultStatus, 
    make_status,
)

from fastapi_learning import (
    Token, 
    oauth2_scheme,
    TokenData, 
)

from fastapi_learning.models.employees import LoggedInEmployee
from fastapi_learning.businesses.employees_mgr import EmployeesManager

from fastapi_learning.controllers import (
    templates,
    json_req,
    set_access_token,
    get_access_token,
    delete_access_token,
    set_login_redirect_code,
    get_login_redirect_code,
    set_login_redirect_message,
    get_login_redirect_message,
    attempt_decoding_access_token,
    redis_server,
)

from fastapi_learning.common.jwt_utils import create_access_token

from fastapi_learning.common.consts import (
    RESPONSE_FORMAT,
    LOGIN_REDIRECT_STATE_CERTAIN,
    LOGIN_PAGE_TITLE,
    HOME_PAGE_TITLE,
    LOGIN_ERROR_MSG,
    BAD_LOGIN_MSG,
    INVALID_USERNAME_PASSWORD_MSG,
    NOT_LOGGED_IN_SESSION_MSG,
    LOGGED_IN_SESSION_MSG,
)

from fastapi_learning.common.queue_logging import logger

from fastapi_learning.controllers.required_login import (
    get_logged_in_user,
    delete_cached_logged_in_user,
)

from . import (
    html_req, 
    JsonAPIRoute,
)

logger = logger()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

api_router = APIRouter(route_class=JsonAPIRoute,
    prefix="/api",
    tags=["API"],
)

def __login_response(request: Request) -> HTMLResponse: 
    logger.debug('Delivering the login response.')

    code = get_login_redirect_code(request, delete_also=True)
    message = get_login_redirect_message(request, delete_also=True)

    # The login page request is ALWAYS HTML.
    # But there is only a single login redirect route, other JSON requests 
    # which require authenticated session also get redirected here when 
    # their sessions are not authenticated, hence has to respond in JSON.
    if json_req(request):
        return JSONResponse(make_status(code=code, text=message).as_dict())

    return templates.TemplateResponse(request=request, 
                name="auth/login.html", 
                context={"title": LOGIN_PAGE_TITLE, 
                         "message": message})

@router.get("/login")
async def login_page(request: Request, state: int = 0) -> HTMLResponse:
    """
    HTML response: Return the login page.
    """

    logger.debug(f'Attempt to deliver the login page, state: {state}.')

    if state == LOGIN_REDIRECT_STATE_CERTAIN:
        delete_access_token(request)
        return __login_response(request=request)

    # Prepares to check if this is an authenticated session.
    # access_token is None is not an error condition: user has not 
    # logged in before, just deliver the login HTML page.
    access_token = get_access_token(request)
    if access_token == None:
        return __login_response(request=request)
    
    data = await get_logged_in_user(request, access_token)
    if isinstance(data, HTTPException):
        delete_access_token(request)
        set_login_redirect_code(request, data.status_code)
        set_login_redirect_message(request, str(data))
        return __login_response(request=request)
    
    return RedirectResponse(url=router.url_path_for('home_page'))

@router.get("/home")
async def home_page(request: Request,
                    user = Depends(get_logged_in_user)) -> HTMLResponse:
    """
    HTML response: Return the home page.
    """

    logger.debug('Attempt to deliver the home page.')

    # Remove entry cached by get_logged_in_user(...)
    delete_cached_logged_in_user(request)

    return templates.TemplateResponse(request=request, name="auth/home.html", 
                                      context={"title": HOME_PAGE_TITLE, 
                                               "data": {"user_number": user.emp_no, 
                                                        "user_scopes": user.scopes}})

@router.get("/__internal")
async def __internal(request: Request):

    """ 
    FIXME: This is a work-around code. To be removed when there is a better 
        solution found.

    A 'private' endpoint.

    In endpoint /auth/token, the 'session' cookie is not yet available: This is the 
    main reason for this redirection. From experimentation, I have found that this 
    intermediate redirection step makes the 'session' cookie available.

    The value of the 'session' cookie is the session Id.

    In summary, the primary purpose of this 'private' endpoint is to incorporate 
    the session Id into the access token payload.
    """

    # print(f"Headers: {request.headers.__dict__}")
    # print(f"Header format: {request.headers.get(RESPONSE_FORMAT)}")

    #
    # FIXME! Clean up. Set by 
    #     async def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # before redirect to this method, so session Id is available.
    #
    request.session.pop('x-email', None)

    #
    # Protect the /auth/__internal endpoint: This route means to be "private"!
    # That is, if users type this full route onto browsers, they should get 
    # redirected to the login page.
    #
    http_referer = request.headers.get('referer') or request.headers.get('x-referer') \
                        or request.headers.get('host')
    invalid_referer = True
    
    if http_referer != None:
        parsed_url = urlparse(http_referer)
        # testserver: Pytest integration host header value.
        # x-referer: Custom header value set by GUI/CLI clients.
        if parsed_url.path in ['/', '/auth/token', '/api/login', '/auth/login', 
                               'testserver', 'desktopclient']: 
            invalid_referer = False

    # If the referer/host is not recognisation, then returns the login page.
    # (Note: The login page conditionally delivers the home page.)
    if (http_referer == None) or invalid_referer:
        return RedirectResponse(url=router.url_path_for('login_page'))

    # Gathers the required info to create the access token.
    s = str(request.cookies.get('x-scopes'))
    access_token = create_access_token(data={'sub': request.cookies.get('x-email'),
                                             'emp_no': int(request.cookies.get('x-emp-no')),
                                             'scopes': s.split('^') if len(s) > 0 else [],
                                             'session_id': request.cookies.get('session')})
    # Stores the access token.
    set_access_token(request, access_token)

    # Delivers the final response.
    response = RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER) \
        if await html_req(request) else \
            make_status().add_data(
                vars(Token(access_token=access_token, token_type="bearer", detail=""))
            ).as_dict()

    # Remove the temporary cookies.
    # For some test methods, the response object does not have method 
    # delete_cookie. I don't understand why nor did I look into it.
    if hasattr(response, 'delete_cookie'):
        response.delete_cookie('x-email')
        response.delete_cookie('x-emp-no')
        response.delete_cookie('x-scopes')
        response.delete_cookie('x-expected-format')
    return response
                
@router.post("/token")
@api_router.post("/login")
async def login(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    """
    Authenticate users.

    Implements both ``/auth/token`` and ``/api/login``. 
    
    For ``/auth/token``: The default return format depends on the value of 
    ``x-expected-format``.

    For ``/api/login``: The incoming request header ``x-expected-format`` set 
    to ``application/json``.

    The response from this method can be in either ``JSON`` or 
    ``HTML`` format.

    - The default return format is ``HTML``.

    - If the request header ``x-expected-format`` is present and its value 
      is ``application/json``, then the return format is ``JSON``.

    When successfully logged in, depending on the requested return format:

    - ``HTML``: Returns the home page.

    - ``JSON``: Returns the following JSON: 
      ``{"access_token": <token>, "token_type": "bearer"}``.

    See ./tests/integration/test_auth_itgt.py for more details on possible 
    responses.
    """

    logger.debug('Attempt to log in...')

    async def bad_login(op_status: ResultStatus):
        # code 500: invalid email value or password value or database retrieval failed.
        # code 401: email or password does not match.
        match op_status.code:
            case status.HTTP_401_UNAUTHORIZED: message = INVALID_USERNAME_PASSWORD_MSG
            case status.HTTP_500_INTERNAL_SERVER_ERROR: message = BAD_LOGIN_MSG
            case _: message = LOGIN_ERROR_MSG

        if await html_req(request):
            set_login_redirect_code(request, op_status.code)
            set_login_redirect_message(request, message)

            return RedirectResponse(url=f"{router.url_path_for('login_page')}?state={LOGIN_REDIRECT_STATE_CERTAIN}", 
                                    status_code=status.HTTP_303_SEE_OTHER)        
        else:
            return make_status(code=op_status.code, text=message).as_dict()

    # Check if the session is authenticated and is still valid.
    access_token = get_access_token(request)
    if access_token != None:
        data = await get_logged_in_user(request, access_token)

        if isinstance(data, LoggedInEmployee):
            return RedirectResponse(url=router.url_path_for('home_page'), status_code=status.HTTP_303_SEE_OTHER) \
                if await html_req(request) else \
                    make_status().add_data(
                        vars(Token(access_token=request.session["access_token"], 
                                   token_type="bearer", detail=LOGGED_IN_SESSION_MSG))
                    ).as_dict()
    
    op_status = EmployeesManager().login(form_data.username, form_data.password)

    if op_status.code != status.HTTP_200_OK:
        return await bad_login(op_status)

    # 
    # FIXME: HACK! This causes the 'session' cookie created, so that 
    #     async def __internal(request: Request): can access the session Id.
    #
    request.session['x-email'] = op_status.data[0]['email']

    fd = await request.form()
    response_format = fd.get(RESPONSE_FORMAT) or request.headers.get(RESPONSE_FORMAT)

    #
    # Setting up the temporary cookies which store required info so that the endpoint
    # method __internal(...) can create the access token.
    # 
    # FIXME: This another work-around. In async def __internal(...) the session Id is
    #     available, so that it can be incorporated into the access token payload.
    # 
    response = RedirectResponse(url=router.url_path_for('__internal'), status_code=status.HTTP_303_SEE_OTHER)
    # FIXME: I would prefer setting headers than cookies, but headers does not to work.
    # response.headers[RESPONSE_FORMAT] = response_format
    response.set_cookie(key=RESPONSE_FORMAT, value=response_format, httponly=True)
    response.set_cookie(key='x-email', value=op_status.data[0]['email'], httponly=True)
    response.set_cookie(key='x-emp-no', value=str(op_status.data[0]['emp_no']), httponly=True)
    response.set_cookie(key='x-scopes', value='^'.join(op_status.data.scopes), httponly=True)

    return response

@router.post("/logout", response_class=HTMLResponse)
@api_router.post("/logout", response_class=HTMLResponse)
async def logout(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Logs out and redirects to the login route ``/auth/login``.

    This endpoint works with both:

    * Browsers: The 'session' cookie, which is the session Id, is available.
        The access token is not required.

    * Non-browser clients: The access token is included in the request 
        'Authorization' header. The 'session' cookie is not available. 
        The session Id is then extracted from the access token payload.

    FIXME: The implementation contains work-around code. It should be 
        refactored later on.
    """

    logger.debug('Attempt to log out...')

    # Clients are browsers. That is, from application web pages.
    session_id = request.cookies.get('session')
    if session_id == None:
        # From other clients, such as Postman, desk top clients, etc.
        token_data = attempt_decoding_access_token(token, False)
        if isinstance(token_data, TokenData): session_id = token_data.session_id
        
    logger.debug(f"Session Id extracted from token: {session_id}")    

    auth_session: bool = False
    if session_id != None:
        # Clean up the session. 
        # FIXME: I don't know how to access the session middleware yet. 
        #    Going directly with Redis server is a work around.
        session_id = f"starsessions.{session_id}"

        # Does this session Id exist, currently?
        auth_session = session_id in redis_server.scan_iter(session_id)
        redis_server.delete(session_id)
    
    if not auth_session:
        set_login_redirect_message(request, NOT_LOGGED_IN_SESSION_MSG)
        logger.debug(NOT_LOGGED_IN_SESSION_MSG)

    return RedirectResponse(url=f"{router.url_path_for('login_page')}?state={LOGIN_REDIRECT_STATE_CERTAIN}",
                            status_code=status.HTTP_303_SEE_OTHER)    
