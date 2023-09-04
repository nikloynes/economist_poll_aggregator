#!/usr/bin/env python
# test_poll_agg.py

# TESTS
# poll_agg.py module

# this file contains a range of tests for the poll_agg module.

# USAGE: pytest test_poll_agg.py

# NL, 04/09/23

###########
# IMPORTS
###########
import sys
import pytest
import logging
import datetime as dt
from dateutil import parser as date_parser

import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

SCRIPT_DIR = sys.path[0] # so that we can run pytest from root dir
sys.path.insert(0, SCRIPT_DIR+'/../')

import poll_agg as pa

###########
# INIT
###########
# set up logger
logger = logging.getLogger('poll_agg_tests')

###########
# PATHS & CONSTANTS
###########
GOOD_POLLS = SCRIPT_DIR+'/example_data/good_polls.csv'
EMPTY_POLLS = SCRIPT_DIR+'/example_data/empty_polls.csv'
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
mock_data = {
    'Date': ['01/01/23', '02/01/23', '03/01/23', '03/01/23'],
    'Pollster': ['A', 'B', 'B', 'D'],
    'Sample': ['1000', '2000*', '1123', '1234+*'],
    'Candidate1': ['50.55%', '40%', '50%', np.nan],
    'Candidate2': ['40%', '50%', np.nan, np.nan]
}


def test_get_polls_no_dates_df_not_empty(mocker):
    '''
    just to assert whether the df is not empty under
    `normal` condidtions.
    '''
    mocker.patch('pandas.read_html', return_value=[pd.DataFrame(mock_data)])
    result = pa.get_polls('some_url')
    assert not result.empty


def test_get_polls_dates_in_bounds_df_not_empty(mocker):
    '''
    testing 
    - dates, in all their forms, in the bounds of existing data
    - resulting df isn't empty
    '''
    mocker.patch('pandas.read_html', return_value=[pd.DataFrame(mock_data)])
    result = pa.get_polls('some_url', from_date='01/01/23', to_date='02/01/23')
    result2 = pa.get_polls('some_url', from_date=dt.datetime(2023, 1, 1), to_date='02/01/23')
    result3 = pa.get_polls('some_url', from_date='01/01/23', to_date=dt.datetime(2023, 1, 2))
    result4 = pa.get_polls('some_url', from_date=dt.datetime(2023, 1, 1), to_date=None)
    assert not result.empty
    assert not result2.empty
    assert not result3.empty    
    assert not result4.empty 


def test_get_polls_column_renaming(mocker):
    '''
    testing that columns are always renamed to what we want,
    given a number of data input scenarios
    '''
    mocker.patch('pandas.read_html', return_value=[pd.DataFrame(mock_data)])
    expected_columns = ['date', 'pollster', 'n', 'Candidate1', 'Candidate2']
    
    # basic
    result = pa.get_polls('some_url')

    # with 1 date (in range)
    result2 = pa.get_polls('some_url', from_date='01/01/23')

    # with 2 dates in range
    result3 = pa.get_polls('some_url', from_date='01/01/23', to_date='02/01/23')
    
    # with 1 date out, one date in range
    result4 = pa.get_polls('some_url', from_date='01/01/22', to_date='02/01/23')

    # with 3 dates out of range
    result5 = pa.get_polls('some_url', from_date='01/01/22', to_date='02/01/22')

    assert list(result.columns) == expected_columns
    assert list(result2.columns) == expected_columns
    assert list(result3.columns) == expected_columns
    assert list(result4.columns) == expected_columns
    assert list(result5.columns) == expected_columns


def test_get_polls_data_types(mocker):
    '''
    ensuring our column data types are as expected 
    '''
    mocker.patch('pandas.read_html', return_value=[pd.DataFrame(mock_data)])

    result = pa.get_polls('some_url')
    assert result['date'].dtype == 'datetime64[ns]'
    assert result['n'].dtype == 'int64'
    assert result['Candidate1'].dtype =='float64'
    assert result['Candidate2'].dtype =='float64'


def test_get_polls_date_filtering(mocker):
    '''
    to ensure our date filtering functionality works
    as expected
    '''
    mocker.patch('pandas.read_html', return_value=[pd.DataFrame(mock_data)])
    
    # filtering, within bounds
    result = pa.get_polls('some_url', from_date=dt.datetime(2023, 1, 1), to_date=dt.datetime(2023, 1, 1))
    
    # filtering, out of bounds
    result2 = pa.get_polls('some_url', from_date=dt.datetime(2022, 1, 1), to_date=dt.datetime(2022, 1, 2))
    
    assert len(result) == 1
    assert result.iloc[0]['date'] == dt.datetime(2023, 1, 1)
    assert len(result2) == 0
    assert result2.empty


