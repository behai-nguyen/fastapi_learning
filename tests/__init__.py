# 
# 15/05/2024.
# 
# Tests helper functions.
# 

import os

from dotenv import load_dotenv

from http import HTTPStatus

from fastapi import Response
from fastapi.testclient import TestClient

from bh_database.core import Database

# 
# Note: import the main.py module so that conftest.py can
# import this, i.e. test_main.
# 
import main as test_main
from fastapi_learning.models.employees import Employees

load_dotenv( os.path.join(os.getcwd(), '.env') )

Database.disconnect()
Database.connect(os.environ.get('SQLALCHEMY_DATABASE_URI'), 
                    os.environ.get('SQLALCHEMY_DATABASE_SCHEMA'))

def logout(last_response: Response, test_client: TestClient):
    """
    Logout test session. HTTP server session deleted from the 
    session store.
    """

    session_cookie = last_response.cookies.get('session')
    test_client.cookies = {'session': session_cookie}
    test_client.post('/auth/logout')

def login(username: str, password: str,
          test_client: TestClient) -> Response:
    """
    Log in a test session.
    """

    login_data = {
        'username': username,
        'password': password
    }
    response = test_client.post(  
        '/auth/token', 
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    assert response != None
    assert response.status_code == HTTPStatus.OK.value
    
    return response

def delete_employee(partial_last_name: str, partial_first_name: str):
    Employees.begin_transaction(Employees)

    employees = Employees.session.query( Employees ).filter( 
        Employees.last_name.ilike(partial_last_name),
        Employees.first_name.ilike(partial_first_name)
    ).all()

    if ( employees != None ):
        for emp in employees:
            Employees.session.delete( emp )

    Employees.commit_transaction(Employees)