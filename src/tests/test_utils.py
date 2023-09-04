#!/usr/bin/env python
# test_utils.py

# TESTS
# utils.py module

# this file contains a range of tests for the utils module.

# USAGE: pytest test_utils.py

# NL, 04/09/23

###########
# IMPORTS
###########
import sys
import pytest
from argparse import ArgumentTypeError

SCRIPT_DIR = sys.path[0] # so that we can run pytest from root dir
sys.path.insert(0, SCRIPT_DIR+'/../')

import utils as ut

###########
# TESTS
###########
def test_load_env_var():
    # deprecated this so no need for test
    pass


def test_remove_percentage_symbol():
    '''
    a variety of conditions to test our
    remove_percentage_symbol function
    does what it says on the tin
    '''
    # some expected true positives
    result = ut.remove_percentage_symbol('10%')
    result2 = ut.remove_percentage_symbol('10.0%')
    result3 = ut.remove_percentage_symbol('10.00%')

    # what about some unexpected ones
    result4 = ut.remove_percentage_symbol('10foo%')
    result5 = ut.remove_percentage_symbol('10%foo')

    # and some complete fails
    result6 = ut.remove_percentage_symbol(10)
    result7 = ut.remove_percentage_symbol([10, 20, 30])

    assert result == '10'
    assert result2 == '10.0'
    assert result3 == '10.00'
    assert result4 == '10foo'
    assert result5 == '10foo'
    # below aren't strings, so should return as supplied
    assert result6 == 10
    assert result7 == [10, 20, 30]


def test_remove_non_numeric():
    result = ut.remove_non_numeric('10%')
    result2 = ut.remove_non_numeric('10.0%')
    result3 = ut.remove_non_numeric('10.00%')
    result4 = ut.remove_non_numeric('10foo%')
    result5 = ut.remove_non_numeric('10%foo')

    result6 = ut.remove_non_numeric(10)
    result7 = ut.remove_non_numeric([10, 20, 30])

    assert result == '10'
    assert result2 == '10.0'
    assert result3 == '10.00'
    assert result4 == '10'
    assert result5 == '10'
    # below aren't strings, so should return as supplied
    assert result6 == 10
    assert result7 == [10, 20, 30]


def test_validate_date_format_correct():
    result = ut.validate_date_format('2020-01-01')
    result2 = ut.validate_date_format('2020-01-01 00:00:00')
    assert result == '2020-01-01'
    assert result2 == '2020-01-01 00:00:00'


def test_validate_date_format_incorrect():
    with pytest.raises(ArgumentTypeError):
        result = ut.validate_date_format('01/01/1996')    
    
    with pytest.raises(ArgumentTypeError):
        result = ut.validate_date_format('foo')

    with pytest.raises(TypeError):
        result = ut.validate_date_format(2023)

    with pytest.raises(TypeError):
        result = ut.validate_date_format([2023, 1, 12])

    