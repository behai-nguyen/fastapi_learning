"""
29/07/2024.

Application level Business Object.
"""

from bh_apistatus.result_status import make_status

from .base_business import BaseBusiness

class AppBusiness(BaseBusiness):
    def _preprocess_write_data(self):
        """ Override. No processing needed. """
        return make_status()

    def _validate(self):
        """ Override. No processing needed. """
        return make_status()

    def _pre_write(self):        
        """ Override. No processing needed. """
        return make_status()

    def _write(self):
        """ Override. No processing needed. """
        return make_status()

    def _post_write(self):
        """ Override. No processing needed. """
        return make_status()