def test_network_issues(mocker):
    '''
    assuming we have a network timeout?
    '''
    mocker.patch('pandas.read_html', side_effect=TimeoutError)
    with pytest.raises(TimeoutError):
        pa.get_polls('some_url')


# TO DO:
# - parsing error on the .read_html() method 
#   (e.g. if the html is malformed, or the index is wrong)

# 4 - testing the validate_condidates() function
mock_polls_df = pd.DataFrame({
    'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
    'pollster': ['Pollster A', 'Pollster B', 'Pollster C'],
    'n': [1000, 2000, 3000],
    'CandidateA': [40, 50, 60],
    'CandidateB': [30, 40, 50],
    'CandidateC': [20, 30, 40]
})
mock_polls_df['date'] = pd.to_datetime(mock_polls_df['date'])
# we need to drop some cols for a certain flavour of this df
mock_polls_agg_df = mock_polls_df.drop(columns=pa.TRENDS_DROP)


def test_validate_candidates_all():
    result = pa.validate_candidates(mock_polls_df, 'all')
    assert result == ['CandidateA', 'CandidateB', 'CandidateC']


def test_validate_candidates_valid():
    '''
    testing a range of conditions where we are supplying something
    valid to the function that isn't 'all'
    '''
    result = pa.validate_candidates(mock_polls_df, 'CandidateA')
    result2 = pa.validate_candidates(mock_polls_df, 'CandidateB')
    result3 = pa.validate_candidates(mock_polls_df, 'CandidateC')
    result4 = pa.validate_candidates(mock_polls_df, ['CandidateA', 'CandidateC'])
    assert result == ['CandidateA']
    assert result2 == ['CandidateB']
    assert result3 == ['CandidateC']
    assert result4 == ['CandidateA', 'CandidateC']


def test_validate_candidates_invalid():
    '''
    testing a range of conditions where we are supplying something
    invalid to the function that isn't 'all'
    '''
    with pytest.raises(ValueError):
        pa.validate_candidates(mock_polls_df, 'invalid')
    with pytest.raises(ValueError):
        pa.validate_candidates(mock_polls_df, ['CandidateA', 'invalid'])


# 5 - testing the aggregate_with_lead_time() function
def test_aggregate_with_lead_time_empty_polls_df():
    empty_df = pd.DataFrame(columns=pa.BASE_COLS + ['Candidate1', 'Candidate2'])
    result = pa.aggregate_with_lead_time(empty_df, dt.datetime(2023, 1, 1))
    # need to subset as date column is still there
    assert result[['Candidate1', 'Candidate2']].isna().all().all()


def test_aggregate_with_lead_time_empty_polls_df_throw_error():
    empty_df = pd.DataFrame(columns=pa.BASE_COLS + ['Candidate1', 'Candidate2'])
    with pytest.raises(ValueError):
        result = pa.aggregate_with_lead_time(empty_df, dt.datetime(2023, 1, 1), throw_error=True)


def test_aggregate_with_lead_time_no_data_within_lead_time():
    result = pa.aggregate_with_lead_time(mock_polls_agg_df, dt.datetime(2024, 5, 1), lead_time=7, lead_override=False)
    assert result.drop(columns='date').isna().all().all()


def test_aggregate_with_lead_time_data_within_lead_time():
    result = pa.aggregate_with_lead_time(mock_polls_agg_df, dt.datetime(2024, 5, 1), lead_time=7, lead_override=True)
    assert len(result) == 1
    assert result.iloc[0]['date'] == dt.datetime(2024, 5, 1)
    assert result.iloc[0]['CandidateA'].dtype == 'float64'
    assert result.iloc[0]['CandidateB'].dtype == 'float64'
    assert result.iloc[0]['CandidateC'].dtype == 'float64'


def test_aggregate_with_lead_time_aggregation_accuracy():
    '''
    assessing whether we get the mean/median we want
    '''
    result = pa.aggregate_with_lead_time(mock_polls_agg_df, dt.datetime(2023,1,3), agg_type='mean', lead_time=2)
    result2 = pa.aggregate_with_lead_time(mock_polls_agg_df, dt.datetime(2023,1,3), agg_type='median', lead_time=2)
    assert result.iloc[0]['CandidateA'] == 50
    assert result.iloc[0]['CandidateB'] == 40
    assert result.iloc[0]['CandidateC'] == 30
    assert result2.iloc[0]['CandidateA'] == 50
    assert result2.iloc[0]['CandidateB'] == 40
    assert result2.iloc[0]['CandidateC'] == 30


