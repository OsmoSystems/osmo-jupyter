#!/usr/bin/env python3
"""
This is a library to store code snippets that other technicians might find useful. 
The following snippet must occur at the beginning of ajupyter notebook to make use of the following functions.

# Find Osmo's Jupyter Library 
import os
import sys
import importlib
if not any(['python-jupyter-tools' in p for p in sys.path]):
    found_osmo_library = False
    for root, dirs, files in os.walk(r'/'):
        for name in files:
            if name == "Osmo_Jupyter_Library.py":
                sys.path.append(os.path.abspath(root))
                import Osmo_Jupyter_Library as ojl
                found_osmo_library = ojl.osmo_lib_imported()
                break
        if found_osmo_library:
            break
    if not found_osmo_library:
        print("WARNING COULD NOT FIND THE FOLDER CONTAINING Osmo_Jupyter_Library.py")
else:
    import Osmo_Jupyter_Library as ojl
    importlib.reload(ojl)
    ojl.osmo_lib_imported()


Functions are then called like this:
ojl.osmo_lib_imported()
"""

# CONSTANTS
dt_format = '%Y-%m-%d %H:%M:%S'


def osmo_lib_imported():
	print("Found and imported Osmo_Jupyter_Library.py")
	return True

def remove_outliers(df,columns):
	import numpy as np
	threshold = 3 # number of std dev away from mean before data is thrown out
	df_copy = df.copy() # Pandas seems to break the laws of editing variables outside of the function scope, so make a copy instead
	for c in columns:
		average = df_copy[c].mean()
		stdev = df_copy[c].std()
		if stdev > 0:
			df_copy[c] = df_copy[c].apply(lambda x: np.NaN if (np.abs(x - average)  >= (threshold*stdev)) else x) # Replace all values outside of 3 standard deviations with NaN
	return df_copy

def now():
	import datetime
	return datetime.datetime.now().strftime(dt_format)

def utc_to_local(dtime = None, dstring = None):
	import datetime
	if dstring:
		utc_dt = datetime.datetime.strptime(dstring, dt_format)
		return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime(dt_format)
	else:
		dtime = datetime.datetime.strptime(dtime.strftime(dt_format), dt_format) # TODO: This is a hack! I don't understand python timezones well enough to do this correctly
		return dtime.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime(dt_format) # TODO: change this to return a dtime instead of a dstring

def local_to_utc(dtime = None, dstring = None):
	import datetime
	if dstring:
		local_dt = datetime.datetime.strptime(dstring, dt_format)
		return local_dt.replace(tzinfo=None).astimezone(tz=datetime.timezone.utc).strftime(dt_format)
	else:
		return dtime.replace(tzinfo=None).astimezone(tz=datetime.timezone.utc)

def load_from_db(db_engine, nodes, events, down_sample):
    # Database protocol required to connect to our MySQL database. Only needs to run once
    import pandas as pd

    connection = db_engine.connect()
    raw_node_data = pd.read_sql(
        '''
            SELECT calculation_detail.*, reading.hub_id
            from (calculation_detail join reading on reading.reading_id = calculation_detail.reading_id)
            where calculation_detail.node_id in {nodes}
            and calculation_detail.create_date between "{start_date}" and "{end_date}"
            and MOD(calculation_detail.reading_id,{down_sample}) = 0
            order by calculation_detail.create_date
        '''.format(	
            nodes = "("+', '.join([str(n) for n in nodes])+")",
            start_date = local_to_utc(dstring = events['start']),
            end_date = local_to_utc(dstring = events['end']),
            down_sample = down_sample,
        ),
        db_engine
    )
    connection.close()
    return raw_node_data

def plot_splice_size(data, plot_settings):
    return int(len(data)/plot_settings['dots_to_plot']) or 1

def plot_rgbt(df, n, s, events, plot_settings):
    import plotly.graph_objs as go
    from plotly.offline import iplot
    indices = {
        'r': {'color':'red', 'axis': 2 if plot_settings['plot_on_separate_axes'] else 2},
        'g': {'color':'green', 'axis': 3 if plot_settings['plot_on_separate_axes'] else 2},
        'b': {'color':'blue', 'axis': 4 if plot_settings['plot_on_separate_axes'] else 2},
    }
    
    node_sorted_data = df[
        (df['sensor_index'] == s) &
        (df['node_id'] == n)
    ]
    node_data = remove_outliers(node_sorted_data, indices.keys()) # Remove big count outliers for better visualization (prevents skewed scale based on outlieres)
    node_data = node_data.iloc[::plot_splice_size(node_data, plot_settings), :]  # resamples every nth row so that Plotting doesnt use so much CPU 

    temperature_data = df[
        (df['calculation_dimension'] == 'temperature') &
        (df['node_id'] == n)
    ]
    temperature_data = temperature_data.iloc[::plot_splice_size(temperature_data, plot_settings), :]  # resamples every nth row so that Plotting doesnt use so much CPU 
    if s in [0,1,2,3]:
        LED = 'White LED'
    elif s in [4,5,6,7]:
        LED = 'Blue LED'
        
    if not len(node_data['create_date']):
        print('No Data to Plot for Node {}, Sensor {}.'.format(n, s))
    else:
        node_data_traces = [
            go.Scatter(
                x= node_data['create_date'],
                y= node_data[col] / (1 if not plot_settings["plot_ratio_instead_of_count"] else (node_data['r'] + node_data['g'] + node_data['b'])),
                name = col,
                mode= 'markers',
                marker = {'color':indices[col]['color']},
                yaxis= 'y'+str(indices[col]['axis']))
            for col in indices
        ] + [
            go.Scatter(
                x= temperature_data['create_date'],
                y= temperature_data['calculated_value'],
                name = 'temperature',
                mode= 'markers',
                marker = {'color':'black'},
                yaxis= 'y5'
            )
        ]
        
        layout= go.Layout(
            title="RGB for Node {}, LS{} {}".format(n, s, LED),
            xaxis={'title':'Time'},
            yaxis={
                'title':'',
                'range':[0,1],
                'visible':False
            },
            **{'yaxis'+str(indices[col]['axis']): {
                'title': col,
                'overlaying':'y',
                'tickcolor': indices[col]['color'],
                'side':'left' if indices[col]['axis'] <=2 else 'right',
                'visible': True if indices[col]['axis'] <=3 else False
            } for col in indices
            },
            yaxis5={
                'title':'Temperature',
                'overlaying':'y',
                'side':'right',
                'visible':False
            },
            annotations=[
                {
                    'x' : events[e],
                    'y' : 0.95,
                    'xref' : 'x',
                    'yref' : 'y',
                    'text' : e,
                    'showarrow' : True,
                    'textangle' : -55,
                    'ax' : 1
                }
                for e in events]
        )
        figure = go.Figure(data=node_data_traces, layout=layout)
        iplot(figure, show_link=False)


def save_df_to_csv(df):
	# Save the downloaded data to a file so that you can re-run the notebook even if the database changes or you lose access
	import datetime
	csv_filename = 'local_db_{}.csv'.format(datetime.datetime.now().isoformat()).replace(':', '-')
	print('Saving data file to', csv_filename, '.')
	df.to_csv(csv_filename, index=False)

def read_df_from_csv(csv_filename):
	# To load from CSV instead of database, put an up-to-date filename here and comment out everything above this in the cell
	import pandas as pd
	df = pd.read_csv(csv_filename)
	df['create_date'] = pd.to_datetime(df['create_date'])
	return df