"""
29/07/2024.

Base Business Object.

Receiving submitted data, apply validations, query database, write to 
database etc.

Base Business Objects should be framework neutral: they should not reference any 
framework directly.

Base Business Objects can import framework-dependent modules directly, otherwise nothing 
is possible, if moved to a different framework, these framework-dependent modules would 
have to be re-written. 
"""

from http import HTTPStatus

from abc import (
    ABC,
    abstractmethod,
)

from bh_database.constant import (
    BH_RECORD_STATUS_NEW,
    BH_RECORD_STATUS_MODIFIED,
)

from fastapi_learning.common.queue_logging import logger

class BaseBusiness(ABC):
    """
    Base Business Object. Responsible for validating, applies additional processing
    to submitted data and writes data to databases.

    Protected Variables:

    self._type: Run-time info. The class type of the instance.

    self._write_data: set by def write_to_database(data) only. 
    Access by others. Do not expose this variable as a public property.

    self._write_last_result: the result returned by write_to_database(data).

    Set by any of these abstractmethod methods, which descendant must implement:
        def _validate(self), 
	    def _pre_write(self), 
        def _write(self),
        def _post_write(self)

    In most case, def _write(self) does the works, it is highly likely that 
    this method sets self._write_last_result most of the times.

    Descendant can set this variable in anyway it sees fits, ON ONE CONDITION,
    it must contains the following core snippet:

        {
            "status": {
            	"code": 9999,
            	"text": "... message text ..."
            }
        }    
    """

    def __init__(self):
        self._last_message = ''
        self._type = type(self)

        self._write_data = None
        self._write_last_result = None

    def get(self, key, source_data: dict, default=None, type=None):
        """Return the default value if the requested data doesn't exist.
        If `type` is provided and is a callable it should convert the value,
        return it or raise a :exc:`ValueError` if that is not possible.  In
        this case the function will return the default as if the value was not
        found:

        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.get('foo', type=int)
        42
        >>> d.get('bar', -1, type=int)
        -1

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key can't
                        be looked up.  If not further specified `None` is
                        returned.
        :param type: A callable that is used to cast the value in the
                    :class:`MultiDict`.  If a :exc:`ValueError` is raised
                    by this callable the default value is returned.
        """
        try:
            rv = source_data[key]
        except KeyError:
            return default
        if type is not None:
            try:
                rv = type(rv)
            except ValueError:
                rv = default
        return rv

    def _param_exists_with_value(self, param_name):
        """
        Checks if a param is present in self._write_data and if its string
        value has some data.

        Return:

        True -- if param exists and its has some value. False otherwise.
        """

        if param_name not in self._write_data: return False

        if self._write_data[ param_name ] == None: return False
        if len(str(self._write_data[param_name])) == 0: return False

        return True

    def _param_test_int_value(self, param_name, value: int):
        """
        Checks if a param is present in self._write_data and if its integer
        value equals a test value.

        Arguments:

        param_name: name of param to test for.

        value: test integer value.

        Return:

        True -- if param exists, and its integer value equals a test value. 
        False otherwise.
        """
        if param_name not in self._write_data: return False
        try:
            param_value = int(self._write_data[param_name])
        except:
            return False

        return param_value == value

    def _param_to_record(self, record, param_name, field_name, \
        reject_absent_param=True, default_absent_param_value='', reject_no_value=False):
        """
        Conditionally do this assignment:

            record[ field_name ] = self._write_data[ param_name ]

        and return True to indicate assignment took place. False otherwise.

        Arguments:

        record: a dictionary where to copy conditionally copy self._write_data[ param_name ]
        to record[ field_name ]. record represents a row in a database table.

        param_name, field_name: 1. param_name: a key in dicitonary self._write_data; 
        2. field_name: a key in record, this is a database table column name, where
        record is a row.

        reject_absent_param, default_absent_param_value: what to do when param_name does
        not exist in self._write_data.
        
            1. reject_absent_param: when True, do nothing, returns False to indicate no 
               copy took place. When False, copy with default_absent_param_value and 
               return True to indicate copy took place.

            2. default_absent_param_value: see (1) above.

        reject_no_value: what to do when param_name exists in self._write_data and
        its value is either null or blank.

            1. True, returns False to indicate no copy took place.

            2. False, accepts null or blank value, and returns True to indicate copy 
               took place.

        Return:

        True, False -- see arguments' documentation above.
        """
        if param_name not in self._write_data:
            if reject_absent_param: return False

            else:
                record[ field_name ] = default_absent_param_value
                return True

        if reject_no_value:
            if self._write_data[ param_name ] == None: return False
            if len(str(self._write_data[param_name])) == 0: return False

        record[ field_name ] = self._write_data[ param_name ]
        return True

    def _get_rec_status(self, id_key_name):
        """
        Determines if a submitted data represents a new row or an updated row.

        Arguments:

        id_key_name: a submitted param of a table primary key.

        If self._write_data[ id_key_name ] has a value, then the submitted data
        represents an updated row, a new row otherwise.

        Return:

        BH_RECORD_STATUS_NEW or BH_RECORD_STATUS_MODIFIED.
        """
        return BH_RECORD_STATUS_NEW if (id_key_name not in self._write_data \
                or self._write_data[id_key_name] == None or len(str(self._write_data[id_key_name])) == 0) \
                else BH_RECORD_STATUS_MODIFIED

    @abstractmethod
    def _preprocess_write_data(self):
        """
        Applies any preprocess requirements to self._write_data.

        Return:

        Core snippet:

            {
            	"status": {
            		"code": 9999,
            		"text": "... message text ..."
            	}
            }

        Descendant method is freed to add any additional data as required.
        """

    @abstractmethod
    def _validate(self):
        """
        Validates appropriate data section in self._write_data.

        Return:

        Core snippet:

            {
            	"status": {
            		"code": 9999,
            		"text": "... message text ..."
            	}
            }

        Descendant method is freed to add any additional data as required.
        """

    @abstractmethod
    def _pre_write(self):
        """
        Carries out any tasks before writing self._write_data to database.

        Return:

        Core snippet:

            {
            	"status": {
            		"code": 9999,
            		"text": "... message text ..."
            	}
            }

        Descendant method is freed to add any additional data as required.
        """

    @abstractmethod
    def _write(self):
        """
        Writes appropriate data section in self._write_data to database.

        Return:

        Core snippet:

            {
            	"status": {
            		"code": 9999,
            		"text": "... message text ..."
            	}
            }

        Descendant method is freed to add any additional data as required.
        """

    @abstractmethod
    def _post_write(self):
        """
        Carries out any tasks after finished writing self._write_data 
        to database.

        Return:

        Core snippet:

            {
            	"status": {
            		"code": 9999,
            		"text": "... message text ..."
            	}
            }

        Descendant method is freed to add any additional data as required.
        """

    """
    Consider adding any decorator if apppropriate.
    """
    def write_to_database(self, data):
        """
        Template function: SHOULD NOT HAVE TO OVERRIDE.

        Arguments:

        data: a dictionary. Data to be written to database. 

        There is no predefined structure for this dictionary. Different structures  
        implemented by descendant classes.
        
        Each descendant class must pick out their own fields.

        Return:
        
        self._write_last_result: descendant classes defines and document the 
        structure for this data. It must have the follow core snippet:

            Core snippet:

                {
            	    "status": {
            		    "code": 9999,
            		    "text": "... message text ..."
            	    }
                }
        """

        logger().debug('Entered...')

        self._write_data = data
        self._write_last_result = None

        status = self._preprocess_write_data()
        
        if status.code == HTTPStatus.OK.value:
            status = self._validate()

        if status.code == HTTPStatus.OK.value:
            status = self._pre_write()

        if status.code == HTTPStatus.OK.value:
            status = self._write()

        if status.code == HTTPStatus.OK.value:
            status = self._post_write()

        logger().debug('Exited.')

        return self._write_last_result if self._write_last_result != None else status

    def __get_last_message(self):
        return self._last_message

    def __set_last_message(self, message):
        self._last_message = message

    """Message from last operation."""
    last_message = property(fget=__get_last_message, fset=__set_last_message)