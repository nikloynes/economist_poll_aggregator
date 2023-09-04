# economist_poll_aggregator
Code for the *poll aggregator* assignment for the Political Data Scientist role at The Economist

Last updated: NL, 04/09/23
_______________________________

The goal of this code is to provide a convenient and easy-to-use interface for the [Economist Political Data Scientist poll aggregation task](https://cdn-dev.economistdatateam.com/jobs/pds/code-test/assignment.html). The code is divided into 2 modules, `poll_agg.py` and `utils.py`, both of which live in `src/`. 

The core functionality (retrieving polling data, aggregating it, storing it into csvs) is containde in the script `get_polls_aggregate.py`. You can customise the behaviour of this script using arguments, and also run the underlying functions interactively (run `ipython` or `python` from the root directory of the repo and then `import src.poll_agg as pa`). 

I extensively tested this code on MacOS 12.4, Ubuntu 22.04 and Windows 10, using various Python versions from 3.10 through 3.11.5. If you face any problems, I recommend trying 3.11.5 in a `venv`. 

### Prerequesites
- This program was written in Python 3.11.5. You will need to make sure you have **Python 3.10** (or higher) installed on your machine for it to work. If you don't have Python installed, you can download it [here](https://www.python.org/downloads/).
- You don't *need* to do this, but it's advisable to run the code in a **virtual environment**: 
    - You can use Python's built-in `venv` module, or install `virtualenv` using `pip install virtualenv`. 
    - Then, create a virtual environment by running `python -m venv .venv` or `python -m virtualenv .venv` (you can change `.venv` to any name you like) in the root directory of this repository. 
    - Activate the virtual environment by running `source .venv/bin/activate` (or `source .venv/Scripts/activate` on Windows). 
    - When you're done, you can deactivate the virtual environment by running `deactivate` in your terminal.

### Install
- Clone this repository (copy the URL from the green "Code" button above, then run `git clone <URL>` in your terminal in the location you want to clone the repo to)
- Optional: create a virtual environment in the repo's root dir, activate the environment (see above)
- Install the required dependencies by running `pip install -r requirements.txt` in your terminal from the repo's root directory. 

### Running the code
- `get_polls_aggregate.py` doesn't need any arguments. You can run it in default configurations by typing `python get_polls_aggregate.py` in the repo's root dir - it will produce the output csvs `polls.csv` and `trends.csv` there.
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
- by default, the script will collect polls (and make aggregations) for **all candidates**, in `time_increment`s of **1 day**, with a `lead_time` of **3 days**, but lead_time only applying if polling data `is_missing` for a given date. It will exceed that `lead_time` if no data is available at all (`lead_override`). It will produce **means**. 
- The `lead_time` of 3 days and `lead_override==True` do **not** mean that there will always be data for a given candidate. Instead it means that there will be polling data for a given date. If you want there to always be data for a given candidate, you should produce aggregations just for individual candidates, loop over the candidates, and set `lead_override` to `True`. This way you will end up with very few NaNs in your data, but a lot of imprecise means. 
- `get_polls_aggregate.py` produces a logfile every time it's run. by default, this will be stored in `logs/` in the repo's root directory. You can customise the filepath by passing in the `-lo` or `--log_file_path` argument. 
- the default logging level is `INFO`. You can customise this by passing in the `-ll` or `--log_level` argument. If you are experiencing issues/bugs with the script, you can try setting the logging level to `DEBUG` to get more information about what's going on, and where the script is failing.

### Running tests
- I implemented a range of tests for all the functions contained in `poll_agg.py` and `utils.py`. They all use the pytest framework. In order to run the tests, simply run 
    ```bash
    pytest src/tests/test_poll_agg.py
    pytest src/tests/test_utils.py
    ``` 
    all tests should pass just fine.
- For this purpose, `pytest` and `pytest-mock` are also part of the `requirements.txt` file. 
- Optional: Given that I aim to write strictly typed python code, you may also want to install `mypy` and run `mypy src/poll_agg.py` to check that the code is type-safe. Unfortunately, there are still a few errors that come up here, all associated with the `filter_by_date()` function. this is due to mypy preferring very cumbersome definitions of `Tuple[]` - which I chose not to do for this function as it did not read well at all, and ended up not functioning at all. All other code is type-safe. 

### Notes on design choices for this task
In this section I will briefly explain some of the design choices I made for this task.
- Many Python coders like to write scripts where the main functionality is contained in a `main()` function, which is then called at the bottom of the script. I personally don't like this approach and prefer to write scripts where the main functionality is contained in the global scope. This is the approach I have taken here. 
- There is an argument against hard-coding constants (such as the URL for the polling data, out-paths) into the main code module. In production, you'd want some kind of config file or environment variables system for storing this info (especially once you move towards a database, API keys, etc.). However, I initially started this project with that appraoch, and it seemed completely overkill. For now, I decided I was fine with hard-coding 3 constants into the main module.
- In line with the spec of the assignment, I tried to be as explicit as possible when it comes to documentation/explanation. In practice, this means that there are verbose docstrings and comments in the code. I would usually comment considerably less, but I felt it was required for this task.
- In essence, this task can be completed in a few lines of code (cheating a bit, as we need our own `remove_non_numeric` function):    
    ```python
    polls_df = pd.read_html('https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html')[0]
    polls_df['date'] = pd.to_datetime(polls_df['Date'], format='%m/%d/%y')
    polls_df = polls_df.set_index('date').drop(['Date', 'Pollster', 'Sample'], axis=1)
    for col in candidate_cols:
        polls_df[col] = polls_df[col].apply(ut.remove_non_numeric)
    trends_df = polls_df.resample('1d').mean().rolling(window=7, min_periods=1).mean()
    polls_df.to_csv('polls.csv')
    trends_df.to_csv('trends.csv')
    ```  
    However, I found that, following investigation of the intricacies of pandas' `.resample` method, I was unable to replicate 1:1 the exact means or medians I achieved with the 'naive' (i.e. looping) method. Furthermore, I felt that such as submission would fail to demonstrate my ability to write clean, modularised, well-structured, well-documented code. As such, I decided to write my own aggregation function, which is a bit more verbose, but which I believe is more robust and intuitively understandable. Plus, obviously, we still need to deal with %-symbols, and other quirks in messy data (which would only get worse in the real world). This is best done with properly modularised code which is robust to edge cases and logs errors easily. 
- Rather than using a specific web scraping library, I'm relying on pandas' built in html reader function. For this task it proved sufficient, but for a more complex scraping tasks I would probably use something like `BeautifulSoup`.
- Though Python is dynamically typed, I believe strongly in the utility of type hints. At times this makes the code look a bit bulkier than it perhaps needs to be. However, in my experience, enforcing strict typing helps any Pyhton project down the road, and is thus something I do for 99% of my Python work now.
