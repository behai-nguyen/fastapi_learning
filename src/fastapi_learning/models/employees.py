"""
14/05/2024.

Implements the "employees" table in the "employees" MySQL test database 
by the Oracle Corporation: https://github.com/datacharmer/test_db.

See also: 

1. https://github.com/behai-nguyen/bh_database/tree/main/examples/fastapir

2. https://behainguyen.wordpress.com/2024/01/14/rust-actix-web-endpoints-which-accept-both-application-x-www-form-urlencoded-and-application-json-content-types/#step-two-update-employees-table
"""

from pydantic import BaseModel

from sqlalchemy import (
    Column,
    Integer,
    Date,
    String,
)

from bh_apistatus.result_status import ResultStatus
from bh_database.base_table import WriteCapableTable

class Employees(WriteCapableTable):
    """
    Implements the 'employees' table.
    """
    
    __tablename__ = 'employees'

    emp_no = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    password = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    first_name = Column(String(14), nullable=False)
    last_name = Column(String(16), nullable=False)
    gender = Column(String(1), nullable=False)
    hire_date = Column(Date, nullable=False)

    def select_by_email(self, email: str) -> ResultStatus:
        """
        Note the usage of the single quotation marks '{0}': MySQL, PostgreSQL and
        MariaDB accept this. PostgreSQL rejects double quotation mark ("{0}").
        """
        return self.run_select_sql(
            "select * from employees where email = '{0}'".format(email), True)
    
class LoggedInEmployee(BaseModel):
    """
    See also https://docs.pydantic.dev/1.10/usage/models/. This is a Pydantic 
    implementation: a SQLAlchemy class for database model and Pydantic model
    for internal data representation.
    """
    email: str
    password: str
    birth_date: str
    first_name: str
    last_name: str
    gender: str
    hire_date: str
