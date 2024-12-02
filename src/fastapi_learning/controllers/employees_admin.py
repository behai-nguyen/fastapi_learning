"""
Application employees administration controller.

Implements the following new routes:

1. GET: https://0.0.0.0:5000/emp/search
   Returns HTML.

2. GET/POST: https://0.0.0.0:5000/emp/search/{partial-last-name}/{partial-first-name}
   Returns HTML or JSON.

3. GET: https://0.0.0.0:5000/emp/admin-get-update/{emp_no}
   Returns HTML or JSON.

4. GET: https://0.0.0.0:5000/emp/own-get-update/{emp_no}
   Returns HTML or JSON.

5. POST: https://0.0.0.0:5000/emp/admin-save
   Returns JSON.

6. POST: https://0.0.0.0:5000/emp/user-save
   Returns JSON.

7. GET: https://0.0.0.0:5000/emp/new
   Returns HTML.
"""
from typing import Annotated

from fastapi import (
    APIRouter, 
    Request, 
    Depends,
    Security,
)

from fastapi.security import SecurityScopes

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)

from bh_apistatus.result_status import make_500_status

from fastapi_learning.common.queue_logging import logger

from fastapi_learning.models.employees import LoggedInEmployee
from fastapi_learning.businesses.employees_mgr import EmployeesManager

from fastapi_learning.controllers import (
    templates,
    credentials_exception,
    verify_user_scopes,
)

from fastapi_learning.common.consts import (
    INVALID_PERMISSIONS_MSG,
    SEARCH_EMPLOYEES_PAGE_TITLE,
    EMPLOYEES_MAINTENANCE_PAGE_TITLE,
)

from fastapi_learning.controllers.required_login import (
    get_logged_in_user,
    get_cached_logged_in_user,
)

from . import json_req

logger = logger()

router = APIRouter(
    prefix="/emp",
    tags=["Employees"],
)

SEARCH_PAGE = "emp/search.html"
SEARCH_RESULT_PAGE = "emp/search_result.html"
UPDATE_PAGE = "emp/update.html"
INSERT_PAGE = "emp/insert.html"

async def do_search(request: Request,
                    last_name: str, first_name: str, 
                    security_scopes: SecurityScopes,
                    user: Annotated[LoggedInEmployee, Depends(get_cached_logged_in_user)]):
    """
    Attempts to search employees using partial last name and partial first name.

    Returned response can either be JSON or HTML. Default is HTML. 
    
    To get JSON response, set request 'x-expected-format' header to 'application/json'.

    If the requesting user does not have sufficient scopes (permissions) return an
    error response.

    Example of a successful JSON response:

        {
            "status": {
                "code": 200,
                "text": "Data has been retrieved successfully."
            },
            "data": [
                {
                    "emp_no": 12483,
                    "email": "niranjan.gornas.12483@gmail.com",
                    "password": "$argon2id$v=19$m=16,t=2,p=1$cTJhazRqRWRHR3NYbEJ2Zg$z7pMnKzV0eU5eJkdq+hycQ",
                    "birth_date": "19/10/1959",
                    "first_name": "Niranjan",
                    "last_name": "Gornas",
                    "gender": "M",
                    "hire_date": "10/01/1990"
                },
                ...
                {
                    "emp_no": 496044,
                    "email": "gopalakrishnan.gornas.496044@gmail.com",
                    "password": "$argon2id$v=19$m=16,t=2,p=1$cTJhazRqRWRHR3NYbEJ2Zg$z7pMnKzV0eU5eJkdq+hycQ",
                    "birth_date": "26/05/1958",
                    "first_name": "Gopalakrishnan",
                    "last_name": "Gornas",
                    "gender": "M",
                    "hire_date": "27/10/1988"
                }
            ]
        }
    """

    res, exception = await verify_user_scopes(security_scopes, user, INVALID_PERMISSIONS_MSG)
    if not res:
        if json_req(request): 
            return make_500_status(exception.detail).as_dict()
        else:
            return templates.TemplateResponse(request=request, name=SEARCH_RESULT_PAGE,
                                              context={"exception": exception,
                                                       "title": SEARCH_EMPLOYEES_PAGE_TITLE})
    status = EmployeesManager() \
        .select_by_partial_last_name_and_first_name(last_name, first_name)
    
    return status.as_dict() if json_req(request) else \
        templates.TemplateResponse(request=request, name=SEARCH_RESULT_PAGE,
                                   context={"status": status.as_dict(), 
                                            "data": {"user_scopes": user.scopes},
                                            "title": SEARCH_EMPLOYEES_PAGE_TITLE})

