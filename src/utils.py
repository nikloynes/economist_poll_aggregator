#!/usr/bin/env python
# utils.py

# Economist Poll aggregator assignment
# Utilities module

# this module contains utilities for running the poll aggregator

# USAGE: import utils as ut

# NL, 22/08/23
# NL, 29/08/23 -- deprecating dotenv-related funcs  
# NL, 03/09/23 -- adding validate_date_format

############
# IMPORTS 
############
import os
import logging
import re
from argparse import ArgumentTypeError
from typing import Any

###########
# EXCEPTIONS
###########
class EnvVarNotFoundError(Exception):
    pass

###########
# INIT
###########
# set up logger
logger = logging.getLogger('utils')

############
# FUNCTIONS 
############
def load_env_var(env_var: str):
    '''
    DEPRECATED 
    --> REMOVED dotenv logic from codebase

    loads an environment variable (from dotenv or regular env)
    and throws an error if it isn't found

    args:
        env_var (str): name of environment variable to load
    '''
    var = os.getenv(env_var)
    logging.info(f'loaded {env_var} from environment')

    if var is None:
        raise EnvVarNotFoundError(f'Environment variable {env_var} not found. Please add to environment.')
    
    return var


def remove_percentage_symbol(value: Any) -> Any:
    '''
    removes a percentage symbol from a string. 
    this function is useful as, when iterating over a
    pandas df with `apply`, there will be NaNs inbetween, 
    meaning we want to handle this.

    args:
        value (str): value to remove % from
    
    returns:
        value (str): value with % removed
    '''
    if isinstance(value, str) and '%' in value:
        return value.replace('%', '')
   
    return value


def remove_non_numeric(value: str) -> str:
    '''
    removes non-numeric characters from a string,
    but retaining '.' characters. 

    args:
        value (str): value to remove non-numeric characters from
    
    returns:
        value (str): value with non-numeric characters removed
    '''
    if isinstance(value, str):
        logging.debug(f'Removing non-numeric characters from {value}')
        return ''.join(filter(lambda c: c.isdigit() or c == '.', value))
    
    logging.debug(f'Value {value} is not a string. Returning as is.')
    return value


def validate_date_format(date_str: str) -> str:
    '''
    when user passes a date to the CLI, we want to validate
    that the format is YYYY-MM-DD . 
    while the dateutil parser will throw an error if it can't parse, 
    it will be easier to throw an error sooner.

    args:
        date_str (str): date string to validate
    
    returns:
        date_str (str): date string if valid
    '''
    date_format = r'\d{4}-\d{2}-\d{2}'  # YYYY-MM-DD

    if re.match(date_format, date_str):
        return date_str
    else:
        raise ArgumentTypeError(f'Invalid date format. Please use YYYY-MM-DD.')

