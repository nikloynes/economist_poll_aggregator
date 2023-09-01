# economist_poll_aggregator
My code for poll aggregator assignment for the Political Data Scientist role at The Economist (08/2023)

Last updated: NL, 01/09/23

The goal of this code is to provide a convenient and easy-to-use interface for the [Economist Political Data Scientist poll aggregation task](https://cdn-dev.economistdatateam.com/jobs/pds/code-test/assignment.html). The code is broadly structured into 2 core modules, `poll_agg.py` and `utils.py`, both of which live in `src/`. The core functionality (retrieving polling data, aggregating it, storing it into csvs) is run through the script `get_polls_aggregate.py`. You can customise the behaviour of this script, and also run the underlying functions in an interactive session with heavy customisability.

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
-  `get_polls_aggregate.py` runs without needing any arguments. You can run it with default arguments simply by typing `python get_polls_aggregate.py` - it will 
- arguments
- logging

### Running tests
- regular tests script
- mypy for type checking

### Notes on design choices for this task