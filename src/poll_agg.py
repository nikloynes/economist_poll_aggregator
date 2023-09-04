#!/usr/bin/env python
# poll_agg.py

# Economist Poll aggregator assignment
# Poll aggregator module

# this module contains functions for 
# - retrieving & cleaning polling data 
# - aggregating (averaging) polling data
# - error handling
# - logging
# - writing to files

# USAGE: import poll_agg as pa

# NL, 22/08/23
# NL, 28/08/23 -- refining aggregation function with interpolation
# NL, 29/08/23 -- simplification: removing dotenv, removing runtime
#                 type checking in favour of mypy
# NL, 01/09/23 -- ironing out quirks with out-of-bounds date 
#                 subsetting / interpolation
# NL, 04/09/23 -- cleaning up, refactoring (breaking up big functions),
#                 making compatible with mypy (mostly) and pytest


############
# IMPORTS 
############
import sys
import logging
from typing import Literal

import pandas as pd
import numpy as np
import datetime as dt
from dateutil import parser as date_parser

MODULE_DIR = sys.path[0] # so that we can run pytest from root dir
sys.path.insert(0, MODULE_DIR+'/../')

import src.utils as ut

###########
# EXCEPTIONS
###########

###########
# INIT
###########
# set up logger
logging.getLogger('poll_agg')

###########
# PATHS & CONSTANTS
###########
POLLS_URL = 'https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html'
POLLS_OUTFILE = 'polls.csv'
TRENDS_OUTFILE = 'trends.csv'

# columns in every polls_df
BASE_COLS = ['date', 'pollster', 'n']

# columns to drop in trends_df
TRENDS_DROP = ['pollster', 'n']

###########
# FUNCTIONS
###########
# helpers
def filter_by_date(df: pd.DataFrame,
                   from_date: dt.datetime | str | None = None,
                   to_date: dt.datetime | str | None = None) -> pd.DataFrame:
    '''
    helper function that allows us to subset a dataframe
    by a from_date and to_date. we re-use this quite a bit
    across this module, so makes sense to have it as its own
    function.

    args:
        :df (pd.DataFrame): dataframe to subset
        :from_date (dt.datetime, str, None): earliest date to retrieve data from, optional
        :to_date (dt.datetime, str, None): latest date to retrieve data from, optional

    returns:
        :df (pd.DataFrame): filtered dataframe
    '''
    if from_date:
        if not isinstance(from_date, dt.datetime):
            from_date = date_parser.parse(from_date)
        df = df[df['date'] >= from_date]
        logging.debug(f'filtered polls by from_date: {from_date}')

    if to_date:
        if not isinstance(to_date, dt.datetime):
            to_date = date_parser.parse(to_date)
        df = df[df['date'] <= to_date]
        logging.debug(f'filtered polls by to_date: {to_date}')
    
    return df


def parse_from_to_date(df: pd.DataFrame,
                       from_date: dt.datetime | str | None = None,
                       to_date: dt.datetime | str | None = None) -> (dt.datetime, dt.datetime):
    '''
    supplying from_date and to_date as args is optional. 
    if they aren't supplied, we take the earliest and latest
    dates from polls_df. this function produces the 
    objects we need in the correct format regardless of the
    configuration. 

    args:
        :df (pd.DataFrame): df to use if from_date and to_date aren't supplied
        :from_date (dt.datetime, str, None): earliest date to retrieve data from, optional
        :to_date (dt.datetime, str, None): latest date to retrieve data from, optional

    returns:
        :from_date (dt.datetime): earliest date to retrieve data from
        :to_date (dt.datetime): latest date to retrieve data from
    '''
    out = () 
    for i, date_obj in enumerate([from_date, to_date]):
        if date_obj is None:
            if i==0:
                tmp_date = df['date'].min()
            elif i==1:
                tmp_date = df['date'].max()
        elif isinstance(date_obj, str):
            tmp_date = date_parser.parse(date_obj)
        elif isinstance(date_obj, dt.datetime):
            tmp_date = date_obj
        else:
            raise TypeError(f'from_date and to_date must be either None, str or dt.datetime.\
                              {type(date_obj)} supplied.')
        out += (tmp_date,)
    return out


