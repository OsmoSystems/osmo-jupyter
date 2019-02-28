import pandas as pd


def _guard_index_is_datetime(ysi_data):
    if not isinstance(ysi_data.index, pd.DatetimeIndex):
        raise ValueError(
            '''
            ysi_data must be a DataFrame indexed by pre-parsed timestamps. Get this with, eg.:
                pd.read_csv(
                    <YSI filename>,
                    parse_dates=['Timestamp']
                ).set_index('Timestamp')
            '''
        )


def _guard_no_fractional_seconds(datetime_series):
    if any([t.microsecond for t in datetime_series]):
        raise ValueError(
            '''
            Data joining does not work if timestamps have fractional seconds.
            (If you get this error, ask a dev - we can fix it)
            '''
        )


def join_nearest_ysi_data(
    other_data,
    ysi_data,
    other_data_timestamp_column='timestamp'
):
    '''
    Params:
        other_data: DataFrame with a timestamp column to be augmented with YSI data
        ysi_data: DataFrame from YSI. Should be indexed by pre-parsed timestamps. Get this with, eg.:
            pd.read_csv(
                <YSI filename>,
                parse_dates=['Timestamp']
            ).set_index('Timestamp')
        other_data_timestamp_column: column name in other_data containing pre-parsed timestamps.
            Default: 'timestamp'. Pass None to use the index.
    Return:
        DataFrame with each row in other_data augmented with the closest-timestamp data from the YSI.
        Discards "other_data" that is collected outside of the timerange of the YSI data.
        YSI columns will be prefixed with 'YSI ' (e.g. 'YSI Dissolved Oxygen (%)')
    '''
    _guard_index_is_datetime(ysi_data)
    _guard_no_fractional_seconds(other_data[other_data_timestamp_column])

    # TODO:
    #  - consider: what happens for really long data sets? Will resampling to 1s use up all the memory?
    #     - could do an outer join on both and combine the timestamp columns before interpolating.
    #     - Could then just call interpolate w/o resampling
    #  - test in jupyter notebooks
    #  - a bit more commenting

    # Upsample YSI data to allow any timestamp to be joined on a strict match
    resampled_ysi_data = (
        ysi_data
        .add_prefix('YSI ')
        .resample('s')
        .interpolate(method='nearest')
    )
    return other_data.join(
        resampled_ysi_data,
        how='inner',  # Drop superfluous YSI rows and "other" rows outside of YSI timerange
        on=other_data_timestamp_column,
    ).reset_index(drop=True)  # Drop and reset the old "other" index, as some "other" rows may have been discarded
