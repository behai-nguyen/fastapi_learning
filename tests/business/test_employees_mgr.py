
"""
Test EmployeesManager business component.

venv\Scripts\pytest.exe -m employees_mgr
venv\Scripts\pytest.exe -k _business_ -v

venv\Scripts\pytest.exe -k <test method name>
E.g.: 
    venv\Scripts\pytest.exe -k test_business_write_employee_invalid

Use --capture=no to enable print output. I.e.:

venv\Scripts\pytest.exe -m employees_mgr --capture=no
"""

import pytest

from http import HTTPStatus

from argon2 import PasswordHasher

from fastapi_learning.businesses.employees_validation import (
    WWW_EMAIL_MSG,
    EMAIL_MSG,
    PASSWORD_MSG,
    BIRTH_DATE_MSG,
    LAST_NAME_MSG,
    FIRST_NAME_MSG,
    GENDER_MSG,
    HIRE_DATE_MSG,
    HIRE_DATE_AFTER_BIRTH_DATE_MSG,    
)

from fastapi_learning.businesses.employees_mgr import EmployeesManager

from fastapi_learning.common.consts import (
    INVALID_USERNAME_PASSWORD_MSG,
    DUPLICATE_EMAIL_MSG,
)

from tests import delete_employee

@pytest.mark.employees_mgr
def test_business_select_by_email_invalid_1(app):
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
                    }
                ]
            }
        }
    """
    employees_mgr = EmployeesManager()

    status = employees_mgr.select_by_email('')

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value
    assert hasattr(status, 'data') == True
    assert status.data != None
    assert hasattr(status.data, 'errors') == True
    assert len(status.data.errors) == 1

    error = status.data.errors[ 0 ]
    assert error[ 'id' ] == 'email'
    assert error[ 'label' ] == 'Email'
    assert len(error[ 'errors' ]) == 2
    assert error[ 'errors' ][ 0 ] == WWW_EMAIL_MSG
    assert error[ 'errors' ][ 1 ] == EMAIL_MSG

@pytest.mark.employees_mgr
def test_business_select_by_email_invalid_2(app):
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
                            "Please enter a valid email address"
                        ]
                    }
                ]
            }
        }
    """
    employees_mgr = EmployeesManager()

    # heekeun.majewski.10153@gmail.com
    status = employees_mgr.select_by_email('.10153@gmail.com')

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value
    assert hasattr(status, 'data') == True
    assert status.data != None
    assert hasattr(status.data, 'errors') == True
    assert len(status.data.errors) == 1

    error = status.data.errors[ 0 ]
    assert error[ 'id' ] == 'email'
    assert error[ 'label' ] == 'Email'
    assert len(error[ 'errors' ]) == 1
    assert error[ 'errors' ][ 0 ] == EMAIL_MSG