# the protein
def get_polls(url: str = POLLS_URL,
              from_date: dt.datetime | str | None = None,
              to_date: dt.datetime | str | None = None) -> pd.DataFrame:
    '''
    retrieves polling data from desired URL.
    is set up to work well for the polling data on 
    the assignment URL, but should work for other
    tabular data.

    the scraping method used here is pandas.read_html rather
    than a bespoke library. this depends on the `lxml` library.

    args:
        :url (str): url to retrieve polling data from
        :from_date (dt.datetime, str, None): earliest date to retrieve data from, optional
        :to_date (dt.datetime, str, None): latest date to retrieve data from, optional

    returns:
        polls (pd.DataFrame): polling data
    '''
    polls_df = pd.read_html(url)[0]
    logging.info(f'retrieved polling data from {url}')

    polls_df = polls_df.rename(columns={'Date': 'date',
                                        'Pollster' : 'pollster',
                                        'Sample' : 'n'})
    
    # date col to datetime
    polls_df['date'] = pd.to_datetime(polls_df['date'], format='%m/%d/%y')
    logging.debug(f'converted date column to datetime')

    # remove non-numeric characters from sample size, convert to int
    polls_df['n'] = polls_df['n'].apply(lambda x: ''.join(filter(str.isdigit, x)))
    polls_df['n'] = pd.to_numeric(polls_df['n'])
    logging.debug(f'converted sample size column - "n" - to int')

    # candidate cols to float
    candidate_cols = [col for col in polls_df.columns if col not in BASE_COLS]

    for col in candidate_cols:
        polls_df[col] = polls_df[col].apply(ut.remove_non_numeric)

        # convert all cases in col which are '' to np.nan
        polls_df.loc[polls_df[col] == '', col] = np.nan
        polls_df[col] = polls_df[col].astype(float)

        # /100 (to decimals)
        polls_df[col] = polls_df[col] / 100
    logging.debug(f'converted candidate perc columns to float')

    # filter by date
    polls_df = filter_by_date(polls_df, from_date, to_date)

    logging.info(f'n polls retrieved: {len(polls_df)}')
    logging.info(f'n unique pollsters: {len(polls_df["pollster"].unique())}')
    logging.info(f'candidates found: {candidate_cols}')
    logging.info(f'earliest date with polls: {polls_df["date"].min()}')
    logging.info(f'latest date with polls: {polls_df["date"].max()}')

    return polls_df


def validate_candidates(polls_df: pd.DataFrame,
                        candidates: list | str = 'all') -> list[str]:
    '''
    validates the input of candidates provided by user, 
    for use in the the aggregate_polls() function.
    '''
    if candidates == 'all':
        candidates = [col for col in polls_df.columns if col not in BASE_COLS]

    if isinstance(candidates, str):
        candidates = [candidates]

    for candidate in candidates:
        if not isinstance(candidate, str) or candidate not in polls_df.columns:
            raise ValueError(f'Invalid candidate: {candidate}')
    return candidates


def aggregate_with_lead_time(polls_df: pd.DataFrame,
                             date: dt.datetime,
                             lead_time: int = 7,
                             lead_override: bool = True,
                             agg_type: Literal['mean', 'median'] = 'mean',
                             candidates: list[str] | str = 'all',
                             throw_error: bool = False) -> pd.DataFrame:
    '''
    Assuming we want to interpolate, this function produces
    interpolated aggregation for 1 day. It returns a 1-line dataframe.
    By default, it returns NAs if there's either an empty polls_df
    originally supplied, or if lead_override is False and there's no
    data within the lead_time. This can be changed by setting throw_error
    to True. 

    args:
        :polls_df (pd.DataFrame): dataframe of polls
        :date (dt.datetime): date to aggregate polls for
        :lead_time (int): number of days before target day to include in an average
            when aggregating polls
        :lead_override (bool): whether to increase lead_time if there is no data
        :agg_type (str): type of aggregation to use, either 'mean' or 'median'
        :candidates (list[str] or str): list of candidates to
            aggregate polls for, or 'all' for all candidates.
            these must be column names in the polls df.
        :throw_error (bool): whether to throw an error if there's no data
            at all. defaults to False.
    '''
    logging.debug(f'Aggregating data with interpolation for date {date}')

    if candidates=='all':
        candidates = [col for col in polls_df.columns if col not in BASE_COLS]

    subset_df = polls_df[(polls_df['date'] <= date) & (polls_df['date'] >= (date - dt.timedelta(days=lead_time)))]

    if len(polls_df)==0 or (len(subset_df)==0 and not lead_override):
        logging.debug(f'No polling data. Returning NaNs.')
        if throw_error:
            raise ValueError(f'No polling data for {date}.')
        return pd.DataFrame({'date': date, **{candidate: np.nan for candidate in candidates}}, index=[0])

    while len(subset_df)==0 and lead_override:
        lead_time += 1
        logging.debug(f'New lead time: {lead_time}')
        subset_df = polls_df[(polls_df['date'] <= date) & (polls_df['date'] >= (date - dt.timedelta(days=lead_time)))]    
    
    # Produce aggregations for each column that isn't `date`
    if agg_type == 'mean':
        aggregation_df = subset_df.mean().to_frame().T
    elif agg_type == 'median':
        aggregation_df = subset_df.median().to_frame().T
    aggregation_df['date'] = date

    return aggregation_df