# 6 - testing the aggregate_polls() function
def test_aggregate_polls_empty_polls_df():
    '''
    this should throw an attribute error, 
    as the genearted from_date and to_date will both 
    be nan and thus we can't create a date range
    '''
    empty_df = pd.DataFrame(columns=pa.BASE_COLS + ['Candidate1', 'Candidate2'])
    with pytest.raises(AttributeError):
        result = pa.aggregate_polls(empty_df)


def test_aggregate_polls_standard_polls_df():
    '''
    this is the condition
    we would get with the standard config, specifically
    when running the script'''
    result = pa.aggregate_polls(mock_polls_df)
    assert len(result) == 3
    assert result.iloc[0]['date'] == dt.datetime(2023, 1, 1)
    assert result.iloc[1]['date'] == dt.datetime(2023, 1, 2)
    assert result.iloc[2]['date'] == dt.datetime(2023, 1, 3)
    assert result.iloc[0]['CandidateA'] == 40
    assert result.iloc[1]['CandidateA'] == 50
    assert result.iloc[2]['CandidateA'] == 60
    assert result.iloc[0]['CandidateB'] == 30
    assert result.iloc[1]['CandidateB'] == 40
    assert result.iloc[2]['CandidateB'] == 50


def test_aggregate_polls_invalid_candidate():
    with pytest.raises(ValueError):
        result = pa.aggregate_polls(mock_polls_df, candidates=['CandidateA', 'invalid'])


def test_aggregate_polls_valid_candidate_subset():
    result = pa.aggregate_polls(mock_polls_df, candidates=['CandidateA', 'CandidateC'])
    assert len(result) == 3
    assert list(result.columns) == ['date', 'CandidateA', 'CandidateC']
    assert result.iloc[0]['CandidateA'] == 40
    assert result.iloc[1]['CandidateA'] == 50
    assert result.iloc[2]['CandidateA'] == 60
    assert result.iloc[0]['CandidateC'] == 20
    assert result.iloc[1]['CandidateC'] == 30
    assert result.iloc[2]['CandidateC'] == 40


def test_aggregate_polls_date_range_out_of_bounds():
    '''
    in this condition, we expect the function 
    to return an empty df with a row full of
    NaNs for each day/candidate
    '''
    result = pa.aggregate_polls(mock_polls_df, from_date=dt.datetime(2022, 1, 1), to_date=dt.datetime(2022, 1, 3))
    assert len(result) == 3
    assert result.iloc[0]['date'] == dt.datetime(2022, 1, 1)
    assert result.iloc[1]['date'] == dt.datetime(2022, 1, 2)
    assert result.iloc[2]['date'] == dt.datetime(2022, 1, 3)
    # lets just pick a few
    assert np.isnan(result.iloc[0]['CandidateA'])
    assert np.isnan(result.iloc[2]['CandidateB'])
    assert np.isnan(result.iloc[1]['CandidateC'])    


def test_aggregate_polls_interpolation_methods():
    '''
    we're leaving this as default, so lead_override is set to
    True. this means we should get a row for each day, 
    and we should get something of use in there as well. 
    '''
    result = pa.aggregate_polls(
        mock_polls_df, 
        from_date='2023-01-03',
        to_date='2023-01-06',
        interpolation='never')
    
    result2 = pa.aggregate_polls(
        mock_polls_df, 
        from_date='2023-01-03',
        to_date='2023-01-06',
        interpolation='always')
    
    result3 = pa.aggregate_polls(
        mock_polls_df, 
        from_date='2023-01-03',
        to_date='2023-01-06',
        interpolation='if_missing')
    
    assert len(result) == 1
    assert len(result2) == 4
    assert len(result3) == 4

    # some random checking
    assert not np.isnan(result.iloc[0]['CandidateA']) 
    assert not np.isnan(result2.iloc[3]['CandidateB'])


def test_aggregate_polls_interpolation_methods_no_lead_override():
    '''
    we're now forcing lead override off, which should give use some
    different results
    '''
    result = pa.aggregate_polls(
        mock_polls_df, 
        from_date='2023-01-03',
        to_date='2023-01-06',
        interpolation='never',
        lead_time=1,
        lead_override=False)
    
    result2 = pa.aggregate_polls(
        mock_polls_df, 
        from_date='2023-01-03',
        to_date='2023-01-06',
        interpolation='always',
        lead_time=1,
        lead_override=False)
    
    result3 = pa.aggregate_polls(
        mock_polls_df, 
        from_date='2023-01-03',
        to_date='2023-01-06',
        interpolation='if_missing',
        lead_time=1,
        lead_override=False)
    
    assert len(result) == 1
    assert len(result2) == 4
    assert len(result3) == 4

    # some random checking
    assert not np.isnan(result.iloc[0]['CandidateA']) 
    assert np.isnan(result3.iloc[2]['CandidateB'])
    assert np.isnan(result2.iloc[3]['CandidateB'])
