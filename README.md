python-sdk

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

# Start Jason Notebook

Jason to provide what could copy over.

# End Jason Notebook