def aggregate_polls(polls_df: pd.DataFrame,
                    candidates: list[str] | str = 'all',
                    agg_type: Literal['mean', 'median'] = 'mean',
                    increment_days: int = 1,
                    lead_time: int = 7,
                    lead_override: bool = True,
                    interpolation: Literal['if_missing', 'always', 'never'] = 'if_missing',
                    from_date: dt.datetime | str | None = None,
                    to_date: dt.datetime | str | None = None) -> pd.DataFrame:
    '''
    this function takes a dataframe of polls (obtained from `get_polls()`)
    and aggregates (averages) them by candidate column
    and returns a trends_df dataframe.

    NOTE: in its current form, this function is
    agnostic to which pollsters produced which polls.

    args:
        :polls_df (pd.DataFrame): dataframe of polls
        :candidates (list[str] or str): list of candidates to 
            aggregate polls for, or 'all' for all candidates.
            these must be column names in the polls df.
        :agg_type (str): type of aggregation to use, either 'mean' or 'median'
        :increment_days (int): number of days to increment by when aggregating polls, 
            defaults to 1 (daily)
        :lead_time (int): number of days before target day to include in an average
            when aggregating polls
        :lead_override (bool): whether to increase lead_time if there is no data
        :interpolation (str): mechanism to use for interpolating averages, 
            either 'if_missing', 'always' or 'never'. 'if_missing' 
            will include data from `lead_time` previous days only if 
            there is no data for a given day. `always` will always include
            data from `lead_time` previous days. `never` will never include
            data from `lead_time` previous days, and not return any data for days
            without polls.
        :from_date (dt.datetime or str): earliest date to aggregate polls from, optional
        :to_date (dt.datetime or str): latest date to aggregate polls from, optional

    returns:
        trends_df (pd.DataFrame): dataframe of aggregated polls
    '''
    # some minor runtime type checking to prevent 
    # unexpected behaviour
    if interpolation not in ['if_missing', 'always', 'never']:
        raise ValueError('interpolation must be one of "if_missing", "always" or "never"')
    if agg_type not in ['mean', 'median']:
        raise ValueError('agg_type must be one of "mean" or "median"')

    # validate candidates, subset polls_df
    candidates = validate_candidates(polls_df, candidates)
    polls_df = polls_df[BASE_COLS + candidates]

    # remove redundant columns
    polls_df = polls_df.drop(columns=TRENDS_DROP)

    # filter polls_df by date if required
    polls_df = filter_by_date(polls_df, from_date, to_date)
    from_date, to_date = parse_from_to_date(polls_df, from_date, to_date)

    # create a list of all dates between from_date & to_date
    # with increments of increment_days
    dates = [from_date + dt.timedelta(days=x) for x in range(0, (to_date-from_date).days+1, increment_days)] 

    # some logging of core params of this run
    logging.info(f'n polls retrieved: {len(polls_df)}')
    logging.info(f'start date: {from_date}')
    logging.info(f'end date: {to_date}')
    logging.info(f'producing averages in increments of {increment_days} days')
    logging.info(f'interpolation rule for days with missing data: {interpolation}')
    logging.info(f'lead time: {lead_time} days.')
    logging.info(f'aggregation method: {agg_type}.')
    logging.info(f'aggregating data for candidates: {candidates}')

    # start by aggregating data
    trends_df = polls_df.groupby('date').agg(agg_type).reset_index()
    
    if interpolation=='never':
        logging.debug(f'not interpolating data. finished aggregating polls.')
        out_df = trends_df

    else:
        out_df = pd.DataFrame()
        for date in dates:
            logging.debug(f'processing date: {date}')

            if date in trends_df['date'].values:
                if interpolation=='if_missing':
                    # copy data from trends_df to out_df
                    logging.debug(f'found data for {date}. retaining.')
                    out_df = pd.concat([out_df, trends_df[trends_df['date']==date]], ignore_index=True)
                    use_lead_time = False

                elif interpolation=='always':
                    use_lead_time = True

            elif date not in trends_df['date']: # being explicit here to avoid confusion
                use_lead_time = True
                logging.debug(f'date {date} not found in trends_df. interpolating...')

            if use_lead_time:
                logging.debug(f'interpolating data for date {date}')
                newline_df = aggregate_with_lead_time(
                    polls_df=polls_df, 
                    date=date,
                    lead_time=lead_time,
                    lead_override=lead_override,
                    agg_type=agg_type,
                    candidates=candidates,
                    throw_error=False) 
                
                out_df = pd.concat([out_df, newline_df], ignore_index=True)

    # sort by date
    out_df = out_df.sort_values(by='date').reset_index(drop=True)
    logging.info(f'produced aggregations for {len(out_df)} days.')

    return out_df