@router.post("/search/{last_name}/{first_name}")
@router.get("/search/{last_name}/{first_name}")
async def search(request: Request, last_name: str, first_name: str, 
                 user = Depends(get_logged_in_user),
                 response = Security(do_search, scopes=["admin:read"])):
    """ 
    Route: https://0.0.0.0:5000/emp/search/{partial-last-name}/{partial-first-name}

    For example: https://0.0.0.0:5000/emp/search/%nas%/%An
    """

    return response

async def get_employee_to_update(request: Request, emp_no: str, 
                                 security_scopes: SecurityScopes,
                                 user: Annotated[LoggedInEmployee, Depends(get_cached_logged_in_user)]):

    def __get_page_data(user: LoggedInEmployee) -> dict:
        res = {"user_scopes": user.scopes}

        res.update({"required_scopes": ["admin:write"], "save_url": "/emp/admin-save"}) \
            if 'admin:read' in security_scopes.scopes \
            else res.update({"required_scopes": ["user:write"], "save_url": "/emp/user-save"})
        
        return res
    
    res, exception = await verify_user_scopes(security_scopes, user, INVALID_PERMISSIONS_MSG)

    if not res:
        if json_req(request): 
            return make_500_status(exception.detail).as_dict()
        else:
            return templates.TemplateResponse(request=request, name=UPDATE_PAGE,
                                              context={"exception": exception,
                                                       "title": EMPLOYEES_MAINTENANCE_PAGE_TITLE})

    status = EmployeesManager().select_by_employee_number(int(emp_no))

    return status.as_dict() if json_req(request) else \
        templates.TemplateResponse(request=request, name=UPDATE_PAGE,
                                   context={"employee": status.serialise_data(),
                                            "data": __get_page_data(user),
                                            "title": EMPLOYEES_MAINTENANCE_PAGE_TITLE})

@router.get("/admin-get-update/{emp_no}")
async def admin_update(request: Request, emp_no: str,
                       user = Depends(get_logged_in_user),
                       response = Security(get_employee_to_update, scopes=["admin:read"])):
    """ 
    Route: https://0.0.0.0:5000/emp/admin-get-update/{emp_no}

    For example: https://0.0.0.0:5000/emp/admin-get-update/10399

    This method selects a record and returns it as either HTML or JSON, in preparation 
    for editing (updating). The most sufficient scope required for this method is 
    'admin:read'. 
    """

    return response

@router.get("/own-get-update/{emp_no}")
async def user_update(request: Request, emp_no: str,
                      user = Depends(get_logged_in_user),
                      response = Security(get_employee_to_update, scopes=["user:read"])):

    """ 
    Route: https://0.0.0.0:5000/emp/own-get-update/{logged-in-emp-no}

    For example: https://0.0.0.0:5000/emp/own-get-update/10399

    // This method selects the logged in user and returns it as either HTML or JSON, in 
    // preparation for editing (updating). The most sufficient scope required for this 
    // method is 'user:read', coupled with additional extra check for requesting employee
    // number matches the logged in employee number.
    """

    if user.emp_no != int(emp_no):
        if json_req(request): 
            return make_500_status(INVALID_PERMISSIONS_MSG).as_dict()
        else:            
            exception = credentials_exception(detail=INVALID_PERMISSIONS_MSG)
            return templates.TemplateResponse(request=request, name=UPDATE_PAGE,
                                              context={"exception": exception,
                                                       "title": EMPLOYEES_MAINTENANCE_PAGE_TITLE})
    return response

