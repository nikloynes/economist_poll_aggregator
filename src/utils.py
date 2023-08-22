#!/usr/bin/env python
# utils.py

# Economist Poll aggregator assignment
# Utilities module

# this module contains utilities for running the poll aggregator

# USAGE: import utils as ut

# NL, 22/08/23

############
# IMPORTS 
############
import os
import logging

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


def remove_percentage_symbol(value):
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


def remove_non_numeric(value):
    '''
    removes non-numeric characters from a string,
    but retaining '.' characters. 

    args:
        value (str): value to remove non-numeric characters from
    
    returns:
        value (str): value with non-numeric characters removed
    '''
    if isinstance(value, str):
        return ''.join(filter(lambda c: c.isdigit() or c == '.', value))
    
    return value



