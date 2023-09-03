# economist_poll_aggregator
My code for poll aggregator assignment for the Political Data Scientist role at The Economist (08/2023)

Last updated: NL, 01/09/23

The goal of this code is to provide a convenient and easy-to-use interface for the [Economist Political Data Scientist poll aggregation task](https://cdn-dev.economistdatateam.com/jobs/pds/code-test/assignment.html). The code is broadly structured into 2 core modules, `poll_agg.py` and `utils.py`, both of which live in `src/`. 

The core functionality (retrieving polling data, aggregating it, storing it into csvs) is easily run through the script `get_polls_aggregate.py`. You can customise the behaviour of this script, and also run the underlying functions in an interactive session with heavy customisability.

### Prerequesites
- This program was written in Python 3.11.5. You will need to make sure you have **Python 3.10** (or higher) installed on your machine for it to work. You can check this by running `python --version` or `python3 --version`, but if you have several versions installed, you may need to run something like this - `ls -l /usr/bin/python* & ls -l /usr/local/bin/python*` in your terminal. If you don't have Python installed, you can download it [here](https://www.python.org/downloads/).
- You don't *need* to do this, but it's advisable to run the code in a **virtual environment**: 
    - You can use Python's built-in `venv` module, or install `virtualenv` using `pip install virtualenv`. 
    - Then, create a virtual environment by running `python -m venv .venv` or `python -m virtualenv .venv` (you can change `.venv` to any name you like) in the root directory of this repository. 
    - Activate the virtual environment by running `source .venv/bin/activate` (or `source .venv/Scripts/activate` on Windows). 
    - When you're done, you can deactivate the virtual environment by running `deactivate` in your terminal.

### Install
- Clone this repository 
- Optional: create a virtual environment, activate the environment (see above)
- Install the required packages by running `pip install -r requirements.txt` in your terminal from the repo's root directory

### Running the code
-  `get_polls_aggregate.py` runs without needing any arguments. You can run it with default arguments simply by typing `python get_polls_aggregate.py` - it will produce the output csvs `polls.csv` and `trends.csv` in the repo's root directory
- You can customise the behaviour of the script by passing in arguments. You can see the available arguments by running `python get_polls_aggregate.py --help` in your terminal. These are the options available to you: 
```
usage: get_polls_aggregate.py [-h] [-fd FROM_DATE] [-td TO_DATE] [-at {mean,median}] [-c [CANDIDATES ...]]
                              [-id INCREMENT_DAYS] [-le LEAD_TIME] [-i INTERPOLATION] [-po POLLS_OUTPATH]
                              [-ao AGGS_OUTPATH] [-lo LOG_FILE_PATH] [-ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-l]

Args for running poll downloader & aggregator.

options:
  -h, --help            show this help message and exit
  -fd FROM_DATE, --from_date FROM_DATE
                        Date from which to collect polls for. Format: YYYY-MM-DD.
  -td TO_DATE, --to_date TO_DATE
                        Date up to which (inclusive) to collect polls for. Format: YYYY-MM-DD
  -at {mean,median}, --agg_type {mean,median}
                        Aggregation type (mean or median).
  -c [CANDIDATES ...], --candidates [CANDIDATES ...]
                        Candidates to collect polls for. Defaults to all candidates.
  -id INCREMENT_DAYS, --increment_days INCREMENT_DAYS
                        The increment of days to produce aggregations for.
  -le LEAD_TIME, --lead_time LEAD_TIME
                        Lead time (number of days) to incorporate in averages
  -i INTERPOLATION, --interpolation INTERPOLATION
                        When to interpolate data (i.e. use data from preceding days) "if_missing", "never" or "always".
  -po POLLS_OUTPATH, --polls_outpath POLLS_OUTPATH
                        Filepath for raw polls csv.
  -ao AGGS_OUTPATH, --aggs_outpath AGGS_OUTPATH
                        Filepath for aggregations csv.
  -lo LOG_FILE_PATH, --log_file_path LOG_FILE_PATH
                        Custom filepath for log file.
  -ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Log level for logging messages. "debug", "info", "warning", "error" or "critical".
  -l, --log_to_stdout   Print logging messages to stdout (as well as file)
``` 
- `get_polls_aggregate.py` produces a logfile. by default, this will be stored in `logs/` in the repo's root directory. You can customise the filepath by passing in the `-lo` or `--log_file_path` argument. 
- the default logging level is `INFO`. You can customise this by passing in the `-ll` or `--log_level` argument. If you are experiencing issues/bugs with the script, you can try setting the logging level to `DEBUG` to get more information about what's going on.

### Running tests
- regular tests script
- mypy for type checking

### Notes on design choices for this task