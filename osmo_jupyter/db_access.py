
def connect_to_db():
    # TODO

def load_calculation_details(db_engine, node_ids, start_utc, end_utc, include_hub_id=False, downsample_interval=None):
    """ Load node data from the calculation_details table, optionally with hub ID included from the readings table

    Args:
        db_engine: database engine created using `connect_to_db`
        node_ids: iterable of node IDs to get data for
        start_utc: string of ISO-formatted start datetime in UTC, inclusive # TODO (PR feedback plz): establish safe patterns for use of local time and use that instead
        end_utc: string of ISO-formatted end datetime in UTC, inclusive
        include_hub_id: if True, the output will include a 'hub_id' column. Default False because the request including hub_id takes extra time.
        downsample_interval: if this is a number, it will be used to select fewer rows. You should get *roughly* n / downsample_interval samples.
    Returns:
        a pandas.DataFrame of data from the node IDs provided.
    Raises:
        sqlalchemy.OperationalError: database connection is not working (often due to wrong password or network disconnect). In this case, a good debugging step is to reconnect to the database.
    """

    connection = db_engine.connect()

    # TODO? (PR feedback plz): it feels like there's already a fair amount of logic in constructing this query; I could factor out a construct_node_data_query() function here for unit testing
    downsample_clause = f'AND MOD(calculation_detail.reading_id, {downsample_interval}) = 0' if downsample_interval is not None else ''

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
    nodes_selector = '({})'.format(', '.join(str(n) for n in node_ids)

    calculation_details = pd.read_sql(
        f'''
            SELECT {select_clause}
            FROM ({source_table})
            WHERE calculation_detail.node_id IN {nodes_selector}
            AND calculation_detail.create_date BETWEEN "{start_utc}" AND "{end_utc}"
            {downsample_clause}
            ORDER BY calculation_detail.create_date
        ''',
        db_engine
    )
    connection.close()
    return calculation_details
