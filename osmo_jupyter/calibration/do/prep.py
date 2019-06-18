import pandas as pd

from osmo_jupyter.constants import FRACTION_O2_IN_ATMOSPHERE
from osmo_jupyter.ysi import join_interpolated_ysi_data


def _get_o2_partial_pressure(atmospheric_pressure_mmhg, saturation_percent):
    saturation_fraction = saturation_percent / 100
    return saturation_fraction * FRACTION_O2_IN_ATMOSPHERE * atmospheric_pressure_mmhg


def prep_calibration_data(
    ysi_data_filepath,
    image_data_filepath,
    do_patch_roi_name,
    reference_patch_roi_name,
):
    ''' Prepare data from a calibration experiment for use in curve fitting

    Args:
        ysi_data_filepath: file path to a YSI data file. Must include dissolved oxygen, barometer and temperature data.
        image_data_filepath: file path to ROI summary statistics file from process_experiment
        do_patch_roi_name: ROI name in camera data file to use as sensing patch
        reference_patch_roi_name: ROI name in camera data file to use as control patch

    Returns:
        calibration data set with columns:
            'timestamp'
            'Temperature (C)'
            'DO (mmHg)'
            'DO patch reading': red MSORM from DO patch
            'Reference patch reading': red MSORM from control patch
            'SR reading': spatial ratiometric reading
    '''
    # import YSI data
    ysi_data = pd.read_csv(
        ysi_data_filepath,
        parse_dates=['Timestamp']
    ).set_index('Timestamp')

    # add DO partial pressure
    ysi_data['Dissolved Oxygen (mmHg)'] = _get_o2_partial_pressure(
        atmospheric_pressure_mmhg=ysi_data['Barometer (mmHg)'],
        saturation_percent=ysi_data['Dissolved Oxygen (%)'],
    )

    # Import camera data
    all_camera_data = pd.read_csv(
        image_data_filepath,
        parse_dates=['timestamp']
    )

    # Pull out some choice MSORMs
    r_msorms = all_camera_data.set_index(['timestamp', 'ROI']).unstack()['r_msorm'].reset_index()

    # Join with YSI data and prep for calibration
    desired_ysi_columns = [
        'Temperature (C)',
        'Dissolved Oxygen (mmHg)'
    ]
    msorms_and_ysi_data = join_interpolated_ysi_data(r_msorms, ysi_data[desired_ysi_columns])

    # Let's have a nice clean output DataFrame
    calibration_data_rename = {
        'timestamp': 'timestamp',
        'YSI Temperature (C)': 'Temperature (C)',
        'YSI Dissolved Oxygen (mmHg)': 'DO (mmHg)',
        do_patch_roi_name: 'DO patch reading',
        reference_patch_roi_name: 'Reference patch reading',
    }
    calibration_data_set = (
        msorms_and_ysi_data
        .rename(calibration_data_rename, axis='columns')
        [list(calibration_data_rename.values())]
    )
    calibration_data_set['SR reading'] = calibration_data_set['DO patch reading'] / calibration_data_set[
        'Reference patch reading']
    return calibration_data_set
