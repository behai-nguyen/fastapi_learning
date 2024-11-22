# 
# 14/11/2024.
# 
# Test employees related routes.
#
# Reference: https://stackoverflow.com/a/71428106
# 
# venv\Scripts\pytest.exe -m employees_itgt
# venv\Scripts\pytest.exe -k _integration_ -v
# 
# Use --capture=no to enable print output. I.e.:
# 
# venv\Scripts\pytest.exe -m employees_itgt --capture=no
# 

import importlib

from mimetypes import types_map

import pytest

from fastapi import status as http_status

from argon2 import PasswordHasher

from fastapi_learning.common.consts import (
    RESPONSE_FORMAT,
    INVALID_PERMISSIONS_MSG,
    DUPLICATE_EMAIL_MSG,
)

from fastapi_learning.businesses.employees_mgr import EmployeesManager

from tests import test_main

from tests import logout, login

from tests import delete_employee

@pytest.mark.employees_itgt
def test_integration_employees_search_form_invalid(test_client):
    """
    Test /emp/search path.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. User 'behai_nguyen@hotmail.com' does not have enough permissions 
        # to run employees search. 
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/emp/search')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/search.html page.
        assert ('<title>Learn FastAPI Search Employees</title>' in response.text) == True
        assert ('<h2 class="text-danger fw-bold">Not enough permissions</h2>' in response.text) == True
        assert ('<div class="col"><a href="/auth/home" class="link-primary"><h2>Home</h2></a></div>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_search_form_valid(test_client):
    """
    Test /emp/search path.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. User 'kyoichi.maliniak.10005@gmail.com' has enough permissions 
        # to run employees search. 
        login_response = login('kyoichi.maliniak.10005@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/emp/search')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/search.html page.
        assert ('<title>Learn FastAPI Search Employees</title>' in response.text) == True
        assert ('<input id="last_name" required placeholder="%nas%" value="%nas%" >' in response.text) == True
        assert ('<input id="first_name" required placeholder="%An" value="%An" >' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)        

