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

# IMPORTS
import numpy as np
import dateutil.tz
import datetime
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import iplot


# GENERAL FUNCTIONS
def osmo_lib_imported():
	print("Found and imported Osmo_Jupyter_Library.py")
	return True


# DATA FUNCTIONS
def load_from_db(nodes, start_time_local, end_time_local, disk_cache=True, force_reload=False):    
    csv_filename = 'cached_calculation_details_{nodes}_{start}_to_{end}.csv'.format(
        nodes="_".join(map(str, nodes)),
        start=date_to_filename_string(start_time_local),
        end=date_to_filename_string(end_time_local),
    )
    
    csv_already_exists = os.path.exists(csv_filename)
    load_from_db = force_reload or not csv_already_exists
    
    if disk_cache and csv_already_exists and not force_reload:
        # load from CSV instead of DB
        print('Loading cached file ', csv_filename, '.')
        raw_node_data = pd.read_csv(csv_filename)
    else:
        connection = db_engine.connect()
        raw_node_data = pd.read_sql(
            '''
                SELECT calculation_detail.*
                from calculation_detail
                where node_id in {nodes}
                and create_date between "{start_date}" and "{end_date}"
                order by create_date
            '''.format(
                nodes = "("+', '.join([str(n) for n in nodes])+")",
                start_date = local_to_utc(start_time_local),
                end_date = local_to_utc(end_time_local),
            ),
            db_engine
        )
        connection.close()
        
        if disk_cache:
            print('Saving data file to', csv_filename, '.')
            raw_node_data.to_csv(csv_filename, index=False)

    raw_node_data['create_date'] = utc_to_local(pd.to_datetime(raw_node_data['create_date']))
    raw_node_data['update_date'] = utc_to_local(pd.to_datetime(raw_node_data['update_date']))
    
    return raw_node_data


def remove_outliers(df,columns):
	threshold = 3 # number of std dev away from mean before data is thrown out
	df_copy = df.copy() # Pandas seems to break the laws of editing variables outside of the function scope, so make a copy instead
	for c in columns:
		average = df_copy[c].mean()
		stdev = df_copy[c].std()
		if stdev > 0:
			df_copy[c].apply(lambda x: np.NaN if (np.abs(x - average)  >= (threshold*stdev)) else x) # Replace all values outside of 3 standard deviations with NaN
	return df_copy

def save_df_to_csv(df):
	# Save the downloaded data to a file so that you can re-run the notebook even if the database changes or you lose access
	csv_filename = 'local_db_{}.csv'.format(datetime.datetime.now().isoformat()).replace(':', '-')
	print('Saving data file to', csv_filename, '.')
	df.to_csv(csv_filename, index=False)

def read_df_from_csv(csv_filename):
	# To load from CSV instead of database, put an up-to-date filename here and comment out everything above this in the cell
	df = pd.read_csv(csv_filename)
	df['create_date'] = pd.to_datetime(df['create_date'])
	return df

# DATETIME FUNCTIONS
'''
WARNING: most timezones here are local which will cause issues if you are elsewhere in time or space
'''
dt_format = '%Y-%m-%d %H:%M:%S'
localtz = dateutil.tz.tzlocal()
timezone_offset = localtz.utcoffset(datetime.datetime.now(localtz))


def date_to_string(dtime):
    return dtime if isinstance(dtime, str) else dtime.strftime(dt_format)

def date_to_filename_string(dtime):
    # Version of datetime safe for using in a filename
    return date_to_string(dtime).replace(':', '-')

def utc_to_local(dtime = None, dstring = None):
	# Takes datetime or string, returns the same type TODO: This is not great practice.
	if dstring:
		dtime = pd.to_datetime(dstring) + timezone_offset
		return date_to_string(dtime)
	else:
		return pd.to_datetime(dtime) + timezone_offset

def local_to_utc(dtime = None, dstring = None):
	# Takes datetime or string, returns the same type TODO: This is not great practice.
	if dstring:
		dtime = pd.to_datetime(dstring) - timezone_offset
		return date_to_string(dtime)
	else:
		return pd.to_datetime(dtime) - timezone_offset


# PLOT FUNCTIONS

def plot_splice_size(data, plot_settings):
	return int(len(data)/plot_settings['dots_to_plot']) or 1

def plot_rgbt(df, n, s, events, plot_settings):
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
