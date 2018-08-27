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
from plotly.offline import iplot, init_notebook_mode
import os
from sqlalchemy import create_engine


# GENERAL FUNCTIONS
def osmo_lib_imported():
	print("Found and imported Osmo_Jupyter_Library.py")
	return True


# DATA FUNCTIONS
db_engine = create_engine(
	'mysql+pymysql://{user}:{password}@{host}/{dbname}'.format(
		user='technician',
		password='0sm0b0ts',
		dbname='osmobot',
		host='osmobot-db2.cxvkrr48hefm.us-west-2.rds.amazonaws.com'
	)
)

def parse_exp(exp):
	if ('end' not in exp['events']) or (exp['events']['end'] == 'ongoing'):
		exp['events']['end'] = date_to_string(datetime.datetime.now())
	sensors = [0,1,2,3,4,5,6,7]
	return [exp['nodes'], exp['events'], sensors]

def load_from_db(exp, down_sample = 1, save_to_csv=False, force_reload=False):	
	csv_filename = 'cached_data_{nodes}_{start}_to_{end}.csv'.format(
		nodes="_".join(map(str, exp['nodes'])),
		start=date_to_filename_string(exp['events']['start']),
		end=date_to_filename_string(exp['events']['end']),
	)
	
	if os.path.exists(csv_filename) and not force_reload:
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
				and MOD(calculation_detail.reading_id,{down_sample}) = 0
				order by create_date
			'''.format(
				nodes = "("+', '.join([str(n) for n in exp['nodes']])+")",
				start_date = local_to_utc(exp['events']['start']),
				end_date = local_to_utc(exp['events']['end']),
				down_sample = down_sample,
			),
			db_engine
		)
		connection.close()
		
		if save_to_csv:
			print('Saving data file to', csv_filename, '.')
			raw_node_data.to_csv(csv_filename, index=False)

	raw_node_data['create_date'] = utc_to_local(raw_node_data['create_date'])
	raw_node_data['update_date'] = utc_to_local(raw_node_data['update_date'])
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
crgb_to_color = {
	'c': 'black',
	'r': 'red',
	'g': 'green',
	'b': 'blue'
}


init_notebook_mode(connected=True)

def subsample_for_plot(df, plot_settings):
	# resample every nth row so that Plotting doesnt use so much CPU 
	n = int(len(df)/plot_settings['dots_to_plot']) or 1
	return df.iloc[::n, :]

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
	node_data = subsample_for_plot(node_data, plot_settings)  # resamples every nth row so that Plotting doesnt use so much CPU 

	temperature_data = df[
		(df['calculation_dimension'] == 'temperature') &
		(df['node_id'] == n)
	]
	temperature_data = subsample_for_plot(temperature_data, plot_settings)  # resamples every nth row so that Plotting doesnt use so much CPU 
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

def axis_attributes(color, title, left_side, **kwargs):
	return dict(
		**{
			'title': title,
			'overlaying': 'y',
			'side': 'left' if left_side else 'right',
			'color': color,
#			 'font': {'color': color},
#			 'tickfont': {'color': color},
		},
		**kwargs
	)
def clean_crgb_and_temperature_data(node_id, sensor_index, raw_node_data):
	sensor_data = raw_node_data[
		(raw_node_data['sensor_index'] == sensor_index) &
		(raw_node_data['node_id'] == node_id)
	]
	crgb_data = remove_outliers(sensor_data,['c','r','g','b'])

	temperature_data = raw_node_data[
		(raw_node_data['calculation_dimension'] == 'temperature') &
		(raw_node_data['node_id'] == node_id)
	]
	temperature_data_reindexed = (
		temperature_data
		.drop('reading_id', axis='columns')
		.set_index(temperature_data['reading_id'])
	)
	
	crgbt_data = (
		crgb_data
		.join(temperature_data_reindexed, on='reading_id', how='left', rsuffix='_temperature')
		.rename({'calculated_value_temperature': 'temperature'}, axis='columns')
	)[['c','r','g','b','temperature', 'create_date']]
	
	return crgbt_data

def plot_relative_crgb_and_temperature(crgbt_data, node_id, sensor_index, correlation_info, events):
	subsampled_crgbt_data = subsample_for_plot(crgbt_data)
	
	max_crgb = subsampled_crgbt_data.max()

	if crgbt_data.empty:
		print('No Data to Plot for Node {}, Sensor {}.'.format(node_id, sensor_index))
		return
	
	time_since_experiment_start_12hrs = (subsampled_crgbt_data['create_date'] - crgbt_data['create_date'].min()) / pd.Timedelta(hours=12)
	
	crgb_traces = [
		go.Scatter(
			x=subsampled_crgbt_data['create_date'],
			y=subsampled_crgbt_data[color_letter] / max_crgb[color_letter],
			text=subsampled_crgbt_data[color_letter].apply(lambda counts: f'raw counts: {counts}'),
			name=color_letter,
			mode='markers',
			marker={'color':crgb_to_color[color_letter]},
			yaxis='y2',
		)
		for color_letter in 'crgb'
	]
	
	crgb_temperature_serieses = {
		color_letter: correlation_info[color_letter]['intercept'] + subsampled_crgbt_data['temperature'] * correlation_info[color_letter]['temperature_slope_counts_per_degree']
		for color_letter in 'crgb'
	}
	crgb_temperature_traces = [
		go.Scatter(
			x=subsampled_crgbt_data['create_date'],
			y=crgb_temperature_serieses[color_letter] / max_crgb[color_letter],
			name=f'temperature effect ({color_letter})',
			mode='lines',
			line={
				'color': crgb_to_color[color_letter],
				'dash': 'dash',
			},
			yaxis='y2',
			opacity=0.5,
		)
		for color_letter in 'crgb'
	]
	
	crgb_regression_serieses = {
		color_letter: (
			correlation_info[color_letter]['intercept'] + 
			subsampled_crgbt_data['temperature'] * correlation_info[color_letter]['temperature_slope_counts_per_degree'] + 
			time_since_experiment_start_12hrs * correlation_info[color_letter]['time_slope_counts_per_12hr'] 
		)
		for color_letter in 'crgb'
	}
	crgb_regression_traces = [
		go.Scatter(
			x=subsampled_crgbt_data['create_date'],
			y=crgb_regression_serieses[color_letter] / max_crgb[color_letter],
			name=f'temperature + time regression ({color_letter})',
			mode='lines',
			line={
				'color': crgb_to_color[color_letter],
				'width': 1,
			},
			yaxis='y2',
			opacity=0.5,
		)
		for color_letter in 'crgb'
	]

	node_data_traces = crgb_temperature_traces + crgb_regression_traces + crgb_traces + [
		go.Scatter(
			x=subsampled_crgbt_data['create_date'],
			y=subsampled_crgbt_data['temperature'],
			name='temperature',
			mode='markers',
			marker={'color':'black', 'symbol': 'cross-thin-open'},
			yaxis='y3'
		),
	]  

	if sensor_index in [0,1,2,3]:
		LED = 'White LED'
	elif sensor_index in [4,5,6,7]:
		LED = 'Blue LED'

	layout= go.Layout(
	title="crgb for Node {}, LS{} {}".format(node_id, sensor_index, LED),
	xaxis={'title':'Time'},
	yaxis={
		'title':'',
		'range':[0,1],
		'visible':False
	},
	yaxis2=axis_attributes(color='black', title='Relative intensity (value / max value)', left_side=True),
	yaxis3=axis_attributes(color='black', title='Temperature', left_side=False),
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

def get_covariance_matrix(crgbt_data):
	crgbt_data_for_covariance = crgbt_data.copy()
	create_date_integers = crgbt_data_for_covariance['create_date'].apply(lambda datetime: int(datetime.value))
	crgbt_data_for_covariance['create_date'] = create_date_integers # Replace column with one that we can calculate covariance on
	
	return crgbt_data_for_covariance.cov()

def get_correlation_status(r_value):
	'''
	Simplify an R value (https://en.wikipedia.org/wiki/Pearson_correlation_coefficient) to a basic positive, negative, or zero value
	'''
	r_value_threshold = 0.5
	
	if r_value < -r_value_threshold:
		correlation = -1
	elif r_value > r_value_threshold:
		correlation = 1
	else:
		correlation = 0
		
	return correlation
		

def analyze_temperature_and_time_correlation(crgbt_data, color_to_analyze):
	if crgbt_data.empty:
		# No data, early return
		return pd.Series([])
	
	actual_output_values = crgbt_data[color_to_analyze]
	one_percent = actual_output_values.mean()/100
	hours_since_experiment_start = (crgbt_data['create_date'] - crgbt_data['create_date'].min()) / pd.Timedelta(hours=1)
	input_temperatures_and_time = pd.DataFrame([crgbt_data['temperature'], hours_since_experiment_start]).T
	
	regression = sklearn.linear_model.Ridge(alpha=0.01, normalize=True)
	regression.fit(
		input_temperatures_and_time,
		actual_output_values,
	)
	
	temperature_slope, time_slope = regression.coef_
	intercept = regression.intercept_
	temperature_prediction = crgbt_data['temperature'] * temperature_slope + intercept
	
	r_squared = regression.score(input_temperatures_and_time, actual_output_values)

	temperature_r_value = scipy.stats.stats.pearsonr(actual_output_values, crgbt_data['temperature'])[0]
	time_r_value = scipy.stats.stats.pearsonr(actual_output_values, hours_since_experiment_start)[0]
	return pd.Series({
		'intercept': intercept,
		'temperature_slope_counts_per_degree': temperature_slope,
		'temperature_slope_pct_per_degree': temperature_slope / one_percent,
		'time_slope_counts_per_12hr': time_slope * 12,
		'time_slope_pct_per_12hr': time_slope / one_percent * 12,
		'temperature_r_value': temperature_r_value,
		'time_r_value': time_r_value,
		'r_squared': r_squared,
		'temperature_correlation': get_correlation_status(temperature_r_value),
		'time_correlation': get_correlation_status(time_r_value),
	})


def analyze_temperature_and_time_correlation_all_colors(crgbt_data):
	return pd.DataFrame({
		color_letter: analyze_temperature_and_time_correlation(crgbt_data, color_letter)
		for color_letter in 'crgb'
	})


def simulate_value(correlation_info_for_color, temperature, elapsed_12_hr_periods):
	temperature_element = correlation_info_for_color['temperature_slope_counts_per_degree'] * temperature
	time_element = correlation_info_for_color['time_slope_counts_per_12hr'] * elapsed_12_hr_periods
	return correlation_info_for_color['intercept'] + temperature_element + time_element
	
def check_r_over_b_effect_with_simulated_fluorescence_reading(correlation_info):
	temperature = 20 # Assume constant temperature / that temperature effects can be factored out using some sweet maths
	elapsed_hours = 12
	elapsed_12_hr_periods = elapsed_hours / 12
	
	# based on 2018-08-14 Neptune DO Calibration with Stocking, a full DO sweep makes about 1100 counts difference in r and 150 counts difference in b
	# Note: it might be better for this to be proportional to the blue signal?
	r_fluorescence = 1100
	b_fluorescence = 150
	
	
	r_initial = simulate_value(correlation_info['r'], temperature=temperature, elapsed_12_hr_periods=0)
	b_initial = simulate_value(correlation_info['b'], temperature=temperature, elapsed_12_hr_periods=0)
	r_later = simulate_value(correlation_info['r'], temperature=temperature, elapsed_12_hr_periods=elapsed_12_hr_periods)
	b_later = simulate_value(correlation_info['b'], temperature=temperature, elapsed_12_hr_periods=elapsed_12_hr_periods)
	
	r_over_b_change_due_to_problem_effect = (r_later / b_later) - (r_initial / b_initial)
	r_over_b_change_due_to_fluorescence = ((r_initial + r_fluorescence) / (b_initial + b_fluorescence)) - (r_initial / b_initial)
	
	noise_as_fraction_of_signal = r_over_b_change_due_to_problem_effect / r_over_b_change_due_to_fluorescence
	return pd.Series({
		'r_initial': r_initial,
		'b_initial': b_initial,
		'r_12hrs_later': r_later,
		'b_12hrs_later': b_later,
		'r_over_b_change_due_to_problem_effect_12hrs': r_over_b_change_due_to_problem_effect,
		'r_over_b_change_due_to_fluorescence': r_over_b_change_due_to_fluorescence,
		'12hrs_noise_as_fraction_of_signal': noise_as_fraction_of_signal,
	})

def check_for_bifurcation(correlation_info):
	if correlation_info.empty:
		# No data, early return
		raise ValueError('no correlation info')
	
	def is_bifurcated(correlation_series):
		# Define "bifurcation" as where one color is convincingly positively correlated with a factor and the others are negatively correlated
		return correlation_series.max() == 1 and correlation_series.min() == -1

	return pd.Series({
		'temperature_bifurcation': is_bifurcated(correlation_info.loc['temperature_correlation']),
		'time_bifurcation': is_bifurcated(correlation_info.loc['time_correlation'])
	})


def get_correlation_and_problem_level_info_for_sensor(node_id, sensor_index, led_code, node_data, visualize=False, **plot_kwargs):
	crgbt_data = clean_crgb_and_temperature_data(node_id, sensor_index, node_data)
	metadata = pd.Series({
		'sensor_index': sensor_index,
		'led_code': led_code,
		'crgbt_rows': len(crgbt_data),
	})
	if crgbt_data.empty:
		# No data, early return
		return metadata
	
	correlation_info = analyze_temperature_and_time_correlation_all_colors(crgbt_data)		

	if visualize:
		plot_relative_crgb_and_temperature(crgbt_data, node_id, sensor_index, correlation_info, **plot_kwargs)
		display(correlation_info)

	bifurcation_and_problem_data = pd.concat([
		check_for_bifurcation(correlation_info),
		check_r_over_b_effect_with_simulated_fluorescence_reading(correlation_info),
	])
	if visualize:
		display(bifurcation_and_problem_data)
		
	return pd.concat([
		metadata,
		correlation_info.stack(),
		bifurcation_and_problem_data
	])

def get_correlation_and_problem_level_info_for_node(
	node_id,
	start_time_local,
	end_time_local,
	led_codes='w,w,w,w,b,b,b,b',
	experiment_is_ongoing=False,
	visualize=False,
	**plot_kwargs
):
	raw_node_data = load_from_db(
		nodes=[node_id],
		start_time_local=start_time_local,
		end_time_local=end_time_local,
		disk_cache=not experiment_is_ongoing
	)
	led_codes_list = led_codes.split(',')
	return pd.DataFrame([
		get_correlation_and_problem_level_info_for_sensor(node_id, sensor_index, led_code, raw_node_data, visualize, **plot_kwargs)
		for sensor_index, led_code in enumerate(led_codes_list)
	])


# !pip install orderedset
from orderedset import OrderedSet
from copy import copy

def order_dataframe_columns(start_columns, dataframe):
	''' Return a new DataFrame with columns reordered such that start_columns come first.
	All other columns will come afterward, in their original order.
	'''
	all_columns = OrderedSet(dataframe.columns)
	
	missing_columns = set(start_columns) - set(all_columns)
	if missing_columns:
		raise ValueError(f'Some of the start columns you asked for {missing_columns} aren\'t present in the DataFrame you passed')
	
	extra_columns = OrderedSet(dataframe.columns) - start_columns
	
	# Must use an index here to support non-string (eg. tuple) column labels
	new_column_order = pd.Index(start_columns + list(extra_columns))
	
	return dataframe[new_column_order]