@pytest.mark.employees_itgt
def test_integration_employees_search_result_html(test_client):
    """
    Test /emp/search/{partial-last-name}/{partial-first-name} path.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('kyoichi.maliniak.10005@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/emp/search/%nas%/%An')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin me.html page.
        assert ('<title>Learn FastAPI Search Employees</title>' in response.text) == True

        assert ('<div class="col-1">12483</div>' in response.text) == True
        assert ('<div class="col-3">Niranjan</div>' in response.text) == True
        assert ('<div class="col-2">1990-01-10</div>' in response.text) == True

        assert ('<div class="col-1">496044</div>' in response.text) == True
        assert ('<div class="col-3">Gopalakrishnan</div>' in response.text) == True
        assert ('<div class="col-2">1988-10-27</div>' in response.text) == True        

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_search_result_json(test_client):
    """
    Test /emp/search/{partial-last-name}/{partial-first-name} path.

    Return data:
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

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('kyoichi.maliniak.10005@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

        response = test_client.get('/emp/search/%nas%/%An')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        number_of_records = len(status['data'])
        assert number_of_records > 2

        record = status['data'][0]
        record["emp_no"] = 12483
        record["email"] = "niranjan.gornas.12483@gmail.com"
        record["password"] = "$argon2id$v=19$m=16,t=2,p=1$cTJhazRqRWRHR3NYbEJ2Zg$z7pMnKzV0eU5eJkdq+hycQ"
        record["birth_date"] = "19/10/1959"
        record["first_name"] = "Niranjan"
        record["last_name"] = "Gornas"
        record["gender"] = "M"
        record["hire_date"] = "10/01/1990"

        record = status['data'][number_of_records - 1]
        record["emp_no"] = 496044
        record["email"] = "gopalakrishnan.gornas.496044@gmail.com"
        record["password"] = "$argon2id$v=19$m=16,t=2,p=1$cTJhazRqRWRHR3NYbEJ2Zg$z7pMnKzV0eU5eJkdq+hycQ"
        record["birth_date"] = "26/05/1958"
        record["first_name"] = "Gopalakrishnan"
        record["last_name"] = "Gornas"
        record["gender"] = "M"
        record["hire_date"] = "27/10/1988"
    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_search_result_json_invalid(test_client):
    """
    Test /emp/search/{partial-last-name}/{partial-first-name} path.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. User 'behai_nguyen@hotmail.com' does not have enough permissions
        # to search employees.
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

        response = test_client.get('/emp/search/%nas%/%An')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert status['status']['text'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_own_get_update_html_invalid(test_client):
    """
    Test https://localhost:5000/emp/own-get-update/{logged-in-emp-no}

    Login with user 'kyoichi.maliniak.10005@gmail.com', whose employee
    number is 10005; and who has sufficient scopes 'admin:read' and 
    'admin:write' to perform the operation, which requires only 'user:write'.

    However, 'emp/own-get-update/{logged-in-emp-no}' only works for own
    employee number. 

    Calling update own details with a different employee number.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('kyoichi.maliniak.10005@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # User 'kyoichi.maliniak.10005@gmail.com', employee number is 10005.
        response = test_client.get('/emp/own-get-update/67010')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/update.html page.
        assert ('<title>Learn FastAPI Employees Maintenance</title>' in response.text) == True

        assert ('<h2 class="text-danger fw-bold">Not enough permissions</h2>' in response.text) == True
        assert ('<div class="col"><a href="/auth/home" class="link-primary"><h2>Home</h2></a></div>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_own_get_update_json_invalid(test_client):
    """
    Test https://localhost:5000/emp/own-get-update/{logged-in-emp-no}

    Login with user 'kyoichi.maliniak.10005@gmail.com', whose employee
    number is 10005; and who has sufficient scopes 'admin:read' and 
    'admin:write' to perform the operation, which requires only 'user:write'.

    However, 'emp/own-get-update/{logged-in-emp-no}' only works for own
    employee number. 

    Calling update own details with a different employee number.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('kyoichi.maliniak.10005@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

        # User 'kyoichi.maliniak.10005@gmail.com', employee number is 10005.
        response = test_client.get('/emp/own-get-update/67010')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert status['status']['text'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_own_get_update_html_valid(test_client):
    """
    Test https://localhost:5000/emp/own-get-update/{logged-in-emp-no}

    Login with user 'behai_nguyen@hotmail.com', whose employee number 
    is 500222; and who has sufficient scopes 'user:read' and 'user:write'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # User 'behai_nguyen@hotmail.com', employee number is 500222.
        response = test_client.get('/emp/own-get-update/500222')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/update.html page.
        assert ("<title>Learn FastAPI Employees Maintenance</title>" in response.text) == True

        assert ("empNo = 500222;" in response.text) == True
        assert ('<input name="empNo" id="empNo" readonly class="selector-input" >' in response.text) == True

        assert ("email = 'behai_nguyen@hotmail.com';" in response.text) == True
        assert ('<span id="email"></span>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_own_get_update_json_valid(test_client):
    """
    Test https://localhost:5000/emp/own-get-update/{logged-in-emp-no}

    Login with user 'behai_nguyen@hotmail.com', whose employee number 
    is 500222; and who has sufficient scopes 'user:read' and 'user:write'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

        response = test_client.get('/emp/own-get-update/500222')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        """
        {'status': {'code': 200, 'text': 'Data has been retrieved successfully.'}, 'data': [{'emp_no': 500222, 'email': 'behai_nguyen@hotmail.com', 'password': '$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA', 'birth_date': '09/12/1978', 'first_name': 'Be Hai', 'last_name': 'Nguyen', 'gender': 'M', 'hire_date': '08/10/2022'}]}
        """

        assert status['status']['code'] == http_status.HTTP_200_OK
        assert status['status']['text'] == 'Data has been retrieved successfully.'
        assert ('data' in status) == True

        data = status['data']
        assert len(data) == 1

        assert int(data[0]['emp_no']) == 500222
        assert data[0]['email'] == 'behai_nguyen@hotmail.com'
        assert PasswordHasher().verify(data[0]['password'], 'password') == True
        assert data[0]['birth_date'] == '09/12/1978'
        assert data[0]['first_name'] == 'Be Hai'
        assert data[0]['last_name'] == 'Nguyen'
        assert data[0]['gender'] == 'M'
        # assert data[0]['hire_date'] == '08/10/2022'
        assert len(data[0]['hire_date']) == 10

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_user_save_existing_invalid_01(test_client):
    """
    Test https://localhost:5000/emp/user-save

    Login with user 'nidapan.samarati.262556@gmail.com', who has only 'user:read' 
    scope, and attempts to updates their own detail, which requires 'user:write'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('nidapan.samarati.262556@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        user_data = {
            'empNo': 262556,
            'birthDate': '03/04/1953',
            'firstName': 'Nidapan',
            'lastName': 'Samarati',
            'gender': 'M',
            'hireDate': '25/10/1997',
        }

        response = test_client.post('/emp/user-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert status['status']['text'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_user_save_existing_invalid_02(test_client):
    """
    Test https://localhost:5000/emp/user-save

    Login with user 'behai_nguyen@hotmail.com', employee/user number is 500222, 
    and whose scopes are 'user:read' and 'user:write', which are sufficient to 
    update their own details only.
    
    Attempt to update another employee details, i.e., for post update data, 'empNo' 
    param is a value other than 500222.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        user_data = {
            'empNo': 491111,
            'birthDate': '09/12/1978',
            'firstName': 'Be Hai',
            'lastName': 'Nguyen',
            'gender': 'M',
            'hireDate': '18/1/2018',
        }

        response = test_client.post('/emp/user-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert status['status']['text'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_user_save_existing_valid(test_client):
    """
    Test https://localhost:5000/emp/user-save

    Login with user 'behai_nguyen@hotmail.com', whose scopes are 'user:read' 
    and 'user:write', which are sufficient to update their own details.
    
    Updates hire date to '18/1/2018'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        user_data = {
            'empNo': 500222,
            'birthDate': '09/12/1978',
            'firstName': 'Be Hai',
            'lastName': 'Nguyen',
            'gender': 'M',
            'hireDate': '18/1/2018',
        }

        response = test_client.post('/emp/user-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None
        
        status = EmployeesManager().select_by_employee_number(500222).as_dict()

        """
        {'status': {'code': 200, 'text': 'Data has been retrieved successfully.'}, 'data': [{'emp_no': 500222, 'email': 'behai_nguyen@hotmail.com', 'password': '$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA', 'birth_date': '09/12/1978', 'first_name': 'Be Hai', 'last_name': 'Nguyen', 'gender': 'M', 'hire_date': '18/01/2018'}]}
        """

        assert status['status']['code'] == http_status.HTTP_200_OK
        assert status['status']['text'] == 'Data has been retrieved successfully.'
        assert ('data' in status) == True

        data = status['data']
        assert len(data) == 1

        assert data[0]['email'] == 'behai_nguyen@hotmail.com'
        assert data[0]['hire_date'] == '18/01/2018'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_get_update_html_invalid(test_client):
    """
    Test https://localhost:5000/emp/admin-get-update/{emp-no}

    Login with user 'behai_nguyen@hotmail.com', who has only 'user:read' 
    and 'user:write', which are not enough for the endpoint method
    permission, which is 'admin:read'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/emp/admin-get-update/67010')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/update.html page.
        assert ('<title>Learn FastAPI Employees Maintenance</title>' in response.text) == True

        assert ('<h2 class="text-danger fw-bold">Not enough permissions</h2>' in response.text) == True
        assert ('<div class="col"><a href="/auth/home" class="link-primary"><h2>Home</h2></a></div>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_get_update_json_invalid(test_client):
    """
    Test https://localhost:5000/emp/admin-get-update/{emp-no}

    Login with user 'behai_nguyen@hotmail.com', who has only 'user:read' 
    and 'user:write', which are not enough for the endpoint method
    permission, which is 'admin:read'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('behai_nguyen@hotmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

        response = test_client.get('/emp/admin-get-update/67010')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert status['status']['text'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_get_update_html_valid(test_client):
    """
    Test https://localhost:5000/emp/admin-get-update/{emp-no}

    Login with user 'kyoichi.maliniak.10005@gmail.com', who has sufficient 
    scopes 'admin:read' and 'admin:write' to perform the operation.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('kyoichi.maliniak.10005@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/emp/admin-get-update/500222')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/update.html page.
        assert ("<title>Learn FastAPI Employees Maintenance</title>" in response.text) == True

        assert ("empNo = 500222;" in response.text) == True
        assert ('<input name="empNo" id="empNo" readonly class="selector-input" >' in response.text) == True

        assert ("email = 'behai_nguyen@hotmail.com';" in response.text) == True
        assert ('<span id="email"></span>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_get_update_json_valid(test_client):
    """
    Test https://localhost:5000/emp/admin-get-update/{emp-no}

    Login with super user 'mary.sluis.10011@gmail.com', who has 
    sufficient scopes to perform the operation.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('mary.sluis.10011@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        # Expect JSON response.
        test_client.headers = {RESPONSE_FORMAT: types_map['.json']}    

        response = test_client.get('/emp/admin-get-update/500222')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        """
        {'status': {'code': 200, 'text': 'Data has been retrieved successfully.'}, 'data': [{'emp_no': 500222, 'email': 'behai_nguyen@hotmail.com', 'password': '$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA', 'birth_date': '09/12/1978', 'first_name': 'Be Hai', 'last_name': 'Nguyen', 'gender': 'M', 'hire_date': '08/10/2022'}]}
        """

        assert status['status']['code'] == http_status.HTTP_200_OK
        assert status['status']['text'] == 'Data has been retrieved successfully.'
        assert ('data' in status) == True

        data = status['data']
        assert len(data) == 1

        assert int(data[0]['emp_no']) == 500222
        assert data[0]['email'] == 'behai_nguyen@hotmail.com'
        assert PasswordHasher().verify(data[0]['password'], 'password') == True
        assert data[0]['birth_date'] == '09/12/1978'
        assert data[0]['first_name'] == 'Be Hai'
        assert data[0]['last_name'] == 'Nguyen'
        assert data[0]['gender'] == 'M'
        # assert data[0]['hire_date'] == '08/10/2022'
        assert len(data[0]['hire_date']) == 10

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_save_existing_invalid_01(test_client):
    """
    Test https://localhost:5000/emp/admin-save

    Login with user 'weijing.showalter.67000@gmail.com', who has only 'admin:read' 
    scope, and attempts to update other's detail, which requires 'admin:write'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('weijing.showalter.67000@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        user_data = {
            'empNo': 262556,
            'birthDate': '03/04/1953',
            'firstName': 'Nidapan',
            'lastName': 'Samarati',
            'gender': 'M',
            'hireDate': '25/10/1997',
        }

        response = test_client.post('/emp/admin-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert status['status']['text'] == INVALID_PERMISSIONS_MSG

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_save_existing_valid(test_client):
    """
    Test https://localhost:5000/emp/admin-save

    Login with super user 'mary.sluis.10011@gmail.com' and updates other's details.
    
    Updates user 'behai_nguyen@hotmail.com''s hire date and check.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. 
        login_response = login('mary.sluis.10011@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        user_data = {
            'empNo': 500222,
            'birthDate': '09/12/1978',
            'firstName': 'Be Hai',
            'lastName': 'Nguyen',
            'gender': 'M',
            'hireDate': '18/1/2018',
        }

        response = test_client.post('/emp/admin-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None
        
        status = EmployeesManager().select_by_employee_number(500222).as_dict()

        """
        {'status': {'code': 200, 'text': 'Data has been retrieved successfully.'}, 'data': [{'emp_no': 500222, 'email': 'behai_nguyen@hotmail.com', 'password': '$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA', 'birth_date': '09/12/1978', 'first_name': 'Be Hai', 'last_name': 'Nguyen', 'gender': 'M', 'hire_date': '18/01/2018'}]}
        """

        assert status['status']['code'] == http_status.HTTP_200_OK
        assert status['status']['text'] == 'Data has been retrieved successfully.'
        assert ('data' in status) == True

        data = status['data']
        assert len(data) == 1

        assert data[0]['email'] == 'behai_nguyen@hotmail.com'
        assert data[0]['hire_date'] == '18/01/2018'

        #
        # Try update hire_date to '1/11/2022'.
        #

        user_data['hireDate'] = '1/11/2022'

        response = test_client.post('/emp/admin-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None
        
        status = EmployeesManager().select_by_employee_number(500222).as_dict()

        """
        {'status': {'code': 200, 'text': 'Data has been retrieved successfully.'}, 'data': [{'emp_no': 500222, 'email': 'behai_nguyen@hotmail.com', 'password': '$argon2id$v=19$m=16,t=2,p=1$b2szcWQ4a0tlTkFydUdOaw$7LX7WCYbItEMEwvH3yUxPA', 'birth_date': '09/12/1978', 'first_name': 'Be Hai', 'last_name': 'Nguyen', 'gender': 'M', 'hire_date': '01/11/2022'}]}
        """

        assert status['status']['code'] == http_status.HTTP_200_OK
        assert status['status']['text'] == 'Data has been retrieved successfully.'
        assert ('data' in status) == True

        data = status['data']
        assert len(data) == 1

        assert data[0]['email'] == 'behai_nguyen@hotmail.com'
        assert data[0]['hire_date'] == '01/11/2022'

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_new_form_invalid(test_client):
    """
    Test /emp/new path: form to create a new employee.
    
    User 'weijing.showalter.67000@gmail.com', scope 'admin:read' 
    only. Required scope 'admin:write'.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. User 'weijing.showalter.67000@gmail.com' has insufficient permissions.
        login_response = login('weijing.showalter.67000@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/emp/new')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/search.html page.
        assert ('<title>Learn FastAPI Employees Maintenance</title>' in response.text) == True
        assert ('<h2 class="text-danger fw-bold">Not enough permissions</h2>' in response.text) == True
        assert ('<div class="col"><a href="/auth/home" class="link-primary"><h2>Home</h2></a></div>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_new_form_valid(test_client):
    """
    Test /emp/new path: form to create a new employee.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        # Login. User 'kyoichi.maliniak.10005@gmail.com' has enough permissions.
        login_response = login('kyoichi.maliniak.10005@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        response = test_client.get('/emp/new')

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        # admin emp/search.html page.
        assert ('<title>Learn FastAPI Employees Maintenance</title>' in response.text) == True
        assert ("saveEmployee( '/emp/admin-save' );" in response.text) == True
        assert ('<input name="empNo" id="empNo" readonly class="selector-input" >' in response.text) == True
        assert ('<input name="email" id="email" required maxlength="255" class="selector-input col" >' in response.text) == True
        assert ('<input name="password" id="password" required maxlength="32" class="selector-input" >' in response.text) == True
        assert ('<button type="button" id="newEmpBtn" class="btn btn-primary btn-sm" data-url="emp/new" >New</button>' in response.text) == True

    finally:
        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_save_new_invalid_duplicate_email(test_client):
    """
    Test https://localhost:5000/emp/admin-save

    Login with super user 'mary.sluis.10011@gmail.com' and creates 
    new employee records.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        delete_employee('Do%', 'Be %')

        # Login. 
        login_response = login('mary.sluis.10011@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        user_data = {
            'empNo': '',
            'email': 'behai_nguyen@hotmail.com',
            'password': ',[(/V(w8#);("KG5~$',
            'birthDate': '09/12/1978',
            'firstName': 'Be Hai',
            'lastName': 'Doe',
            'gender': 'M',
            'hireDate': '18/1/2018',
        }

        response = test_client.post('/emp/admin-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None
        """
            {
                "status": {
                    "code": 500,
                    "text": ""
                },
                "data": {
                    "errors": [
                        {
                            "id": "email",
                            "label": "Email",
                            "errors": [
                                "Can't accept this email. Please specify another"
                            ]
                        }
                    ]
                }
            }
        """
        
        assert status['status']['code'] == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        assert ('data' in status) == True
        assert ('errors' in status['data']) == True
        assert len(status['data']['errors']) == 1
        
        error = status['data']['errors'][0]
        assert error['id'] == 'email'
        assert error['label'] == 'Email'
        assert len(error['errors']) == 1
        assert error['errors'][0] == DUPLICATE_EMAIL_MSG

    finally:
        delete_employee('Do%', 'Be %')

        # Logout. Clean up server sessions.
        logout(login_response, test_client)

@pytest.mark.employees_itgt
def test_integration_employees_admin_save_new_valid(test_client):
    """
    Test https://localhost:5000/emp/admin-save

    Login with super user 'mary.sluis.10011@gmail.com' and creates 
    new employee records.
    
    Test successfully write an employee record into database.

    Test includes:
        -- Writes a new employee into database.
        -- Reads this newly inserted record back and verify.
        -- Updates a some fields, and update the database.
        -- Reads the updated employee record back and verify.
        -- Note that updating ignores email and password.
    """

    importlib.reload(test_main)

    test_client.headers.clear()

    try:
        delete_employee('Do%', 'Be %')

        # Login. 
        login_response = login('mary.sluis.10011@gmail.com', 'password', test_client)

        # Set session (Id) for next request.
        session_cookie = login_response.cookies.get('session')
        test_client.cookies = {'session': session_cookie}

        TEST_EMAIL = 'behai_nguyen_1@hotmail.com'
        TEST_PASSWORD = ',[(/V(w8#);("KG5~$'
        
        user_data = {
            # 'empNo': '',
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
            'birthDate': '25/12/1971',
            'firstName': 'Be Hai',
            'lastName': 'Doe',
            'gender': 'M',
            'hireDate': '17/9/1975',
        }

        response = test_client.post('/emp/admin-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_200_OK
        assert ('data' in status) == True
        assert ('employees_new_list' in status['data']) == True
        assert ('employees_updated_list' in status['data']) == True

        # There is one (1) new record.
        # There is no updated record.
        assert len(status['data']['employees_new_list']) == 1
        assert len(status['data']['employees_updated_list']) == 0

        new_emp_no = status['data']['employees_new_list'][0]['emp_no']
        # 499999 is the last emp_no in the original test data.
        assert new_emp_no > 499999

        """
        Read the newly inserted employee back and verify data inserted.
        """
        status = EmployeesManager().select_by_employee_number(new_emp_no)
        
        assert status.code == http_status.HTTP_200_OK
        assert status.data != None
        assert len(status.data) == 1
        assert status.data[0]['emp_no'] == new_emp_no
        assert status.data[0]['email'] == TEST_EMAIL
        assert PasswordHasher().verify(status.data[0]['password'], TEST_PASSWORD)
        assert status.data[0]['birth_date'] == '25/12/1971'
        assert status.data[0]['first_name'] == 'Be Hai'
        assert status.data[0]['last_name'] == 'Doe'
        assert status.data[0]['gender'] == 'M'
        # Note: THERE IS LEADING 0 in single digit day, month.
        assert status.data[0]['hire_date'] == '17/09/1975'

        """
        Update the just inserted employee:
            - set Gender to F
            - set Hire Date to 11/8/2005
        """
        user_data['empNo'] = new_emp_no
        user_data['gender'] = 'F'
        user_data['hireDate'] = '11/8/2005'

        response = test_client.post('/emp/admin-save', data=user_data)

        assert response != None
        assert response.status_code == http_status.HTTP_200_OK

        status = response.json()
        assert status != None

        assert status['status']['code'] == http_status.HTTP_200_OK
        assert ('data' in status) == True
        assert ('employees_new_list' in status['data']) == True
        assert ('employees_updated_list' in status['data']) == True

        # There is no new record.
        # There is one (1) updated record.
        assert len(status['data']['employees_new_list']) == 0
        assert len(status['data']['employees_updated_list']) == 1

        """
        Read the newly updated employee back and verify data updated.
        """
        status = EmployeesManager().select_by_employee_number(new_emp_no)
        
        assert status.code == http_status.HTTP_200_OK
        assert status.data != None
        assert len(status.data) == 1

        assert status.data[0]['emp_no'] == new_emp_no
        assert status.data[0]['email'] == TEST_EMAIL
        assert PasswordHasher().verify(status.data[0]['password'], TEST_PASSWORD)        
        assert status.data[0]['birth_date'] == '25/12/1971'
        assert status.data[0]['first_name'] == 'Be Hai'
        assert status.data[0]['last_name'] == 'Doe'
        assert status.data[0]['gender'] == 'F'
        assert status.data[0]['hire_date'] == '11/08/2005'
        
    finally:
        delete_employee('Do%', 'Be %')

        # Logout. Clean up server sessions.
        logout(login_response, test_client)