""" Functions to access node data from the Osmo database
"""
import dateutil
import pandas as pd
import pytz
import sqlalchemy

import textwrap
from getpass import getpass
from osmo_jupyter import timezone


def configure_database():
    """ Configure a database object for read-only technician access to Osmo data.
    Requires user input to collect database password.

    Returns:
        sqlalchemy Engine object which can be used with other functions in this module.
    Raises:
        ValueError: if connection can't be made, usually because password is incorrect
    """
    print("Enter database password: (if you don't know it, ask someone who does)")
    db_engine = sqlalchemy.create_engine(
        "mysql+pymysql://{user}:{password}@{host}/{dbname}".format(
            user="technician",
            password=getpass(),  # Ask user for the password to avoid checking it in.
            dbname="osmobot",
            host="osmobot-db2.cxvkrr48hefm.us-west-2.rds.amazonaws.com",
        )
    )
    try:
        connection = db_engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        raise ValueError(
            textwrap.dedent(
                f"""Couldn't connect to the database - most likely you typed the password incorrectly.
                Please try again.\n Original error: {e}
            """
            )
        )
    else:
        connection.close()
    return db_engine


SQL_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # Time format favored by mysql


def _to_aware(local_time):
    """ get a timezone-aware object from local time string(s).
    Internal function, used only in DB access.

    Args:
        local_time: string of local time in any valid non-timezone-aware ISO format
            Time should be in Osmo HQ local time.
            eg. ('2012-01-01 12:00:00', '2012-01-01 12:00', '2012-01-01')
    Returns:
        timezone-aware datetime object
    """
    time = dateutil.parser.isoparse(local_time)
    return timezone.OSMO_HQ_TIMEZONE.localize(time)


def _to_utc_string(local_time):
    """ Convert a local time string to a string in UTC that can be passed to the database
    Internal function, used only in DB access.

    Args:
        local_time: string of local time in any valid non-timezone-aware ISO format
            Time should be in Osmo HQ local time.
            eg. ('2012-01-01 12:00:00', '2012-01-01 12:00', '2012-01-01')
    Returns:
        UTC time string that can be used, for instance, for database queries
    """
    aware_datetime = _to_aware(local_time)
    return aware_datetime.astimezone(pytz.utc).strftime(SQL_TIME_FORMAT)


def _get_calculation_details_query(
    node_ids,
    start_time_local,
    end_time_local,
    include_hub_id=False,
    downsample_factor=None,
):
    """ Provide a SQL query to download calculation details. Internal function

    Args:
        node_ids: iterable of node IDs to get data for
        start_time_local: string of ISO-formatted start datetime in local time, inclusive
        end_time_local: string of ISO-formatted end datetime in local time, inclusive
        include_hub_id: if True, the output will include a 'hub_id' column.
            Default False because the request including hub_id takes extra time.
        downsample_factor: if this is a number, it will be used to select fewer rows.
            You should get *roughly* n / downsample_factor samples. If None, no downsampling will occur.
    Returns:
        SQL query that can be used to get the desired data
    """

    start_utc_string = _to_utc_string(start_time_local)
    end_utc_string = _to_utc_string(end_time_local)
    downsample_clause = (
        f"AND MOD(calculation_detail.reading_id, {downsample_factor}) = 0"
        if downsample_factor is not None
        else ""
    )

    select_clause = (
        "calculation_detail.*, reading.hub_id"
        if include_hub_id
        else "calculation_detail.*"
    )
    source_table = (
        "calculation_detail join reading on reading.reading_id = calculation_detail.reading_id"
        if include_hub_id
        else "calculation_detail"
    )
    nodes_selector = "({})".format(", ".join(str(n) for n in node_ids))

    return f"""
        SELECT {select_clause}
        FROM ({source_table})
        WHERE calculation_detail.node_id IN {nodes_selector}
        AND calculation_detail.create_date BETWEEN "{start_utc_string}" AND "{end_utc_string}"
        {downsample_clause}
        ORDER BY calculation_detail.create_date
    """


def load_calculation_details(
    db_engine,
    node_ids,
    start_time_local,
    end_time_local,
    include_hub_id=False,
    downsample_factor=None,
):
    """ Load node data from the calculation_details table, optionally with hub ID included from the readings table

    Args:
        db_engine: database engine created using `connect_to_db`
        node_ids: iterable of node IDs to get data for
        start_time_local: string of ISO-formatted start datetime in local time, inclusive
        end_time_local: string of ISO-formatted end datetime in local time, inclusive
        include_hub_id: if True, the output will include a 'hub_id' column.
            Default False because the request including hub_id takes extra time.
        downsample_factor: if this is a number, it will be used to select fewer rows.
            You should get *roughly* n / downsample_factor samples.
    Returns:
        a pandas.DataFrame of data from the node IDs provided.
    Raises:
        sqlalchemy.OperationalError: database connection is not working
            This is often due to a network disconnect.
            In this case, a good debugging step is to reconnect to the database.
    """

    connection = db_engine.connect()

    calculation_details = pd.read_sql(
        _get_calculation_details_query(
            node_ids,
            start_time_local,
            end_time_local,
            include_hub_id,
            downsample_factor,
        ),
        db_engine,
    )
    connection.close()
    return calculation_details


def get_node_temperature_data(
    start_time_local, end_time_local, node_id, downsample_factor=1
):
    """ Load node temperature data only from the calculation_details table

    Args:
        start_time_local: string of ISO-formatted start datetime in local time, inclusive
        end_time_local: string of ISO-formatted end datetime in local time, inclusive
        node_id: node ID to get data from
        downsample_factor: if this is a number, it will be used to select fewer rows.
            You should get *roughly* n / downsample_factor samples.
    Returns:
        a pandas.DataFrame of temperature data (°C) in local time from the node IDs provided.
    """

    db_engine = configure_database()

    raw_node_data = load_calculation_details(
        db_engine, [node_id], start_time_local, end_time_local, downsample_factor
    )

    print(f"{len(raw_node_data)} rows retrieved.")

    temperature_data = raw_node_data[
        raw_node_data["calculation_dimension"] == "temperature"
    ]

    temperature_data_only = pd.DataFrame(
        {
            "timestamp": timezone.utc_series_to_local(temperature_data["create_date"]),
            "temperature": temperature_data["calculated_value"],
        }
    ).reset_index(drop=True)

    return temperature_data_only
