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


############
# IMPORTS 
############
import os
import sys
import logging
from typing import Union, Literal

import pandas as pd
import numpy as np
import datetime as dt
from dateutil import parser as date_parser

from . import utils as ut

###########
# EXCEPTIONS
###########

###########
# INIT
###########
# set up logger
logging.getLogger(__name__).addHandler(logging.NullHandler())

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
                   to_date: dt.datetime | str | None = None) -> (pd.DataFrame):
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
        elif isinstance(from_date, dt.datetime):
            tmp_date = from_date
        out += (tmp_date,)

    return out


# def create_date_range(df: pd.DataFrame,
#                       from_date: dt.datetime | str | None = None,
#                       to_date: dt.datetime | str | None = None) -> list[dt.datetime]:
#     '''
#     helper function that creates a list of all dates
    
#     '''


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
    else:
        # we will explicitly name our candidates for later use
        candidates = [col for col in polls_df.columns if col not in BASE_COLS]
    
    # remove redundant columns
    polls_df = polls_df.drop(columns=TRENDS_DROP)

    # filter polls_df by date if required
    polls_df = filter_by_date(polls_df, from_date, to_date)
    from_date, to_date = parse_from_to_date(polls_df, from_date, to_date)

    # create a list of all dates between from_date & to_date
    # with increments of increment_days
    dates = [from_date + dt.timedelta(days=x) for x in range(0, (to_date-from_date).days, increment_days)] 

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
    # potentially:
    # polls_EDIT_df.resample("1d").mean().rolling(window=2, min_periods=1).mean()
    
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

                subset_df = polls_df[polls_df['date']<=date]
                subset_df = subset_df[subset_df['date']>=(date-dt.timedelta(days=lead_time))]

                # potential problem - if we have no data, 
                # we need to expand our lead_time
                if len(subset_df)==0:
                    if lead_override:
                        logging.debug(f'no data for {date} minus lead time. \
                                      `lead_override` allowed, so expanding lead time...')
                        found_data = False
                        new_lead_time = lead_time
                        while not found_data:
                            new_lead_time += 1
                            logging.debug(f'new lead time: {new_lead_time}')

                            subset_df = polls_df[polls_df['date']<=date]
                            subset_df = subset_df[subset_df['date']>=(date-dt.timedelta(days=new_lead_time))]
                            if len(subset_df)>0:
                                found_data = True
                                logging.debug(f'found data for \
                                              {(date-dt.timedelta(days=5)).strftime(format="%Y-%m-%d")}\
                                               minus new lead time.')
                                break
                    else:
                        logging.debug(f'no data for {date}.\
                                      `lead_override` not allowed, so adding NaNs...')
                        # add NaNs for all candidates
                        newline = {'date': date, **{candidate: np.nan for candidate in candidates}}
                        out_df = pd.concat([out_df, pd.DataFrame(newline, index=[0])], ignore_index=True)
                        continue
                
                # produce aggregations for each column that isn't `date`
                if agg_type=='mean':
                    newline_df = subset_df.mean().to_frame().T
                elif agg_type=='median':
                    newline_df = subset_df.median().to_frame().T
                newline_df['date'] = date

                # append to out_df
                out_df = pd.concat([out_df, newline_df], ignore_index=True)

    # sort by date
    out_df = out_df.sort_values(by='date').reset_index(drop=True)
    logging.info(f'produced aggregations for {len(out_df)} days.')

    return out_df