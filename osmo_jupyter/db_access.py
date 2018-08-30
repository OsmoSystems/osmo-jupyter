import textwrap
from getpass import getpass

import pandas as pd
import sqlalchemy


def configure_database():
    """ Configure a database object for read-only technician access to Osmo data.
    Requries user input to collect database password.

    Returns:
        sqlalchemy Engine object which can be used with other functions in this module.
    Raises:
        ValueError: if connection can't be made, usually because password is incorrect
    """
    print('Enter database password: (if you don\'t know it, ask someone who does)')
    db_engine = sqlalchemy.create_engine(
        'mysql+pymysql://{user}:{password}@{host}/{dbname}'.format(
            user='technician',
            password=getpass(),
            dbname='osmobot',
            host='osmobot-db2.cxvkrr48hefm.us-west-2.rds.amazonaws.com'
        )
    )
    try:
        connection = db_engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        raise ValueError(textwrap.dedent(
            f'''Couldn't connect to the database - most likely you typed the password incorrectly.
                Please try again.\n Original error: {e}
            '''
        ))
    else:
        connection.close()
    return db_engine


def _get_calculation_details_query(node_ids, start_utc, end_utc, include_hub_id=False, downsample_interval=None):
    """ Provide a SQL query to download calculation details. Internal function

    Args:
        node_ids: iterable of node IDs to get data for
        # TODO (PR feedback plz): establish safe patterns for use of local time and use that instead
        start_utc: string of ISO-formatted start datetime in UTC, inclusive
        end_utc: string of ISO-formatted end datetime in UTC, inclusive
        include_hub_id: if True, the output will include a 'hub_id' column.
            Default False because the request including hub_id takes extra time.
        downsample_interval: if this is a number, it will be used to select fewer rows.
            You should get *roughly* n / downsample_interval samples. If None, no downsampling will occur.
    Returns:
        SQL query that can be used to get the desired data
    """
    downsample_clause = (
        f'AND MOD(calculation_detail.reading_id, {downsample_interval}) = 0'
        if downsample_interval is not None
        else ''
    )

    select_clause = (
        'calculation_detail.*, reading.hub_id'
        if include_hub_id
        else 'calculation_detail.*'
    )
    source_table = (
        'calculation_detail join reading on reading.reading_id = calculation_detail.reading_id'
        if include_hub_id
        else 'calculation_detail'
    )
    nodes_selector = '({})'.format(', '.join(str(n) for n in node_ids))

    return f'''
        SELECT {select_clause}
        FROM ({source_table})
        WHERE calculation_detail.node_id IN {nodes_selector}
        AND calculation_detail.create_date BETWEEN "{start_utc}" AND "{end_utc}"
        {downsample_clause}
        ORDER BY calculation_detail.create_date
    '''


def load_calculation_details(db_engine, node_ids, start_utc, end_utc, include_hub_id=False, downsample_interval=None):
    """ Load node data from the calculation_details table, optionally with hub ID included from the readings table

    Args:
        db_engine: database engine created using `connect_to_db`
        node_ids: iterable of node IDs to get data for
        start_utc: string of ISO-formatted start datetime in UTC, inclusive
        end_utc: string of ISO-formatted end datetime in UTC, inclusive
        include_hub_id: if True, the output will include a 'hub_id' column.
            Default False because the request including hub_id takes extra time.
        downsample_interval: if this is a number, it will be used to select fewer rows.
            You should get *roughly* n / downsample_interval samples.
    Returns:
        a pandas.DataFrame of data from the node IDs provided.
    Raises:
        sqlalchemy.OperationalError: database connection is not working
            This is often due to wrong password or network disconnect.
            In this case, a good debugging step is to reconnect to the database.
    """

    connection = db_engine.connect()

    calculation_details = pd.read_sql(
        _get_calculation_details_query(node_ids, start_utc, end_utc, include_hub_id, downsample_interval),
        db_engine
    )
    connection.close()
    return calculation_details