async def do_save(request: Request, 
                  security_scopes: SecurityScopes,
                  user: Annotated[LoggedInEmployee, Depends(get_cached_logged_in_user)]):
    
    res, exception = await verify_user_scopes(security_scopes, user, INVALID_PERMISSIONS_MSG)

    if not res:
        return make_500_status(exception.detail).as_dict()

    form = await request.form()    
    return EmployeesManager().write_to_database(form._dict).as_dict()
    
@router.post("/admin-save", response_class=JSONResponse)
async def admin_save(request: Request,
                     user = Depends(get_logged_in_user),
                     response = Security(do_save, scopes=["admin:write"])):
    
    """ 
    Route: https://0.0.0.0:5000/emp/admin-save

    This method is for users with 'admin:write' to write new employee records,
    or to update existing records.

    empNo can be blank, None or completely absent. Fields 'email' and 
    'password' must have values.
    """

    return response

@router.post("/user-save", response_class=JSONResponse)
async def user_save(request: Request,
                    user = Depends(get_logged_in_user),
                    response = Security(do_save, scopes=["user:write"])):
    
    """ 
    Route: https://0.0.0.0:5000/emp/user-save

    This method DEDICATE to handle logged in user UPDATES their own details. 
    Details don't include 'email' and 'password'.

    empNo must have a value. Fields 'email' and 'password' can be absent.
    """

    form = await request.form()
    if user.emp_no != int(form._dict['empNo']):
        return make_500_status(INVALID_PERMISSIONS_MSG).as_dict()    

    return response

async def get_employee_insert_form(request: Request, 
                                   security_scopes: SecurityScopes,
                                   user: Annotated[LoggedInEmployee, Depends(get_cached_logged_in_user)]):

    def __get_page_data(user: LoggedInEmployee) -> dict:
        return {"user_scopes": user.scopes, "save_url": "/emp/admin-save"}
    
    res, exception = await verify_user_scopes(security_scopes, user, INVALID_PERMISSIONS_MSG)
    if not res:
        return templates.TemplateResponse(request=request, name=INSERT_PAGE,
                                          context={"exception": exception,
                                                   "title": EMPLOYEES_MAINTENANCE_PAGE_TITLE})

    return templates.TemplateResponse(request=request, name=INSERT_PAGE,
                                      context={"data": __get_page_data(user),
                                               "title": EMPLOYEES_MAINTENANCE_PAGE_TITLE}) 

@router.get("/new", response_class=HTMLResponse)
async def new(request: Request, 
              user = Depends(get_logged_in_user),
              response = Security(get_employee_insert_form, scopes=["admin:write"])):
    """ 
    Route: https://0.0.0.0:5000/emp/new
    """

    return response

async def get_emp_search_form(request: Request,
                              security_scopes: SecurityScopes,
                              user: Annotated[LoggedInEmployee, Depends(get_cached_logged_in_user)]):
    
    _, exception = await verify_user_scopes(security_scopes, user, INVALID_PERMISSIONS_MSG)

    return templates.TemplateResponse(request=request, name=SEARCH_PAGE,
                                      context={"exception": exception, 
                                               "data": {"user_scopes": user.scopes},
                                               "title": SEARCH_EMPLOYEES_PAGE_TITLE})

@router.get('/search', response_class=HTMLResponse)
async def search_form(request: Request, 
                      user = Depends(get_logged_in_user),
                      response = Security(get_emp_search_form, scopes=["admin:read"])):
    """
    Route: https://0.0.0.0:5000/emp/search
    """

    return response