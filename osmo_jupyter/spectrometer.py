import pandas as pd
import io


SPECTRAL_DATA_IDENTIFIER = '>>>>>Begin Spectral Data<<<<<'


def _import_spectrometer_txt(spectrometer_data_file_path):
    # The raw spectrometer file contains mixed "\r\n" and "\n" line endings
    # Open file with newline=None to ensure all line endings are "\n"
    with open(spectrometer_data_file_path, 'r', newline=None) as infile:
        # Read through file metadata until we find the marker that identifies the start of the tab-delimited data
        for line in infile:
            if line.strip() == SPECTRAL_DATA_IDENTIFIER:
                unformatted_spectrometer_df = pd.read_csv(
                    io.StringIO(infile.read()),
                    sep='\t',
                    lineterminator='\n',
                )

                return unformatted_spectrometer_df
        raise ValueError('Spectrometer data not in expected format; check the file header')


def _clean_up_spectrometer_df_header(unformatted_spectrometer_df):

    ''' Cleans up header of raw spectrometer df, and removes redundant timestamp column.

    Args:
        unformatted_spectrometer_df: a pandas df of original spectrometer data,
            imported with _import_spectrometer_txt()

    Return:
        A pandas df with a sensible header, and only one timestamp column
    '''

    timestamp_column, epoch_column = unformatted_spectrometer_df.columns[[0, 1]]
    spectrometer_df_with_clean_header = unformatted_spectrometer_df.rename(
        # timestamp column is in local time, epoch_time column is in UTC
        columns={
            timestamp_column: 'timestamp',
            epoch_column: 'epoch_time'
        }
    )
    # 'epoch_time' column is redundant to 'timestamp' column. Remove it
    spectrometer_df_with_clean_header.drop(['epoch_time'], axis=1, inplace=True)

    return spectrometer_df_with_clean_header


def _reformat_spectrometer_df(spectrometer_df_with_clean_header):
    ''' Reformats a df of spectrometer data with many wavelength columns,to a more useful format with 2 columns

    Args:
        spectrometer_df_with_clean_header: a pandas df of spectrometer data,
            cleaned up with _clean_up_spectrometer_df_header()

    Return:
        A pandas df, indexed by timestamp, with 2 columns: wavelength and intensity
    '''

    n_timestamp_columns = 1
    wavelength_columns = spectrometer_df_with_clean_header.columns[n_timestamp_columns:]
    # melt function is a pivot and turns 3648 columns, each one wavelength, into one column
    reformatted_spectrometer_df = spectrometer_df_with_clean_header.melt(
        id_vars=['timestamp'],
        value_vars=wavelength_columns,
        var_name='wavelength',
        value_name='intensity'
    )
    reformatted_spectrometer_df['wavelength'] = reformatted_spectrometer_df['wavelength'].astype(float)

    return reformatted_spectrometer_df.set_index(['timestamp'])


def import_and_format_spectrometer_data(spectrometer_data_file_path):
    ''' Imports and reformats a raw spectrometer data file to be useful and efficient for notebooks

    Args:
        spectrometer_data_file_path: file path to .txt file produce by oceanview software in the format
            'Time Series (column data)'

    Return:
        A pandas df, indexed by timestamp, with 2 columns: wavelength and intensity
    '''
    unformatted_spectrometer_df = _import_spectrometer_txt(spectrometer_data_file_path)
    spectrometer_df_with_clean_header = _clean_up_spectrometer_df_header(unformatted_spectrometer_df)
    reformatted_spectrometer_df = _reformat_spectrometer_df(spectrometer_df_with_clean_header)

    return reformatted_spectrometer_df


MIN_SPECTROMETER_WAVELENGTH = 340
MAX_SPECTROMETER_WAVELENGTH = 1035


def spectrometer_intensity_summary(reformatted_spectrometer_df,
                                   minimum_wavelength=MIN_SPECTROMETER_WAVELENGTH,
                                   maximum_wavelength=MAX_SPECTROMETER_WAVELENGTH):
    ''' Creates intensity summary (mean) of spectrometer data over some spectrum of wavelengths.

    Args:
        reformatted_spectrometer_df: pandas df of spectrometer data formatted by import_and_format_spectrometer_data()
        minimum_wavelength (optional): sets a lower bound for range over which wavelengths will be summarized
        maximum_wavelength (optional): sets an upper bound for range over which wavelengths will be summarized

    Return:
        A pandas df, indexed by timestamp, with 1 intensity column that summarizes (calculates mean) intensity
            data over some spectrum
    '''

    relevant_wavelengths = reformatted_spectrometer_df['wavelength'].between(minimum_wavelength, maximum_wavelength)
    filtered_spectrometer_data = reformatted_spectrometer_df[relevant_wavelengths]

    # Question whether or not this function should perform a mean for its summary. A mean, sum and integral all
    # produce the same relative change over time, only with different units. An integral may provide us with a
    # physically useful unit (radiance) but it seems that our spectrometer is not calibrated for measuring radiance,
    # so this operation would likely give us a unit close to something useful, but technically arbitrary.
    # Although mean provides arbitrary units, it makes data comparable to tests from the past, so keeping for now.
    intensity_summary = filtered_spectrometer_data.groupby(['timestamp']).mean().drop(['wavelength'], axis=1)

    return intensity_summary
