import pandas as pd
import io


def _import_spectrometer_txt(spectrometer_data_file_path):
    with open(spectrometer_data_file_path, 'r', newline=None) as infile:
        for line in infile:
            if line.strip() == '>>>>>Begin Spectral Data<<<<<':
                file_content_with_unix_endings = infile.read()
                unformatted_spectrometer_data = pd.read_csv(
                    io.StringIO(file_content_with_unix_endings),
                    sep='\t',
                    lineterminator='\n',
                )

                return unformatted_spectrometer_data
        raise ValueError('Spectrometer data not in expected format; check the file header')


def _clean_up_spectrometer_data_header(unformatted_spectrometer_data):

    ''' Cleans up header of raw spectrometer data, and removes redundant timestamp column.

    Args:
        unformatted_spectrometer_data: a pandas df of original spectrometer data,
            imported with _import_spectrometer_txt()

    Return:
        A pandas dataframe with a sensible header, and only one timestamp column
    '''

    timestamp_column, epoch_column = unformatted_spectrometer_data.columns[[0, 1]]
    spectrometer_data_with_clean_header = unformatted_spectrometer_data.rename(
        # timestamp column is in local time, epoch_time column is in UTC
        columns={
            timestamp_column: 'timestamp',
            epoch_column: 'epoch_time'
        }
    )
    # Remove redundant timestamp column
    spectrometer_data_with_clean_header.drop(['epoch_time'], axis=1, inplace=True)

    return spectrometer_data_with_clean_header


def _reformat_spectrometer_data(spectrometer_data_with_clean_header):
    ''' Reformats a df of spectrometer data with many wavelength columns,to a more useful format with 2 columns

    Args:
        spectrometer_data_with_clean_header: a pandas df of spectrometer data,
            cleaned up with _clean_up_spectrometer_data_header()

    Return:
        A pandas df, indexed by timestamp, with 2 columns: wavelength and intensity
    '''

    n_timestamp_columns = 1
    wavelength_columns = spectrometer_data_with_clean_header.columns[n_timestamp_columns:]
    # melt function is a pivot and turns 3648 columns, each one wavelength, into one column
    reformatted_spectrometer_data = spectrometer_data_with_clean_header.melt(
        id_vars=['timestamp'],
        value_vars=wavelength_columns,
        var_name='wavelength',
        value_name='intensity'
    )
    reformatted_spectrometer_data['wavelength'] = reformatted_spectrometer_data['wavelength'].astype(float)

    return reformatted_spectrometer_data.set_index(['timestamp'])


def import_and_format_spectrometer_data(spectrometer_data_file_path):
    ''' Imports and reformats a raw spectrometer data file to be useful and efficient for notebooks

    Args:
        spectrometer_data_file_path: file path to .txt file produce by oceanview software in the format
            'Time Series (column data)'

    Return:
        A pandas dataframe, indexed by timestamp, with 2 columns: wavelength and intensity
    '''
    unformatted_spectrometer_data = _import_spectrometer_txt(spectrometer_data_file_path)
    spectrometer_data_with_clean_header = _clean_up_spectrometer_data_header(unformatted_spectrometer_data)
    reformatted_spectrometer_data = _reformat_spectrometer_data(spectrometer_data_with_clean_header)

    return reformatted_spectrometer_data


def spectrometer_intensity_summary(reformatted_spectrometer_data, minimum_wavelength=340, maximum_wavelength=1035):
    ''' Creates intensity summary (mean) of spectrometer data over some spectrum of wavelengths.

    Args:
        reformatted_spectrometer_data: pandas df of spectrometer data formatted by import_and_format_spectrometer_data()
        minimum_wavelength (optional): sets a lower bound for range over which wavelengths will be summarized
        maximum_wavelength (optional): sets an upper bound for range over which wavelengths will be summarized

    Return:
        A pandas df, indexed by timestamp, with 1 intensity column that summarizes (calculates mean) intensity
            data over some spectrum
    '''

    relevant_wavelengths = reformatted_spectrometer_data['wavelength'].between(minimum_wavelength, maximum_wavelength)
    filtered_spectrometer_data = reformatted_spectrometer_data[relevant_wavelengths]

    # Question whether or not this should be mean. An integral may relate more closely to a useful unit
    intensity_summary = filtered_spectrometer_data.groupby(['timestamp']).mean().drop(['wavelength'], axis=1)

    return intensity_summary
