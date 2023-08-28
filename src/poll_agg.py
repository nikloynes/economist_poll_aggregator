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

############
# IMPORTS 
############
import os
import sys
import logging
from dotenv import load_dotenv
from typing import Union, Literal

import pandas as pd
import numpy as np
import datetime as dt
from dateutil import parser as date_parser

from . import utils as ut

###########
# EXCEPTIONS
###########
class EnvError(Exception):
    pass

###########
# INIT
###########
is_dotenv = load_dotenv()
if not is_dotenv:
    logging.info('dotenv not loaded')
    raise EnvError('dotenv not loaded. please check .env file is in root directory.')
else:
    logging.info('dotenv loaded')    

# set up logger
logger = logging.getLogger('poll_agg')

###########
# PATHS & CONSTANTS
###########
POLLS_URL = ut.load_env_var('POLLS_URL') 
POLLS_OUTFILE = ut.load_env_var('POLLS_OUTFILE')
TRENDS_OUTFILE = ut.load_env_var('TRENDS_OUTFILE')

# columns in every polls_df
BASE_COLS = ['date', 'pollster', 'n']

# columns to drop in trends_df
TRENDS_DROP = ['pollster', 'n']

###########
# FUNCTIONS
###########
def get_polls(url: str = POLLS_URL,
              from_date: dt.datetime | str = None,
              to_date: dt.datetime | str = None) -> pd.DataFrame:
    '''
    retrieves polling data from desired URL.
    is set up to work well for the polling data on 
    the assignment URL, but should work for other
    tabular data.

    args:
        :url (str): url to retrieve polling data from
        :from_date (dt.datetime or str): earliest date to retrieve data from, optional
        :to_date (dt.datetime or str): latest date to retrieve data from, optional

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

    # remove non-numeric characters from sample size, convert to int
    polls_df['n'] = polls_df['n'].apply(lambda x: ''.join(filter(str.isdigit, x)))
    polls_df['n'] = pd.to_numeric(polls_df['n'])

    # candidate cols to float
    candidate_cols = [col for col in polls_df.columns if col not in BASE_COLS]
    logging.info(f'candidates found: {candidate_cols}')

    for col in candidate_cols:
        polls_df[col] = polls_df[col].apply(ut.remove_non_numeric)

        # convert all cases in col which are '' to np.nan
        polls_df.loc[polls_df[col] == '', col] = np.nan
        polls_df[col] = polls_df[col].astype(float)

        # /100 (to decimals)
        polls_df[col] = polls_df[col] / 100

    # filter by date
    if from_date:
        if not isinstance(from_date, dt.datetime):
            from_date = date_parser.parse(from_date)
        polls_df = polls_df[polls_df['date'] >= from_date]
        logging.info(f'filtered polls by from_date: {from_date}')

    if to_date:
        if not isinstance(to_date, dt.datetime):
            to_date = date_parser.parse(to_date)
        polls_df = polls_df[polls_df['date'] <= to_date]
        logging.info(f'filtered polls by to_date: {to_date}')
    
    logging.info(f'polls shape: {polls_df.shape}')

    return polls_df


def aggregate_polls(polls_df: pd.DataFrame,
                    candidates: list[str] | str = 'all',
                    agg_type: Literal['mean', 'median'] = 'mean',
                    increment_days: int = 1,
                    min_lead_time: int = 0,
                    max_lead_time: int = 7,
                    interpolation: Literal['if_missing', 'always', 'never'] = 'if_missing',
                    from_date: dt.datetime | str = None,
                    to_date: dt.datetime | str = None) -> pd.DataFrame:
    '''
    this function takes a dataframe of polls (obtained from `get_polls`)
    and aggregates (averages) them by candidate column
    and returns a trends_df dataframe.

    NOTE: in its current form, this function will be completely
    agnostic to which pollsters originate which polls

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
        :interpolation (str): mechanism to use when leading polls, 
            either 'if_missing', 'always' or 'never'. 'if_missing' 
            will include data from `lead_time` previous days only if 
            there is no data for a given day. `always` will always include
            data from `lead_time` previous days. `never` will never include
            data from `lead_time` previous days, and return NaNs for days with
            missing data.
        :from_date (dt.datetime or str): earliest date to aggregate polls from, optional
        :to_date (dt.datetime or str): latest date to aggregate polls from, optional

    returns:
        trends_df (pd.DataFrame): dataframe of aggregated polls
    '''
    # error handling/ type checking
    if not isinstance(polls_df, pd.DataFrame):
        raise TypeError('polls_df must be a pandas DataFrame')
    
    if not isinstance(candidates, list) and not isinstance(candidates, str):
        raise TypeError('candidates must be a list or str')
    
    # ensure we have the right columns in polls_df
    if candidates!='all':
        if isinstance(candidates, str):
            candidates = [candidates]

        for candidate in candidates:
            if not isinstance(candidate, str):
                raise TypeError('candidates must be a list of strings')
            
            if candidate not in polls_df.columns:
                raise ValueError(f'candidate {candidate} not found in polls_df columns')
        
        polls_df = polls_df[BASE_COLS + candidates]
    logging.info(f'aggregating polls for candidates: {candidates}')

    if agg_type not in ['mean', 'median']:
        raise ValueError('agg_type must be either "mean" or "median"')
    
    if not isinstance(increment_days, int):
        raise TypeError('increment_days must be an int')
    
    if not isinstance(min_lead_time, int):
        raise TypeError('min_lead_time must be an int')
    
    if not isinstance(max_lead_time, int):
        raise TypeError('max_lead_time must be an int')
    
    if interpolation not in ['if_missing', 'always', 'never']:
        raise ValueError('lead_mechanism must be either "if_missing", "always" or "never"')
    
    # filter polls_df by date if required
    if from_date:
        if not isinstance(from_date, dt.datetime):
            from_date = date_parser.parse(from_date)
        polls_df = polls_df[polls_df['date'] >= from_date]
        logging.info(f'filtered polls by from_date: {from_date}')

    if to_date:
        if not isinstance(to_date, dt.datetime):
            to_date = date_parser.parse(to_date)
        polls_df = polls_df[polls_df['date'] <= to_date]
        logging.info(f'filtered polls by to_date: {to_date}')

    # remove redundant columns
    polls_df = polls_df.drop(columns=TRENDS_DROP)

    # log some info about the supplied data, our aggregation mechanism,
    # and also instantiate some vars
    logging.info(f'n polls retrieved: {len(polls_df)}')

    start_date = polls_df['date'].min()
    end_date = polls_df['date'].max()
    logging.info(f'earliest date with polls: {start_date}')
    logging.info(f'latest date with polls: {end_date}')
    
    # create a list of all dates between start and end date
    # with increments of increment_days
    dates = [start_date + dt.timedelta(days=x) for x in range(0, (end_date-start_date).days, increment_days)] 

    logging.info(f'polling averages produced in increments of {increment_days} days')

    logging.info(f'interpolation for days with missing data: {interpolation}')
    logging.info(f'lead time: {min_lead_time} days to {max_lead_time} days. this is days to include in aggregation per increment.')

    logging.info(f'aggregation method: {agg_type}.')

    logging.info(f'aggregating data for candidates: {candidates}')

    # start by aggregating data
    trends_df = polls_df.groupby('date').agg(agg_type).reset_index()
    
    if interpolation=='never':
        logging.info(f'not interpolating data. finished aggregating polls.')
        out_df = trends_df

    elif interpolation=='if_missing':
        logging.info(f'interpolating data for dates with missing poll data...')
        out_df = pd.DataFrame()
        for date in dates:
            if date in trends_df['date']:
                # copy data from trends_df to out_df
                logging.info(f'found data for {date}. retaining.')
                out_df = out_df.append(trends_df[trends_df['date']==date])
            else:
                logging.info(f'no data for {date}. interpolating...')
                # QUESTION HERE IS IF WE WANT TO CHECK IN POLLS DF OR IN TRENDS. 
                # IT DOESNT REALLY MATTER BUT WE MIGHT BE slightly more granula if checking
                # polls.
                subset_df = polls_df[polls_df['date']>=date-dt.timedelta(days=max_lead_time)]
                subset_df = subset_df[subset_df['date']<=date-dt.timedelta(days=min_lead_time)]
                # produce means for each column that isn't `date`
                subset_df = subset_df.groupby('date').agg(agg_type).reset_index()

    elif interpolation=='always':
        # iterate over `dates`.
        # if data exist in trends_df for that date, copy to out_df
        # if data do not exist in trends_df, combine days from 
        for date in dates:
            pass


    return out_df