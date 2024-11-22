"""
29/07/2024.

Business components should be (web) framework neutral.

Employees implementations: validating submitted data, managing CRUD on 
validated data, etc.
"""

from http import HTTPStatus

from argon2 import PasswordHasher

from bh_database.constant import BH_RECORD_STATUS_MODIFIED

from bh_apistatus.result_status import (
    ResultStatus,
    make_500_status,
    make_status,
    clone_status,
)

from bh_database.constant import BH_REC_STATUS_FIELDNAME

from bh_utils.date_funcs import australian_date_to_iso_datetime

from .app_business import AppBusiness

from fastapi_learning.common.queue_logging import logger

from fastapi_learning.models.employees import Employees

from .base_validation import validate
from .employees_validation import (
    SearchByEmailForm,
    LoginForm,
    SearchByNameForm,
    UpdateEmployeeForm,
    AddEmployeeForm,
)

from fastapi_learning.common.consts import (
    EMAIL_NO_MATCHING_MSG,
    INVALID_USERNAME_PASSWORD_MSG,
    ERR_INVALID_SEARCH_EMP_NUMBER_MSG,
    DUPLICATE_EMAIL_MSG,
)

# Proper implementation might turn this into a database table.
MOCK_USER_SCOPES = [
    {
        'user_name': '*', 
        'scopes': ['user:read']
    },
    {
        'user_name': 'moss.shanbhogue.10045@gmail.com',
        'scopes': []
    },
    {
        'user_name': 'behai_nguyen@hotmail.com', 
        'scopes': ['user:read', 'user:write']
    },    
    {
        'user_name': 'nidapan.samarati.262556@gmail.com', 
        'scopes': ['user:read']
    },
    {
        'user_name': 'kyoichi.maliniak.10005@gmail.com', 
        'scopes': ['admin:read', 'admin:write']
    },    
    {
        'user_name': 'weijing.showalter.67000@gmail.com', 
        'scopes': ['admin:read']
    },
    {
        'user_name': 'mary.sluis.10011@gmail.com', 
        'scopes': ['super:*']
    }
]

def mock_get_user_scopes(email: str) -> list:
    res = [item for item in MOCK_USER_SCOPES if item['user_name'] == email]

    return res[0]['scopes'] if len(res) > 0 else \
        [item for item in MOCK_USER_SCOPES if item['user_name'] == '*'][0]['scopes']

