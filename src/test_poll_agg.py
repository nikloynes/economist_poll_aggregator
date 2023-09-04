#!/usr/bin/env python
# test_poll_agg.py

# TESTS
# poll_agg.py module

# this file contains a range of tests for the poll_agg module.

# default values for function arguments are defined as
# constants at the top of the file. these can be however be changed.

# USAGE: pytest test_poll_agg.py

# NL, 04/09/23

###########
# IMPORTS
###########
import pytest
import logging
import datetime as dt
from dateutil import parser as date_parser

import pandas as pd
from pandas.testing import assert_frame_equal

from . import poll_agg as pa

###########
# INIT
###########
# set up logger
logger = logging.getLogger('poll_agg_tests')

###########
# PATHS & CONSTANTS
###########
GOOD_POLLS = 'example_data/good_polls.csv'
EMPTY_POLLS = 'example_data/empty_polls.csv'
BAD_DATE_STR = 'ekasdnjsr42'
WRONG_DATE_FMT = 23.04

GOOD_AGG_TYPE = 'mean'
BAD_AGG_TYPE = 'mode'

###########
# OBJECTS
###########
good_polls_df = pd.read_csv(GOOD_POLLS)
# we need to convert the date column to datetime,
# otherwise our tests will fail. this will 
# always be the case in our code.
good_polls_df['date'] = pd.to_datetime(good_polls_df['date'])
empty_polls_df = pd.read_csv(EMPTY_POLLS)
bad_polls_df_missing_date_col_df = pd.DataFrame({
    'col1': [1, 2, 3], 'col2': ['A', 'B', 'C']
    })

###########
# TESTS
###########
# 1 - testing the filter_by_date_function
def test_filter_by_date_with_from_date_string():
    from_date = '2023-01-02'
    filtered_df = pa.filter_by_date(good_polls_df, from_date=from_date)
    assert (filtered_df['date'] >= dt.datetime.strptime(from_date, '%Y-%m-%d')).all()


def test_filter_by_date_with_to_date_string():
    to_date = '2023-01-02'
    filtered_df = pa.filter_by_date(good_polls_df, to_date=to_date)
    assert (filtered_df['date'] <= dt.datetime.strptime(to_date, '%Y-%m-%d')).all()


def test_filter_by_date_with_bad_date_string():
    with pytest.raises(ValueError):
        pa.filter_by_date(good_polls_df, from_date=BAD_DATE_STR)


def test_filter_by_date_with_wrong_date_format_int():
    from_date = 24.02
    with pytest.raises(TypeError):
        pa.filter_by_date(good_polls_df, from_date=from_date)


def test_filter_by_date_with_both_dates_string():
    from_date = '2023-01-02'
    to_date = '2023-01-03'
    filtered_df = pa.filter_by_date(good_polls_df, from_date=from_date, to_date=to_date)
    assert (filtered_df['date'] >= dt.datetime.strptime(from_date, '%Y-%m-%d')).all()
    assert (filtered_df['date'] <= dt.datetime.strptime(to_date, '%Y-%m-%d')).all()


def test_filter_by_date_with_no_dates():
    filtered_df = pa.filter_by_date(good_polls_df)
    assert len(filtered_df) == len(good_polls_df)
    assert assert_frame_equal(filtered_df, good_polls_df, check_dtype=False) == None


def test_filter_by_date_with_invalid_df():
    '''
    this should still return the same
    df as supplied, as we are not supplying any 
    dates to filter by.
    '''
    filtered_df = pa.filter_by_date(bad_polls_df_missing_date_col_df)
    assert len(filtered_df) == len(bad_polls_df_missing_date_col_df)
    assert assert_frame_equal(filtered_df, bad_polls_df_missing_date_col_df, check_dtype=False) == None


def test_filter_by_date_with_from_date_datetime():
    from_date = dt.datetime(2023, 1, 2)
    filtered_df = pa.filter_by_date(good_polls_df, from_date=from_date)
    assert (filtered_df['date'] >= from_date).all()


def test_filter_by_date_with_to_date_datetime():
    to_date = dt.datetime(2023, 1, 2)
    filtered_df = pa.filter_by_date(good_polls_df, to_date=to_date)
    assert (filtered_df['date'] <= to_date).all()


def test_filter_by_date_with_both_dates_datetime():
    from_date = dt.datetime(2023, 1, 2)
    to_date = dt.datetime(2023, 1, 3)
    filtered_df = pa.filter_by_date(good_polls_df, from_date=from_date, to_date=to_date)
    assert (filtered_df['date'] >= from_date).all()
    assert (filtered_df['date'] <= to_date).all()