@pytest.mark.employees_mgr
def test_business_select_by_email(app):
    """
        {
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
    employees_mgr = EmployeesManager()

    status = employees_mgr.select_by_email('heekeun.majewski.10153@gmail.com')

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

@pytest.mark.employees_mgr
def test_business_select_by_email_no_data(app):
    """
        {
            "status": {
                "code": 404,
                "text": "No employee matches submitted email"
            }
        }
    """
    employees_mgr = EmployeesManager()

    status = employees_mgr.select_by_email('spider_man@hotmail.com')

    assert status.code == HTTPStatus.NOT_FOUND.value
    assert len(status.text) > 0
    assert status.data == None

@pytest.mark.employees_mgr
def test_login_invalid_password(app):
    """
        {
            "status": {
                "code": 500,
                "text": ""
            },
            "data": {
                "errors": [
                    {
                        "id": "password",
                        "label": "Password",
                        "errors": [
                            "Please enter up to 32 characters"
                        ]
                    }
                ]
            }
        }
    """
    employees_mgr = EmployeesManager()

    status = employees_mgr.login('heekeun.majewski.10153@gmail.com', '')

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value
    assert hasattr(status, 'data') == True
    assert status.data != None
    assert hasattr(status.data, 'errors') == True
    assert len(status.data.errors) == 1

    error = status.data.errors[ 0 ]
    assert error[ 'id' ] == 'password'
    assert error[ 'label' ] == 'Password'
    assert len(error[ 'errors' ]) == 1
    assert error[ 'errors' ][ 0 ] == PASSWORD_MSG

@pytest.mark.employees_mgr
def test_login_email_no_match(app):
    """
        {
            "status": {
                "code": 401,
                "text": "Incorrect username or password"
            }
        }
    """
    employees_mgr = EmployeesManager()

    # heekeun.majewski.10153@gmail.com
    status = employees_mgr.login('majewski.10153@gmail.com', 'password')

    assert status.code == HTTPStatus.UNAUTHORIZED.value
    assert status.text == INVALID_USERNAME_PASSWORD_MSG

@pytest.mark.employees_mgr
def test_login_passwords_donot_match(app):
    """
        {
            "status": {
                "code": 401,
                "text": "Incorrect username or password"
            }
        }
    """
    employees_mgr = EmployeesManager()

    status = employees_mgr.login('heekeun.majewski.10153@gmail.com', 'passxxxxx')

    assert status.code == HTTPStatus.UNAUTHORIZED.value
    assert status.text == INVALID_USERNAME_PASSWORD_MSG

@pytest.mark.employees_mgr
def test_business_login_valid(app):    
    """
        {
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
    employees_mgr = EmployeesManager()

    status = employees_mgr.login('heekeun.majewski.10153@gmail.com', 'password')

    assert status.code == HTTPStatus.OK.value
    assert len(status.text) > 0
    assert status.data != None
    assert len(status.data) == 1

    assert status.data[0]['emp_no'] == 10153
    assert status.data[0]['birth_date'] == '15/12/1955'
    assert status.data[0]['first_name'] == 'Heekeun'
    assert status.data[0]['last_name'] == 'Majewski'
    assert status.data[0]['gender'] == 'M'
    assert status.data[0]['hire_date'] == '08/04/1987'

@pytest.mark.employees_mgr
def test_business_write_employee_invalid_data(app):
    """
    Test input data validation.
    """    
    employee = {}
    # This is a new record, we don't have to specify None for primary key.
    employee['empNo'] = None
    employee['email'] = ''
    employee['password'] = ''
    employee['birthDate'] = ''
    employee['firstName'] = ''
    employee['lastName'] = ''
    employee['gender'] = ''
    employee['hireDate'] = ''

    status = EmployeesManager().write_to_database(employee)

    # print("\nstatus.as_dict(): ", status.as_dict(), "\n")

    assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value
    assert hasattr(status, 'data') == True
    assert status.data != None
    assert hasattr(status.data, 'errors') == True
    assert len(status.data.errors) == 7

    error = status.data.errors[ 0 ]
    assert error[ 'id' ] == 'birth_date'
    assert error[ 'label' ] == 'Birth Date'
    assert len(error[ 'errors' ]) == 1
    assert error[ 'errors' ][ 0 ] == BIRTH_DATE_MSG

    error = status.data.errors[ 1 ]
    assert error[ 'errors' ][ 0 ] == FIRST_NAME_MSG

    error = status.data.errors[ 2 ]
    assert error[ 'errors' ][ 0 ] == LAST_NAME_MSG

    error = status.data.errors[ 3 ]
    assert error[ 'errors' ][ 0 ] == GENDER_MSG

    error = status.data.errors[ 4 ]
    assert error[ 'errors' ][ 0 ] == HIRE_DATE_MSG

    error = status.data.errors[ 5 ]
    assert error[ 'id' ] == 'email'
    assert error[ 'label' ] == 'Email'
    assert len(error[ 'errors' ]) == 2
    assert error[ 'errors' ][ 0 ] == WWW_EMAIL_MSG
    assert error[ 'errors' ][ 1 ] == EMAIL_MSG

    error = status.data.errors[ 6 ]
    assert error[ 'id' ] == 'password'
    assert error[ 'label' ] == 'Password'
    assert len(error[ 'errors' ]) == 1
    assert error[ 'errors' ][ 0 ] == PASSWORD_MSG

@pytest.mark.employees_mgr
def test_business_write_employee_invalid_hire_date(app):
    """
    Test input data validation.
    Hire date is before birth date: being hired before being born!
    """
    try:
        delete_employee('Do%', 'Be %')

        employee = {}
        # This is a new record, we don't have to specify None for primary key.
        # employee['empNo'] = None
        employee['email'] = 'behai_nguyen@hotmail.com'
        employee['password'] = ',[(/V(w8#);("KG5~$'
        employee['birthDate'] = '25/12/1971'
        employee['firstName'] = 'Be Hai'
        employee['lastName'] = 'Doe'
        employee['gender'] = 'M'
        # Note: there is no leading 0 in single digit day, month.
        employee['hireDate'] = '17/9/1967'

        status = EmployeesManager().write_to_database(employee)

        # print("\nstatus.as_dict(): ", status.as_dict(), "\n")

        assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value
        assert hasattr(status, 'data') == True
        assert status.data != None
        assert hasattr(status.data, 'errors') == True
        assert len(status.data.errors) == 1

        error = status.data.errors[ 0 ]
        assert error[ 'id' ] == 'hire_date'
        assert error[ 'label' ] == 'Hire Date'
        assert len(error[ 'errors' ]) == 1
        assert error[ 'errors' ][ 0 ] == HIRE_DATE_AFTER_BIRTH_DATE_MSG
    finally:
        delete_employee('Do%', 'Be %')

@pytest.mark.employees_mgr
def test_business_write_employee_invalid_duplicate_email(app):
    """
    Detects duplicate email.
    """
    try:
        delete_employee('Do%', 'Be %')

        employee = {}
        # This is a new record, we don't have to specify None for primary key.
        # employee['empNo'] = None
        employee['email'] = 'behai_nguyen@hotmail.com'
        employee['password'] = ',[(/V(w8#);("KG5~$'
        employee['birthDate'] = '25/12/1971'
        employee['firstName'] = 'Be Hai'
        employee['lastName'] = 'Doe'
        employee['gender'] = 'M'
        # Note: there is no leading 0 in single digit day, month.
        employee['hireDate'] = '17/9/2000'

        status = EmployeesManager().write_to_database(employee)

        # print("\nstatus.as_dict(): ", status.as_dict(), "\n")

        assert status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value
        assert hasattr(status, 'data') == True
        assert status.data != None
        assert hasattr(status.data, 'errors') == True
        assert len(status.data.errors) == 1

        error = status.data.errors[ 0 ]
        print(error)
        assert error[ 'id' ] == 'email'
        assert error[ 'label' ] == 'Email'
        assert len(error[ 'errors' ]) == 1
        assert error[ 'errors' ][ 0 ] == DUPLICATE_EMAIL_MSG

    finally:
        delete_employee('Do%', 'Be %')

@pytest.mark.employees_mgr
def test_business_write_employee(app):
    """
    Test successfully write an employee record into database.

    Test includes:
        -- Writes a new employee into database.
        -- Reads this newly inserted record back and verify.
        -- Updates a some fields, and update the database.
        -- Reads the updated employee record back and verify.
        -- Note that updating ignores email and password.
    """
    try:
        TEST_EMAIL = 'behai_nguyen_1@hotmail.com'
        TEST_PASSWORD = ',[(/V(w8#);("KG5~$'

        delete_employee('Do%', 'Be %')

        """
        Insert a new employee.
        """

        employee = {}
        # This is a new record, we don't have to specify None for primary key.
        # employee['empNo'] = None
        employee['email'] = TEST_EMAIL
        employee['password'] = TEST_PASSWORD
        employee['birthDate'] = '25/12/1971'
        employee['firstName'] = 'Be Hai'
        employee['lastName'] = 'Doe'
        employee['gender'] = 'M'
        # Started working at around 4 years and 3 months old!!!
        # Note: there is no leading 0 in single digit day, month.
        employee['hireDate'] = '17/9/1975'

        status = EmployeesManager().write_to_database(employee)

        # print("\nstatus.as_dict(): ", status.as_dict(), "\n")

        assert status.code == HTTPStatus.OK.value
        assert status.data != None
        assert hasattr(status.data, 'employees_new_list') == True
        assert hasattr(status.data, 'employees_updated_list') == True
        
        # There is one (1) new record.
        # There is no updated record.
        assert len(status.data.employees_new_list) == 1
        assert len(status.data.employees_updated_list) == 0

        new_emp_no = status.data.employees_new_list[0]['emp_no']
        # 499999 is the last emp_no in the original test data.
        assert new_emp_no > 499999

        """
        Read the newly inserted employee back and verify data inserted.
        """
        status = EmployeesManager().select_by_employee_number(new_emp_no)
        
        assert status.code == HTTPStatus.OK.value
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
        employee['empNo'] = new_emp_no
        employee['gender'] = 'F'
        employee['hireDate'] = '11/8/2005'

        status = EmployeesManager().write_to_database(employee)

        assert status.code == HTTPStatus.OK.value
        assert status.data != None
        assert hasattr(status.data, 'employees_new_list') == True
        assert hasattr(status.data, 'employees_updated_list') == True
        
        # There is no new record.
        # There is one (1) updated record.
        assert len(status.data.employees_new_list) == 0
        assert len(status.data.employees_updated_list) == 1

        """
        Read the newly updated employee back and verify data updated.
        """
        status = EmployeesManager().select_by_employee_number(new_emp_no)
        
        assert status.code == HTTPStatus.OK.value
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

@pytest.mark.employees_mgr
def test_business_write_employee_update(app):
    """
    Test successfully write an employee record into database.

    Test demonstrates: 'email' and 'password' don't get update on normal update.
    """
    try:
        TEST_EMAIL = 'behai_nguyen_1@hotmail.com'
        TEST_PASSWORD = ',[(/V(w8#);("KG5~$'

        delete_employee('Do%', 'Be %')

        """
        Insert a new employee.
        """

        employee = {}
        # This is a new record, we don't have to specify None for primary key.
        # employee['empNo'] = None
        employee['email'] = TEST_EMAIL
        employee['password'] = TEST_PASSWORD
        employee['birthDate'] = '25/12/1971'
        employee['firstName'] = 'Be Hai'
        employee['lastName'] = 'Doe'
        employee['gender'] = 'M'
        # Started working at around 4 years and 3 months old!!!
        # Note: there is no leading 0 in single digit day, month.
        employee['hireDate'] = '17/9/1975'

        status = EmployeesManager().write_to_database(employee)

        # Already test on the above test method.

        new_emp_no = status.data.employees_new_list[0]['emp_no']

        """
        Update the just inserted employee:
            - set Gender to F
            - set Hire Date to 11/8/2005
        """
        employee['empNo'] = new_emp_no
        employee['gender'] = 'F'
        employee['hireDate'] = '11/8/2005'

        # ATTEMPT TO UPDATE EMAIL AND PASSWORD: SHOULD NOT TAKE EFFECT.
        employee['email'] = 'behai_nguyen_1@hotmail.com'
        employee['password'] = 'password'

        status = EmployeesManager().write_to_database(employee)

        assert status.code == HTTPStatus.OK.value
        assert status.data != None
        assert hasattr(status.data, 'employees_new_list') == True
        assert hasattr(status.data, 'employees_updated_list') == True
        
        # There is no new record.
        # There is one (1) updated record.
        assert len(status.data.employees_new_list) == 0
        assert len(status.data.employees_updated_list) == 1

        """
        Read the newly updated employee back and verify data updated.
        """
        status = EmployeesManager().select_by_employee_number(new_emp_no)
        
        assert status.code == HTTPStatus.OK.value
        assert status.data != None
        assert len(status.data) == 1

        assert status.data[0]['emp_no'] == new_emp_no

        # 'email' and 'password' DON'T GET UPDATE ON NORMAL UPDATE.
        assert status.data[0]['email'] == TEST_EMAIL
        assert PasswordHasher().verify(status.data[0]['password'], TEST_PASSWORD)

        assert status.data[0]['birth_date'] == '25/12/1971'
        assert status.data[0]['first_name'] == 'Be Hai'
        assert status.data[0]['last_name'] == 'Doe'
        assert status.data[0]['gender'] == 'F'
        assert status.data[0]['hire_date'] == '11/08/2005'

    finally:
        delete_employee('Do%', 'Be %')