# import pytest
from unittest.mock import sentinel

import osmo_jupyter.simulate.plot as module


class TestGetMeshgridOfDoAndTemp:
    def test_meshgrid_shape_matches(self):
        def _mock_fn_of_do_and_temp(do, temp):
            return sentinel.mock_value

        actual = module.get_meshgrid_of_do_and_temp(_mock_fn_of_do_and_temp)

        assert actual.shape == (len(module.DO_DOMAIN), len(module.TEMPERATURE_DOMAIN))
        assert actual.shape == module.DO_MESHGRID.shape == module.TEMPERATURE_MESHGRID.shape
