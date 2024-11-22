"""
29/07/2024.

Implement Basic Data Validation using WTForms.

It should capture all basic data validations required by the application.
"""

import inspect

from collections import OrderedDict

from werkzeug.datastructures import MultiDict

from wtforms import Form
from wtforms.meta import DefaultMeta

from bh_apistatus.result_status import (
    ResultStatus,
    make_status,
    make_500_status,
)

from fastapi_learning.common.queue_logging import logger

class BaseTranslations(object):
    def gettext(self, string):
        caller = inspect.currentframe().f_back.f_locals
    
        return f"{caller['self'].label.text} -- {string.lower()}"

    def ngettext(self, singular, plural, n):
        caller = inspect.currentframe().f_back.f_locals

        if n == 1:
            return f"{caller['self'].label.text} -- {singular.lower()}"

        return f"{caller['self'].label.text} -- {plural.lower()}"

class BaseValidationForm(Form):
    """Implement some generic customisations:

            * Fields ordered: orders of fields can be rearrange for each form.
            * Fields label: each field label can be customised for each field in each form.
            * Validation messages: built-in validation messages can be customised via "~label~".

    :Class Attributes:

        * _fields_ordered: array which lists ordered of fields.
        * _fields_label: array of tuples of (field name, label).

    I.e.::

        _fields_ordered = ['given_name', 'surname', 'address2', 'address1']
        _fields_label = [('given_name', 'Personal Given Name'), ('surname', 'Personal Surname')]
    """

    _fields_ordered = []
    _fields_label = []

    class Meta(DefaultMeta):
        def get_translations(self, form):
            return BaseTranslations()

    def search_field(self, key: str) -> tuple:
        for itm in list(self._fields.items()):
            if (itm[0] == key): return itm

        return None

    def __reorder_fields(self):
        if (len(self._fields_ordered) == 0): return

        tmp_field_dict = OrderedDict()            
        for key in self._fields_ordered:
            field = self.search_field(key)

            if (field != None): tmp_field_dict[field[0]] = field[1]

        self._fields = tmp_field_dict 

    def __customise_field_labels(self): 
        if (len(self._fields_label) == 0): return
        
        for itm in self._fields_label:
            field = self.search_field(itm[0])
            # Should not happen!
            if (field is None): continue

            field[1].label.text = itm[1]        

    def __customise_validators_message(self): 
        for key, field in self._fields.items():
            for validator in field.validators:
                if (not hasattr(validator, 'message')): continue
                if (validator.message is None): continue
                if (len(validator.message) == 0): continue

                validator.message = validator.message.replace("~label~", field.label.text)

    def __init__(
        self,
        formdata=None,
        obj=None,
        prefix="",
        data=None,
        meta=None,
        **kwargs,
    ):
        super().__init__(formdata, obj, prefix, data, meta, **kwargs)
        self.__reorder_fields()
        self.__customise_field_labels()
        self.__customise_validators_message()


def validate(data: dict, forms: list) -> ResultStatus:
    logger().debug('Entered...')
    try:
        record_list = [data] if (type(data) != list) else data

        errors = []

        for r in record_list:
            form_data = MultiDict(mapping=r)

            for form in forms:
                f = form(form_data)
                if (not f.validate()):
                    for err in list(f.errors.items()):
                        """
                        err[0]: form field name of field in error.
                        err[1]: list of error messages.
                        """
                        error = {"id": err[0], 
                                 "label": getattr(f, err[0]).label.text, 
                                 "errors": err[1]} 
                        
                        errors.append(error)

    except Exception as e:
        err_msg = str(e)
        logger().exception(err_msg)

        error = {"id": e.__class__.__qualname__, 
                 "label": e.__class__.__qualname__, 
                 "errors": err_msg}         
        errors.append(error)
                
        return make_500_status('').add_data(errors, name='errors')
    
    logger().debug('Exited.')
    
    if (len(errors) == 0): return make_status()
    return make_500_status('').add_data(errors, name='errors')
