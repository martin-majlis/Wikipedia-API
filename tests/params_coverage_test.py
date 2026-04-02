from unittest.mock import Mock

import pytest

from wikipediaapi._enums import CoordinateType
from wikipediaapi._params import CoordinatesParams
from wikipediaapi._params import GeoSearchParams
from wikipediaapi._params import RandomParams
from wikipediaapi._params import SearchParams
from wikipediaapi._params import _BaseParams
from wikipediaapi._types import GeoPoint


class TestParamsCoverage:
    """Test coverage for missing lines in _params.py."""

    def test_base_params_bool_true(self):
        """Test line 79: boolean True handling."""
        params = _BaseParams()
        params.test_bool = True
        params.FIELD_MAP = {"test_bool": "test_bool"}  # ty: ignore[invalid-attribute-access]
        result = params.to_api()
        assert result["test_bool"] == "1"

    def test_base_params_bool_false(self):
        """Test boolean False handling (should not be included)."""
        params = _BaseParams()
        params.test_bool = False
        params.FIELD_MAP = {"test_bool": "test_bool"}  # ty: ignore[invalid-attribute-access]
        result = params.to_api()
        assert "test_bool" not in result

    def test_base_params_enum_handling(self):
        """Test line 82: Enum handling."""
        from enum import Enum

        class TestEnum(Enum):
            VALUE = "test_value"

        params = _BaseParams()
        params.test_enum = TestEnum.VALUE
        params.FIELD_MAP = {"test_enum": "test_enum"}  # ty: ignore[invalid-attribute-access]
        result = params.to_api()
        assert result["test_enum"] == "test_value"

    def test_coordinates_params_invalid_type(self):
        """Test line 137: TypeError for invalid primary type."""
        with pytest.raises(TypeError) as excinfo:
            CoordinatesParams(primary=123, prop=[])
        assert "CoordinatesParams.primary must be CoordinateType or str" in str(excinfo.value)

    def test_coordinates_params_distance_from_page(self):
        """Test line 155: distance_from_page conversion."""
        mock_page = Mock()
        mock_page.title = "Test_Page"

        from wikipediaapi._enums import CoordinatesProp

        params = CoordinatesParams(
            primary=CoordinateType.ALL, prop=[CoordinatesProp.TYPE], distance_from_page=mock_page
        )
        # Access attribute directly to test line 155 conversion to string
        assert params.distance_from_page == "Test_Page"

    def test_geosearch_params_invalid_sort(self):
        """Test line 251: TypeError for invalid sort type."""
        with pytest.raises(TypeError) as excinfo:
            GeoSearchParams(coord=GeoPoint(lat=51.5, lon=-0.1), sort=123)
        assert "GeoSearchParams.sort must be GeoSearchSort or str" in str(excinfo.value)

    def test_geosearch_params_invalid_globe(self):
        """Test line 255: TypeError for invalid globe type."""
        with pytest.raises(TypeError) as excinfo:
            GeoSearchParams(coord=GeoPoint(lat=51.5, lon=-0.1), globe=123)
        assert "GeoSearchParams.globe must be Globe or str" in str(excinfo.value)

    def test_geosearch_params_invalid_primary(self):
        """Test line 259: TypeError for invalid primary type."""
        with pytest.raises(TypeError) as excinfo:
            GeoSearchParams(coord=GeoPoint(lat=51.5, lon=-0.1), primary=123)
        assert "GeoSearchParams.primary must be CoordinateType or str" in str(excinfo.value)

    def test_random_params_invalid_filter(self):
        """Test line 283: TypeError for invalid filter type."""
        with pytest.raises(TypeError) as excinfo:
            RandomParams(filter_redirect=123)
        assert "RandomParams.filter_redirect must be RedirectFilter or str" in str(excinfo.value)

    def test_search_params_invalid_sort(self):
        """Test line 371: TypeError for invalid sort type."""
        with pytest.raises(TypeError) as excinfo:
            SearchParams(sort=123)
        assert "SearchParams.sort must be SearchSort or str" in str(excinfo.value)

    def test_coordinates_params_prop_string_error(self):
        """Test TypeError for prop as string."""
        with pytest.raises(TypeError) as excinfo:
            CoordinatesParams(primary=CoordinateType.ALL, prop="invalid_string")
        assert "CoordinatesParams.prop must be an iterable" in str(excinfo.value)
