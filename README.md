# State of our Jupyter Notebook tools

# Overview
There are two working sets of tools that are leveraged by our notebooks currently.  One is an organized set of cells from Jona's standardized workbook (Google Drive/Technical_OsmoSystems/Error Analysis/2018-08-17 Long-Term Static Repeatability Tests) and the other is a set of tools that Jason and others have provided (Google Drive/Technical_OsmoSystems/Tools/Jupyter Snippets)

Anything with display or "%" or "!" used iPython features (might conflict with being put into a python library)


Jona's WB
(Google Drive/Technical_OsmoSystems/Error Analysis/2018-08-17 Long-Term Static Repeatability Tests/2018-08-18 Jona.ipynb)

## Cell 1 -> (partially a candidate for sdk)
- pip install dependencies (not a candidate for sdk)
- import statements  (copy don't erase, ongoing experiments may find use of these imports)
    import pandas as pd
    import numpy as np
    import datetime
    import re
    from dateutil.parser import parse
    import plotly.graph_objs as go
    from plotly.offline import download_plotlyjs, init_notebook_mode, iplot, plot
    from sqlalchemy import create_engine
    from getpass import getuser, getpass
    from ipywidgets import widgets
- configure global variables and initialize database engine  (candidate for sdk)
```
  --###INITIALIZE VARIABLES ONCE
  init_notebook_mode(connected=True)
  old_nodes = []
  old_sensors = []
  old_start = None
  old_end = None
  dt_format = '%Y-%m-%d %H:%M:%S'
  db_engine = create_engine(
      'mysql+pymysql://{user}:{password}@{host}/{dbname}'.format(
          user='technician',
          password='0sm0b0ts',
          dbname='osmobot',
          host='osmobot-db2.cxvkrr48hefm.us-west-2.rds.amazonaws.com'
      )
  )
```


## Cell 2 -> Define experiments (not a candidate for sdk)
Jona created a dictionary that has the following structure
- 'name' : 'name of the experiment
- 'nodes' : list of nodes to retrieve data for the experiment
-
```
'events' : {
  start_date
  end_date
  annotation 1 -> n...
}
```

Once experiment variables are set, global variables are populated for usage in another Cell

## Cell 3 -> Helper functions (candidate for sdk))
- remove_outliers
- utc_to_local
- local_to_utc
- load_from_db
-- queries db and closes connection returning data set for nodes
- plot_splice_size (?)
- plot_rgbt
-- parses data and creates scatter plots and layout for figure/iPlot

## Cell 4 -> Bring in Node Data (candidate for sdk)
- Actually calls the db if needed.  Contains additional logic to see if a database call/refresh of the data is needed.
- populates

## Cell 5 -> Plot data (candidate for sdk)
- create the charts using plot_rgbt function and populated data set

## Below seems to be WIP progress code, Jona to confirm if those additional cells are useful

# End Jona Notebook

# Start Jupyter Snippets (tools Jason,Jacob has put together)
Google Drive/Technical_OsmoSystems/Tools/Jupyter Snippets

- data collection log
-- looks to open a file and perform some transformations on the data within
-- TODO: what is the data shape both in and out for this?
- Filter Node Data
-- Receives a dictionary and filters data for node, sensor, calculation dimension and start/end create_dates
- Hex String Parser
-- Purpose
--- Provide folks with the ability to parse a hex string into its constituent parts, using the actual software code that does so in our data processing.
-- Warnings
--- The code that you’ll be using may move around and this notebook is not maintained as a first-class citizen. If the instructions here are broken, please contact the software team.

-- Setup
--- Before you run this, you'll have to set up Node and log in. You'll only have to do this once:
```
1) Install Node v.8.10 on your machine.
  - You can check if this is already done by running this in your command prompt:
  - node --version
  - If it’s not there, you can get it from https://nodejs.org/download/release/v8.10.0/ . If you have a newer version, it's probably fine.
- Log in to npm:
  - npm login
  - Credentials:
  - username: osmobot-devops
  - password: Get this from someone on the software team.
  - e-mail: devops@osmobot.com
-- parses hex string using JS parsing library
-- has a lot of functionality re: hex string parsing, retrieving specific data from hex string
```
- Joining a data collection log with node data
-- Purpose
--- During an experiment, you often have a metadata "log" of times when you were collecting a specific type of data using a node.
--- This joiner allows you to augment your node data frame with this data. For each node data row, it finds the associated metadata and adds it in as additional columns. If there is no corresponding metadata row for a node data row, the node data row will get data_set_id of -1 or NaN and can easily be dropped from the resultant DataFrame.
- Node Start and Stopper Neptune (candidate for sdk)
-- UI for ssh'ing into a hub and starting stoping the hub.service

- Technician Access to Calculation Details-Aggressive anti-caching
-- Pulling calculation details from the DB
--- The calculation details table has all kinds of handy internal intermediate details for each calculation.
--- Getting the data from the DB as part of your notebook means you can get updated data just by re-running the notebook. However, since the database table is subject to change, it's also smart to save off the data in a file alongside the notebook so that you can run the notebook later without requiring database access.
--- Recommended practice is to use the database code while the experiment is in progress or when doing a single data pull, but always save that data off to a CSV and switch to using the CSV before you archive the notebook.

- Technician Access to Calculation Details
-- Pulling calculation details from the DB
--- The calculation details table has all kinds of handy internal intermediate details for each calculation.
--- Getting the data from the DB as part of your notebook means you can get updated data just by re-running the notebook. However, since the database table is subject to change, it's also smart to save off the data in a file alongside the notebook so that you can run the notebook later without requiring database access.
--- Recommended practice is to use the database code while the experiment is in progress or when doing a single data pull, but always save that data off to a CSV and switch to using the CSV before you archive the notebook.

# End Jason Notebook
