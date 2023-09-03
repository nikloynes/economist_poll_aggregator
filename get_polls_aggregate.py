#!/usr/bin/env python
# get_polls_aggregate.py

# Economist Poll aggregator assignment
# Script for retrieving, aggregating and writing out poll data.

# USAGE: python get_polls_aggregate.py [--ARGS]

# NL, 03/09/23

############
# IMPORTS 
############
import os
import sys
import logging
import argparse

import pandas as pd
import datetime as dt
from dateutil import parser as date_parser

import src.poll_agg as pa

############
# CLI args
############
parser = argparse.ArgumentParser(
    description='Args for running poll downloader & aggregator.'
    )

parser.add_argument(
    '-f', 
    '--from_date', 
    dest = 'from_date', 
    default = None, 
    help='Date from which to collect polls for. Format: YYYY-MM-DD.'
)

parser.add_argument(
    '-t', 
    '--to_date', 
    dest = 'to', 
    default = None, 
    help='Date up to which (inclusive) to collect polls for. Format: YYYY-MM-DD')

parser.add_argument(
    '-a',
    '--agg_type',
    dest='agg_type',
    default='mean',
    help='Aggregation type (mean or median).'
)

parser.add_argument(
    '-c',
    '--candidates',
    dest='candidates',
    nargs='*',
    default='all',
    help='Candidates to collect polls for. Defaults to all candidates.'
)

parser.add_argument(
    '-d',
    '--increment_days',
    dest='increment_days',
    default=1,
    help='The increment of days to produce aggregations for.'
)

parser.add_argument(
    '-l',
    '--lead_time',
    dest='lead_time',
    default=1,
    help='Lead time (number of days) to incorporate in averages'
)

parser.add_argument(
    '-i',
    '--interpolation',
    dest='interpolation',
    default='if_missing',
    help='When to interpolate data (i.e. use data from preceding days)\
        "if_missing", "never" or "always".'
)

parser.add_argument(
    '-p',
    '--polls_outpath',
    dest='polls_outpath',
    default='polls.csv',
    help='Filepath for raw polls csv.'
)

parser.add_argument(
    '-a',
    '--aggs_outpath',
    dest='aggs_outpath',
    default='trends.csv',
    help='Filepath for aggregations csv.'
)

parser.add_argument(
    '-o', 
    '--log_file_path', 
    dest='log_file_path',
    default=None,
    help='Custom filepath for log file.')

parser.add_argument(
    '-e',
    '--log_level',
    dest='log_level',
    default='info'
    help='Log level for logging messages. "debug", "info", "warning" or "error".'
)

parser.add_argument(
    '-l', 
    '--log_to_stdout', 
    dest='log_to_stdout',
    action='store_true',
    help='Print logging messages to stdout (as well as file)')

args = parser.parse_args()

###########
# PATHS & CONSTANTS
###########
FROM_DATE = args.from_date
TO_DATE = args.to_date
AGG_TYPE = args.agg_type
CANDIDATES = args.candidates
INCREMENT_DAYS = args.increment_days
LEAD_TIME = args.lead_time
INTERPOLATION = args.interpolation
POLLS_OUTPATH = args.polls_outpath
AGGS_OUTPATH = args.aggs_outpath

