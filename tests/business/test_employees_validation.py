"""
Test employees validation rules / forms.

venv\Scripts\pytest.exe -m employees_validation
venv\Scripts\pytest.exe -k _business_ -v

venv\Scripts\pytest.exe -k <test method name>
E.g.: 
    venv\Scripts\pytest.exe -k test_business_write_employee_invalid

Use --capture=no to enable print output. I.e.:

venv\Scripts\pytest.exe -m employees_validation --capture=no
"""

import pytest

from http import HTTPStatus

from fastapi_learning.businesses.base_validation import validate

from fastapi_learning.businesses.employees_validation import (
    AddEmployeeForm,
    WWW_EMAIL_MSG,
    EMAIL_MSG,
    PASSWORD_MSG,
    HIRE_DATE_AFTER_BIRTH_DATE_MSG,
    UpdateEmployeeForm,
    EMPLOYEE_NUMBER_MSG,
)

@pytest.mark.employees_validation
def test_business_add_employee_validation_invalid_01(app):
    """
    Test new employee: without email and password.
    """

    employee = {}
    # This is a new record, we don't have to specify None for primary key.
    # employee['emp_no'] = None

    # employee['email'] = 'behai_nguyen_1@hotmail.com'
    # employee['password'] = ',[(/V(w8#);("KG5~$'
    employee['email'] = None
    employee['password'] = ''

    employee['birth_date'] = '25/12/1971'
    employee['first_name'] = 'Be Hai'
    employee['last_name'] = 'Doe'
    employee['gender'] = 'M'
    # Started working at around 4 years and 3 months old!!!
    # Note: there is no leading 0 in single digit day, month.
    employee['hire_date'] = '17/9/1975'

    status = validate(employee, [AddEmployeeForm])

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert status.data != None
    assert status.data.errors != None

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
                            "Please enter up to 255 characters",
                            "Please enter a valid email address"
                        ]
                    },
                    {
                        "id": "password",
                        "label": "Password",
                        "errors": [
                            "Please enter between 10 and 32 characters"
                        ]
                    }
                ]
            }
        }    
    """

    assert len(status.data.errors) == 2

    error = status.data.errors[0]
    assert error['id'] == 'email'
    assert error['label'] == 'Email'
    assert error['errors'][0] == WWW_EMAIL_MSG
    assert error['errors'][1] == EMAIL_MSG

    error = status.data.errors[1]
    assert error['id'] == 'password'
    assert error['label'] == 'Password'
    assert error['errors'][0] == PASSWORD_MSG

@pytest.mark.employees_validation
def test_business_add_employee_validation_invalid_02(app):
    """
    Test new employee: hire date is before birth date.
    """

    employee = {}
    # This is a new record, we don't have to specify None for primary key.
    # employee['emp_no'] = None

    employee['email'] = 'behai_nguyen_1@hotmail.com'
    employee['password'] = ',[(/V(w8#);("KG5~$'
    employee['birth_date'] = '25/12/1971'
    employee['first_name'] = 'Be Hai'
    employee['last_name'] = 'Doe'
    employee['gender'] = 'M'
    # Started working before born!!!
    employee['hire_date'] = '17/9/1970'

    status = validate(employee, [AddEmployeeForm])

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert status.data != None
    assert status.data.errors != None

    assert len(status.data.errors) == 1

    error = status.data.errors[0]
    assert error['id'] == 'hire_date'
    assert error['label'] == 'Hire Date'
    assert error['errors'][0] == HIRE_DATE_AFTER_BIRTH_DATE_MSG

@pytest.mark.employees_validation
def test_business_add_employee_validation_invalid_03(app):
    """
    Test new employee: all fields are blank.
    """

    employee = {}
    # This is a new record, we don't have to specify None for primary key.
    # employee['emp_no'] = None

    employee['email'] = ''
    employee['password'] = ''
    employee['birth_date'] = ''
    employee['first_name'] = ''
    employee['last_name'] = ''
    employee['gender'] = ''
    employee['hire_date'] = ''

    status = validate(employee, [AddEmployeeForm])

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert status.data != None
    assert status.data.errors != None

    assert len(status.data.errors) == 7

@pytest.mark.employees_validation
def test_business_add_employee_validation_valid(app):
    """
    Test new employee: valid data.
    """

    employee = {}
    # This is a new record, we don't have to specify None for primary key.
    # employee['emp_no'] = None

    employee['email'] = 'behai_nguyen_1@hotmail.com'
    employee['password'] = ',[(/V(w8#);("KG5~$'
    employee['birth_date'] = '25/12/1971'
    employee['first_name'] = 'Be Hai'
    employee['last_name'] = 'Doe'
    employee['gender'] = 'M'
    employee['hire_date'] = '17/9/2000'

    status = validate(employee, [AddEmployeeForm])

    assert status.code == HTTPStatus.OK
    assert status.data == None

@pytest.mark.employees_validation
def test_business_update_employee_validation_invalid_01(app):
    """
    Test update employee: emp_no = None and emp_no = ''.
    """

    employee = {}

    employee['emp_no'] = None
    employee['birth_date'] = '25/12/1971'
    employee['first_name'] = 'Be Hai'
    employee['last_name'] = 'Doe'
    employee['gender'] = 'M'
    # Started working at around 4 years and 3 months old!!!
    # Note: there is no leading 0 in single digit day, month.
    employee['hire_date'] = '17/9/1975'

    status = validate(employee, [UpdateEmployeeForm])

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert status.data != None
    assert status.data.errors != None

    assert len(status.data.errors) == 1
    """
        {
            "status": {
                "code": 500,
                "text": ""
            },
            "data": {
                "errors": [
                    {
                        "id": "TypeError",
                        "label": "TypeError",
                        "errors": "int() argument must be a string, a bytes-like object or a real number, not 'NoneType'"
                    }
                ]
            }
        }
    """

    employee['emp_no'] = ''
    status = validate(employee, [UpdateEmployeeForm])

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert status.data != None
    assert status.data.errors != None

    assert len(status.data.errors) == 1    
    """
        {
            "status": {
                "code": 500,
                "text": ""
            },
            "data": {
                "errors": [
                    {
                        "id": "emp_no",
                        "label": "Employee Number",
                        "errors": [
                            "Missing employee number"
                        ]
                    }
                ]
            }
        }    
    """
    error = status.data.errors[0]
    assert error['id'] == 'emp_no'
    assert error['label'] == 'Employee Number'
    assert error['errors'][0] == EMPLOYEE_NUMBER_MSG

@pytest.mark.employees_validation
def test_business_update_employee_validation_invalid_02(app):
    """
    Test update employee: hire date is before birth date.
    """

    employee = {}

    employee['emp_no'] = 100020
    # employee['email'] = 'behai_nguyen_1@hotmail.com'
    # employee['password'] = ',[(/V(w8#);("KG5~$'
    employee['birth_date'] = '25/12/1971'
    employee['first_name'] = 'Be Hai'
    employee['last_name'] = 'Doe'
    employee['gender'] = 'M'
    # Started working before born!!!
    employee['hire_date'] = '17/9/1970'

    status = validate(employee, [UpdateEmployeeForm])

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert status.data != None
    assert status.data.errors != None

    assert len(status.data.errors) == 1

    error = status.data.errors[0]
    assert error['id'] == 'hire_date'
    assert error['label'] == 'Hire Date'
    assert error['errors'][0] == HIRE_DATE_AFTER_BIRTH_DATE_MSG

@pytest.mark.employees_validation
def test_business_update_employee_validation_invalid_03(app):
    """
    Test update employee: all fields are blank.
    """

    employee = {}
    # This is a new record, we don't have to specify None for primary key.
    
    employee['emp_no'] = ''
    employee['email'] = ''
    employee['password'] = ''
    employee['birth_date'] = ''
    employee['first_name'] = ''
    employee['last_name'] = ''
    employee['gender'] = ''
    employee['hire_date'] = ''

    status = validate(employee, [UpdateEmployeeForm])

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR

    assert status.data != None
    assert status.data.errors != None

    # 'email' and 'password' are ignored.
    assert len(status.data.errors) == 6

@pytest.mark.employees_validation
def test_business_update_employee_validation_valid(app):
    """
    Test update employee: valid data.
    """

    employee = {}
    
    employee['emp_no'] = 123411
    employee['birth_date'] = '25/12/1971'
    employee['first_name'] = 'Be Hai'
    employee['last_name'] = 'Doe'
    employee['gender'] = 'M'
    employee['hire_date'] = '17/9/2000'

    status = validate(employee, [UpdateEmployeeForm])

    assert status.code == HTTPStatus.OK
    assert status.data == None