class EmployeesManager(AppBusiness):
    """    
    Validate submitted data.
    Carry out CRUD operations on Employees table.

    self.__employee_data: data dictionary which presents an employee 
        record, read to be written into database.
    """

    def __init__(self):
        super().__init__()
        self.__employee_data = None

    def select_by_email(self, email: str) -> ResultStatus:
        """
        Returned codes are: 200, 404 or 500.
        """
        
        try:
            # Validate that email is a syntactically valid.
            search_data = {'email': email}
            status = validate(search_data, [SearchByEmailForm])
            if (status.code != HTTPStatus.OK.value): return status

            #
            # TO_DO: in this revision of the code, we just assume that the logged 
            # in user is querying themselves, we don't YET implement any access 
            # privilege checking. We will do that in a future revision:
            #
            # if email is not the logged in email then
            #     if has no access privilege to view others' data then
            #         raise unauthorised access exception.
            #

            status = Employees().select_by_email(email)

            if (status.code != HTTPStatus.OK.value): return status

            # No record matches submitted email: return error status.
            if status.data == None:
                logger().debug('No employee matched submitted email.')

                return make_status(code=HTTPStatus.NOT_FOUND.value, 
                                   text=EMAIL_NO_MATCHING_MSG)

            return status

        except Exception as e:
            logger().exception(str(e))
            return make_500_status(str(e))

    def select_by_partial_last_name_and_first_name(self, 
            last_name: str, first_name: str) -> ResultStatus:        
        try:
            search_data = {'last_name': last_name, 'first_name': first_name}
            status = validate(search_data, [SearchByNameForm])
            if (status.code != HTTPStatus.OK.value): return status

            return Employees().select_by_partial_last_name_and_first_name(
                last_name, first_name)

        except Exception as e:
            logger.exception(str(e))
            return make_500_status(str(e))
        
    def select_by_employee_number(self, emp_no: int) -> ResultStatus:
        try:
            # 10001 is from the database.
            if emp_no < 10001:
                return make_500_status(ERR_INVALID_SEARCH_EMP_NUMBER_MSG)

            return Employees().select_by_employee_number(emp_no)

        except Exception as e:
            logger.exception(str(e))
            return make_500_status(str(e))
                
    def login(self, email: str, password: str) -> ResultStatus:
        """
        Returned codes are: 200, 401 or 500.
        """

        try:
            logger().debug('Enter...')

            # Validate login data.
            search_data = {'email': email, 'password': password}
            status = validate(search_data, [LoginForm])
            # status.code == 500.
            if (status.code != HTTPStatus.OK.value): return status

            logger().debug('Passed data validation.')

            # Retrieve based on email.
            status = Employees().select_by_email(email)

            logger().debug('Finished searching employees by email. Code: {}'.format(status.code))

            # In error. Return immediately.
            if status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value: return status

            # No record matches submitted email: return error status.
            if status.code == HTTPStatus.NOT_FOUND.value:
                return make_status(code=HTTPStatus.UNAUTHORIZED.value, 
                                   text=INVALID_USERNAME_PASSWORD_MSG)
            
            # Passwords don't match: return error status.            
            try:
                PasswordHasher().verify(status.data[0]['password'], password)
            except Exception as e:
                logger().debug(str(e))

                return make_status(code=HTTPStatus.UNAUTHORIZED.value, 
                                   text=INVALID_USERNAME_PASSWORD_MSG)
            
            # raise Exception("Test login exception!")

            status = status.add_data(mock_get_user_scopes(email), 'scopes')

            """ 
            # The status dictionary variable can be dumped out using the 
            # code below.
            from bh_utils.json_funcs import dumps
            f = open( 'test.json', 'w' )
            f.write( dumps(status.as_dict()) )
            f.close()
            """

            # Return retrieved and match employee.
            return status
            
        except Exception as e:
            logger().exception(str(e))
            return make_500_status(str(e))
        
        finally:
            logger().debug('Exited.')

    def _preprocess_write_data(self):
        """ Override. 
        
        Prepares self.__employee_data, a proper employee dictionary 
        from the submitted data stored in self._write_data. The data 
        in self.__employee_data gets written to the database.

        Return:

        A ready-to-write dictionary which represents a single employee.        
        """

        self.__employee_data = {}
        self._param_to_record(self.__employee_data, 'empNo', 'emp_no')        
        self._param_to_record(self.__employee_data, 'email', 'email')
        self._param_to_record(self.__employee_data, 'password', 'password')
        self._param_to_record(self.__employee_data, 'birthDate', 'birth_date')
        self._param_to_record(self.__employee_data, 'firstName', 'first_name')
        self._param_to_record(self.__employee_data, 'lastName', 'last_name')
        self._param_to_record(self.__employee_data, 'gender', 'gender')
        self._param_to_record(self.__employee_data, 'hireDate', 'hire_date')
        # This field indicates whether this is an updated employee or a new 
        # employee.
        self.__employee_data[BH_REC_STATUS_FIELDNAME] = self._get_rec_status('empNo')

        return super()._preprocess_write_data()

    def _validate(self):
        """ Override. 

        Applies basic validation on input data.

        Then for a new record, verify that email is unique. Note there is no database 
        constraint for unique email.

        For existing records, i.e. write update, ignore 'email' and 'password' columns.
        That is, 'email' and 'password' columns don't get update on normal update.

        For new records, inserting, employee number can be blank, None or absent, 
        'email' and 'password' must have values.

        For existing records, updating, employee number must have value, 'email' and 
        'password' can be absent.
        """

        def __make_error(err_msg: str) -> ResultStatus:
            error = {"id": 'email', "label": 'Email', "errors": [err_msg]}
            return make_500_status('').add_data([error], name='errors')
        
        # Select appropriate validation form.
        validation_form, existing_emp = (UpdateEmployeeForm, True) if \
            self.__employee_data[BH_REC_STATUS_FIELDNAME] == BH_RECORD_STATUS_MODIFIED \
            else (AddEmployeeForm, False)
        
        # Note: 'birth_date' and 'hire_date' are in Australian 
        # date format. That is, dd/mm/yyyy.
        status = validate(self.__employee_data, [validation_form])
        # Fails basic input data validations. Proceeds no further.
        if status.code == HTTPStatus.INTERNAL_SERVER_ERROR.value: return status

        # For write update, i.e., updating an existing employee, ignore 'email' 
        # and 'password' columns.
        if existing_emp: return status

        # Retrieve based on email.
        status = Employees().count_by_email(self.__employee_data['email'])

        # Failed to count email. Return error status.
        if status.code != HTTPStatus.OK.value: return __make_error(status.text)

        # Duplicate email. Return error status.
        if status.data[0]['_count_'] > 0: return __make_error(DUPLICATE_EMAIL_MSG)

        # Successful.
        return make_status()

    def _pre_write(self):
        """ Override. """

        # Australian date to MySQL date.
        self.__employee_data['birth_date'] = australian_date_to_iso_datetime(self.__employee_data['birth_date'], False)
        self.__employee_data['hire_date'] = australian_date_to_iso_datetime(self.__employee_data['hire_date'], False)

        # For write update, i.e., updating an existing employee, don't update 'email' 
        # and 'password' columns. 
        if self.__employee_data[BH_REC_STATUS_FIELDNAME] == BH_RECORD_STATUS_MODIFIED:
            self.__employee_data.pop('email', None)
            self.__employee_data.pop('password', None)
        else:
            self.__employee_data['password'] = PasswordHasher().hash(self.__employee_data['password'])

        return super()._pre_write()

    def _write(self):
        """ Override. 
        
        Return:
            On failure:
            {
                "status": {
                    "code": 500,
                    "text": "blah..."
                }
            }

            On successful:
            {
                "status": {
                    "code": 200,
                    "text": "Data has been saved successfully."
                },
                "data": {
                    "employees_new_list": [
                        {
                            "emp_no": 500218,
                            "birth_date": "1973-04-03",
                            "first_name": "Be Hai",
                            "last_name": "Doe",
                            "gender": "M",
                            "hire_date": "2024-04-12"
                        }
                    ],
                    "employees_updated_list": []
                }
            }

            - "employees_new_list" is populated if the written record was new.
            - ""employees_updated_list" is populated if the written record was updated.
        """

        logger().debug('Entered...')
        try:
            employee = Employees()

            employee.begin_transaction()

            # raise Exception('Test Exception...')

            status = employee.write_to_database([self.__employee_data])

            # Failed to write to {employee.__tablename__} table.
            if status.code != HTTPStatus.OK.value:
                self._write_last_result = status
                return

            # Successful.
            self._write_last_result = clone_status(status)

            # Attach two data fields "employees_new_list" and "employees_updated_list" 
            # to the return write result. These are single element lists. And one of
            # the two would empty.
            data_name = f"{employee.__tablename__}_new_list"
            self._write_last_result.add_data(getattr(status.data, data_name), data_name)

            data_name = f"{employee.__tablename__}_updated_list"
            self._write_last_result.add_data(getattr(status.data, data_name), data_name)

        except Exception as e:
            logger().exception(str(e))
            self._write_last_result = make_500_status(str(e))

        finally:
            employee.finalise_transaction(self._write_last_result)
            logger().debug('Exited.')
            return self._write_last_result