def test_filter_by_date_with_invalid_dataframe():
    invalid_df = pd.DataFrame({'foo': [1, 2, 3]})
    with pytest.raises(KeyError):
        pa.filter_by_date(invalid_df, from_date='2023-01-01')


# 2 - testing the parse_from_to_date function
dates = ['2022-01-01', '2022-01-02', '2022-01-03']
example_df = pd.DataFrame({'date': pd.to_datetime(dates)})

def test_parse_from_to_date_all_none():
    from_date, to_date = pa.parse_from_to_date(example_df)
    assert from_date == dt.datetime(2022, 1, 1)
    assert to_date == dt.datetime(2022, 1, 3)


def test_parse_from_to_date_all_str():
    from_date, to_date = pa.parse_from_to_date(example_df, '2022-01-01', '2022-01-03')
    assert from_date == dt.datetime(2022, 1, 1)
    assert to_date == dt.datetime(2022, 1, 3)


def test_parse_from_to_date_all_datetime():
    from_date, to_date = pa.parse_from_to_date(example_df, dt.datetime(2022, 1, 1), dt.datetime(2022, 1, 3))
    assert from_date == dt.datetime(2022, 1, 1)
    assert to_date == dt.datetime(2022, 1, 3)


def test_parse_from_to_date_mixed_none_str():
    from_date, to_date = pa.parse_from_to_date(example_df, None, '2022-01-03')
    assert from_date == dt.datetime(2022, 1, 1)
    assert to_date == dt.datetime(2022, 1, 3)


def test_parse_from_to_date_mixed_none_datetime():
    from_date, to_date = pa.parse_from_to_date(example_df, None, dt.datetime(2022, 1, 3))
    assert from_date == dt.datetime(2022, 1, 1)
    assert to_date == dt.datetime(2022, 1, 3)


def test_parse_from_to_date_mixed_str_datetime():
    from_date, to_date = pa.parse_from_to_date(example_df, '2022-01-01', dt.datetime(2022, 1, 3))
    assert from_date == dt.datetime(2022, 1, 1)
    assert to_date == dt.datetime(2022, 1, 3)


def test_parse_from_to_date_out_of_bounds_str():
    '''
    it should still give us our desired from_date and to_date,
    even if they aren't in the df. this is the expected
    behaviour. 
    '''
    from_date, to_date = pa.parse_from_to_date(example_df, '2024-12-31', '2025-01-04')
    assert from_date == dt.datetime(2024, 12, 31)
    assert to_date == dt.datetime(2025, 1, 4)


def test_parse_from_to_date_parser_error_from_date():
    '''
    a scenario where dateutil parser can't understand
    the string it was given, from_date
    '''
    with pytest.raises(date_parser.ParserError):
        pa.parse_from_to_date(example_df, 'foo', '2022-01-01')


def test_parse_from_to_date_parser_error_to_date():
    '''
    a scenario where dateutil parser can't understand
    the string it was given, to_date
    '''
    with pytest.raises(date_parser.ParserError):
        pa.parse_from_to_date(example_df, '2022-01-01', 'bar')


def test_parse_from_to_date_invalid_type():
    with pytest.raises(TypeError):
        pa.parse_from_to_date(example_df, [1, 2, 3], '2022-01-03')


def test_parse_from_to_date_empty_df_empty_dates():
    empty_df = pd.DataFrame()
    with pytest.raises(KeyError):  
        pa.parse_from_to_date(empty_df)


def test_parse_from_to_date_empty_df_from_date():
    empty_df = pd.DataFrame()
    with pytest.raises(KeyError):  
        pa.parse_from_to_date(empty_df, '2022-01-01', None)


def test_parse_from_to_date_empty_df_from_date():
    empty_df = pd.DataFrame()
    with pytest.raises(KeyError): 
        pa.parse_from_to_date(empty_df, None, '2022-01-01')


def test_parse_from_to_date_empty_df_both_dates_str():
    '''
    here the expected behaviour is to return our
    two dates as dts regardless of what the df is 
    doing. 
    '''
    empty_df = pd.DataFrame()
    from_date, to_date = pa.parse_from_to_date(empty_df, '2024-12-31', '2025-01-04')
    assert from_date == dt.datetime(2024, 12, 31)
    assert to_date == dt.datetime(2025, 1, 4)


def test_parse_from_to_date_empty_df_both_dates_dt():
    '''
    here the expected behaviour is to return our
    two dates as dts regardless of what the df is 
    doing. 
    '''
    empty_df = pd.DataFrame()
    from_date, to_date = pa.parse_from_to_date(empty_df, dt.datetime(2022, 1, 1), dt.datetime(2022, 1, 3))
    assert from_date == dt.datetime(2022, 1, 1)
    assert to_date == dt.datetime(2022, 1, 3)


# 3 - testing the get_polls() function
