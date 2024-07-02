"""
27/06/2024.
"""
import os
import logging
import logging.config
import yaml

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware which logs when a request starts and ends.
    This middleware effectively groups all loggings for a request
    execution together within a start and end request markers.
    """
    def __init__(self, app):
        super().__init__(app)

    def __get_session_id(self, request: Request):
        session_id = request.cookies.get('session')
        return session_id if session_id != None else '< Session Id not available >'
    
    async def dispatch(self, request: Request, call_next):
        session_id = self.__get_session_id(request)

        logger = logging.getLogger('fastapi_learning.debug')

        logger.info(f'* Request Started {session_id}')
        logger.info(f'Path: {request.url}')

        response = await call_next(request)

        logger.info(f'* Request Finished {session_id}')
        
        return response

def __retrieve_queue_listeners():
    """
    Retrieves and returns a list QueueListener instances associated 
    with the QueueHandler handlers.
    """
    listeners = []

    listeners.append(logging.getHandlerByName('queue_rotating_file').listener)
    return listeners

def prepare_logging_and_start_listeners(default_path='logger_config.yaml'):
    """
    1. Ensures ./logs sub-directory exists under script root directory.
    2. Loads the logger config YAML file and prepares the logging config.
    3. Retrieves a list QueueListener instances associated with the 
       QueueHandler handlers and get them to start listening.
    """

    # Ensure ./logs sub-directory exists under script root directory.
    os.makedirs(f".{os.sep}logs", exist_ok=True)

    # Now that ./logs sub-directory exists under script root directory,
    # loads the logger config YAML file and prepares the logging dictionary
    # config.
    with open(default_path, 'r') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

    listeners = __retrieve_queue_listeners()
    for listener in listeners:
        listener.start()

def logger():
    """
    Retrieves and returns the configured logger from the logging
    dictionary config.
    """

    return logging.getLogger('fastapi_learning.debug')

def logging_stop_listeners():
    """
    Retrieves a list QueueListener instances associated with the 
    QueueHandler handlers and get them to start listening.
    """

    listeners = __retrieve_queue_listeners()
    for listener in listeners:
        listener.stop()
