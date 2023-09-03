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
from src.utils import validate_date_format

############
# CLI args
############
parser = argparse.ArgumentParser(
    description='Args for running poll downloader & aggregator.'
    )

parser.add_argument(
    '-fd', 
    '--from_date', 
    type=validate_date_format,
    default = None, 
    help='Date from which to collect polls for. Format: YYYY-MM-DD.'
)

parser.add_argument(
    '-td', 
    '--to_date', 
    type=validate_date_format,
    default = None, 
    help='Date up to which (inclusive) to collect polls for. Format: YYYY-MM-DD')

parser.add_argument(
    '-at',
    '--agg_type',
    choices=['mean', 'median'],
    default='mean',
    help='Aggregation type (mean or median).'
)

parser.add_argument(
    '-c',
    '--candidates',
    nargs='*',
    default='all',
    help='Candidates to collect polls for. Defaults to all candidates.'
)

parser.add_argument(
    '-id',
    '--increment_days',
    default=1,
    help='The increment of days to produce aggregations for.'
)

parser.add_argument(
    '-le',
    '--lead_time',
    default=1,
    help='Lead time (number of days) to incorporate in averages'
)

parser.add_argument(
    '-i',
    '--interpolation',
    default='if_missing',
    help='When to interpolate data (i.e. use data from preceding days)\
        "if_missing", "never" or "always".'
)

parser.add_argument(
    '-po',
    '--polls_outpath',
    default='polls.csv',
    help='Filepath for raw polls csv.'
)

parser.add_argument(
    '-ao',
    '--aggs_outpath',
    default='trends.csv',
    help='Filepath for aggregations csv.'
)

parser.add_argument(
    '-lo', 
    '--log_file_path', 
    default=f'logs/get_polls_aggregate_{dt.datetime.now().strftime("%Y-%m-%d_%H-%M")}.log',
    help='Custom filepath for log file.')

parser.add_argument(
    '-ll',
    '--log_level',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='DEBUG',
    help='Log level for logging messages. "debug", "info", "warning", "error" or "critical".'
)

parser.add_argument(
    '-l', 
    '--log_to_stdout', 
    action='store_true',
    help='Print logging messages to stdout (as well as file)')

args = parser.parse_args()

############
# PATHS & CONSTANTS
############
LOG_FORMAT = '%(asctime)s [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(name)s - %(levelname)s - %(message)s'

############
# INIT
############
# Logger
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = logging.FileHandler(filename=args.log_file_path)
stdout_handler = logging.StreamHandler(sys.stdout)

if args.log_to_stdout:
    handlers = [file_handler, stdout_handler]
else:
    handlers = [file_handler]

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    handlers=handlers)

logger = logging.getLogger('LOGGER')

logging.debug(f'from_date: {args.from_date}')
logging.debug(f'to_date: {args.to_date}')
logging.debug(f'agg_type: {args.agg_type}')
logging.debug(f'candidates: {args.candidates}')
logging.debug(f'increment_days: {args.increment_days}')
logging.debug(f'lead_time: {args.lead_time}')
logging.debug(f'interpolation: {args.interpolation}')
logging.debug(f'polls_outpath: {args.polls_outpath}')
logging.debug(f'aggs_outpath: {args.aggs_outpath}')
logging.debug(f'log_file_path: {args.log_file_path}')
logging.debug(f'log_level: {args.log_level}')
logging.debug(f'log_to_stdout: {args.log_to_stdout}')

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

