import osmo_jupyter.db_access as module
import pytest
import textwrap


node_ids = [123, 456]
start_utc = '2018-08-08 19:00:00'
end_utc = '2018-09-09 20:00:00'


@pytest.mark.parametrize(
    'name, include_hub_id, downsample_factor, query_contents_to_look_for, should_be_present',
    [
        ('base case', False, None, 'SELECT', True),
        ('SELECT clause with both options on', True, 10, 'SELECT calculation_detail.*, reading.hub_id', True),
        ('MOD clause for downsample option', True, 10, 'AND MOD(calculation_detail.reading_id, 10) = 0', True),
        ('MOD clause not present without downsample option', True, None, 'MOD', False),
        ('no JOIN when not including hub ID', False, 10, 'JOIN', False),
    ]
)
def test_get_calculation_details_query_contents_with_options(
    name,
    include_hub_id,
    downsample_factor,
    query_contents_to_look_for,
    should_be_present,
):
    actual_query = module._get_calculation_details_query(
        node_ids,
        start_utc,
        end_utc,
        include_hub_id=include_hub_id,
        downsample_factor=downsample_factor
    )
    if should_be_present:
        assert query_contents_to_look_for.lower() in actual_query.lower()
    else:
        assert query_contents_to_look_for.lower() not in actual_query.lower()


def test_get_calculation_details_query_basic_case():
    actual_query = module._get_calculation_details_query(node_ids, start_utc, end_utc)
    assert textwrap.dedent(actual_query) == textwrap.dedent('''
        SELECT calculation_detail.*
        FROM (calculation_detail)
        WHERE calculation_detail.node_id IN (123, 456)
        AND calculation_detail.create_date BETWEEN "2018-08-09 02:00:00" AND "2018-09-10 03:00:00"

        ORDER BY calculation_detail.create_date
    ''')
