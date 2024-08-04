"""
Test Employees model: i.e. "employees" table.

venv\Scripts\pytest.exe -m employees
venv\Scripts\pytest.exe -k _unit_ -v

Use --capture=no to enable print output. I.e.:

venv\Scripts\pytest.exe -m employees --capture=no
"""

import pytest

from http import HTTPStatus

from argon2 import PasswordHasher

from fastapi_learning.models.employees import Employees

@pytest.mark.employees
def test_unit_select_by_email(app):
    """
    Dates are in Australian format.

    status = {
        "status": {
            "code": 200,
            "text": "Data has been retrieved successfully."
        },
        "data": [
            {
                "emp_no": 10153,
                "email": "heekeun.majewski.10153@gmail.com",
                "password": "$argon2id$v=19$m=16,t=2,p=1$cTJhazRqRWRHR3NYbEJ2Zg$z7pMnKzV0eU5eJkdq+hycQ",
                "birth_date": "15/12/1955",
                "first_name": "Heekeun",
                "last_name": "Majewski",
                "gender": "M",
                "hire_date": "08/04/1987"
            }
        ]
    }    
    """
    employees = Employees()

    status = employees.select_by_email('heekeun.majewski.10153@gmail.com')

    assert status.code == HTTPStatus.OK.value
    assert len(status.text) > 0
    assert status.data != None
    assert len(status.data) == 1

    assert status.data[0]['emp_no'] == 10153
    assert PasswordHasher().verify(status.data[0]['password'], 'password') == True
    assert status.data[0]['birth_date'] == '15/12/1955'
    assert status.data[0]['first_name'] == 'Heekeun'
    assert status.data[0]['last_name'] == 'Majewski'
    assert status.data[0]['gender'] == 'M'
    assert status.data[0]['hire_date'] == '08/04/1987'

    status_dict = status.as_dict()
    assert status_dict['status']['code'] == HTTPStatus.OK.value
    assert len( status_dict['status']['text'] ) > 0
    assert status_dict['data'][0]['emp_no'] == 10153
    assert PasswordHasher().verify(status_dict['data'][0]['password'], 'password') == True
    assert status_dict['data'][0]['birth_date'] == '15/12/1955'
    assert status_dict['data'][0]['first_name'] == 'Heekeun'
    assert status_dict['data'][0]['last_name'] == 'Majewski'
    assert status_dict['data'][0]['gender'] == 'M'
    assert status_dict['data'][0]['hire_date'] == '08/04/1987'

@pytest.mark.employees
def test_unit_select_by_email_not_found(app):
    """
    status = {
        "status": {
            "code": 200,
            "text": "No data for the selection criteria."
        }
    }    
    """
    employees = Employees()

    status = employees.select_by_email('test@examplemail.com')

    assert status.code == HTTPStatus.OK.value
    assert len(status.text) > 0

    assert getattr(status, 'data') == None
    assert status.data == None

    status_dict = status.as_dict()
    assert status_dict['status']['code'] == HTTPStatus.OK.value
    assert len( status_dict['status']['text'] ) > 0
    assert ('data' not in status_dict) == True

