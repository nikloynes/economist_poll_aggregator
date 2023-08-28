# economist_poll_aggregator
My code for poll aggregator assignment for the Political Data Scientist role at the Economist (08/2023)

Last updated: NL, 28/08/23

The goal of this code is to provide a convenient and easy-to-use interface for Economist Political Data Scientist poll aggregation task. The code is broadly structured into 2 core modules, `poll_agg.py` and `utils.py`, both of which live in `src/`. The core functionality (retrieving polling data, storing it into a csv and producing a csv of daily polling averages) is run through the script `get_polls_aggregate.py`

### Getting started
1. Prerequesites:
- You will need to make sure you have Python 3.8 (or higher) installed on your machine. You can check this by running `python --version` (or `python3 --version`) in your terminal. If you don't have Python installed, you can download it from [here](https://www.python.org/downloads/).
- You don't *need* to do this, but it's advisable to run the code in a virtual environment. Make sure you have the `virtualenv` module installed by running `pip install virtualenv` in your terminal. Then, create a virtual environment by running `virtualenv .venv` (you can change `.venv` for any name you like) in the root directory of this repository. Activate the virtual environment by running `source venv/bin/activate` (or `source venv/Scripts/activate` on Windows). You can deactivate the virtual environment by running `deactivate` in your terminal.
- This repo is configured so that important paths and constants are stored in a `.env` file. While at this stage in the project it isn't essential (there are no API keys required and no database connections), it enables portability and privacy within the project. In order to retain default settings for your environment, simply rename the `.env.example` file into `.env`. 

2. Install
- Clone this repository 
- create a virtual environment, activate the environment (see above)
- Install the required packages by running `pip install -r requirements.txt` in your terminal
- set up your `.env` file (see above)

3. Running the code
-  `get_polls_aggregate.py` runs without needing any arguments. You can run it with default arguments simply by typing `python get_polls_aggregate.py` - it will 
