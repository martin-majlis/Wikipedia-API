import unittest
from unittest.mock import Mock

from wikipediaapi._enums import CoordinateType
from wikipediaapi._params import _BaseParams
from wikipediaapi._params import CoordinatesParams
from wikipediaapi._params import GeoSearchParams
from wikipediaapi._params import RandomParams
from wikipediaapi._params import SearchParams
from wikipediaapi._types import GeoPoint


class TestParamsCoverage(unittest.TestCase):
    """Test coverage for missing lines in _params.py."""

    def test_base_params_bool_true(self):
        """Test line 79: boolean True handling."""
        params = _BaseParams()
        params.test_bool = True
        params.FIELD_MAP = {"test_bool": "test_bool"}
        result = params.to_api()
        self.assertEqual(result["test_bool"], "1")

    def test_base_params_bool_false(self):
        """Test boolean False handling (should not be included)."""
        params = _BaseParams()
        params.test_bool = False
        params.FIELD_MAP = {"test_bool": "test_bool"}
        result = params.to_api()
        self.assertNotIn("test_bool", result)

    def test_base_params_enum_handling(self):
        """Test line 82: Enum handling."""
        from enum import Enum

        class TestEnum(Enum):
            VALUE = "test_value"

        params = _BaseParams()
        params.test_enum = TestEnum.VALUE
        params.FIELD_MAP = {"test_enum": "test_enum"}
        result = params.to_api()
        self.assertEqual(result["test_enum"], "test_value")

    def test_coordinates_params_invalid_type(self):
        """Test line 137: TypeError for invalid primary type."""
        with self.assertRaises(TypeError) as cm:
            CoordinatesParams(primary=123, prop=[])
        self.assertIn("CoordinatesParams.primary must be CoordinateType or str", str(cm.exception))

    def test_coordinates_params_distance_from_page(self):
        """Test line 155: distance_from_page conversion."""
        mock_page = Mock()
        mock_page.title = "Test_Page"

        from wikipediaapi._enums import CoordinatesProp

        params = CoordinatesParams(
            primary=CoordinateType.ALL, prop=[CoordinatesProp.TYPE], distance_from_page=mock_page
        )
        # Access the attribute directly to test line 155 conversion to string
        self.assertEqual(params.distance_from_page, "Test_Page")

    def test_geosearch_params_invalid_sort(self):
        """Test line 251: TypeError for invalid sort type."""
        with self.assertRaises(TypeError) as cm:
            GeoSearchParams(coord=GeoPoint(lat=51.5, lon=-0.1), sort=123)
        self.assertIn("GeoSearchParams.sort must be GeoSearchSort or str", str(cm.exception))

    def test_geosearch_params_invalid_globe(self):
        """Test line 255: TypeError for invalid globe type."""
        with self.assertRaises(TypeError) as cm:
            GeoSearchParams(coord=GeoPoint(lat=51.5, lon=-0.1), globe=123)
        self.assertIn("GeoSearchParams.globe must be Globe or str", str(cm.exception))

    def test_geosearch_params_invalid_primary(self):
        """Test line 259: TypeError for invalid primary type."""
        with self.assertRaises(TypeError) as cm:
            GeoSearchParams(coord=GeoPoint(lat=51.5, lon=-0.1), primary=123)
        self.assertIn("GeoSearchParams.primary must be CoordinateType or str", str(cm.exception))

    def test_random_params_invalid_filter(self):
        """Test line 283: TypeError for invalid filter type."""
        with self.assertRaises(TypeError) as cm:
            RandomParams(filter_redirect=123)
        self.assertIn(
            "RandomParams.filter_redirect must be RedirectFilter or str", str(cm.exception)
        )

    def test_search_params_invalid_sort(self):
        """Test line 371: TypeError for invalid sort type."""
        with self.assertRaises(TypeError) as cm:
            SearchParams(sort=123)
        self.assertIn("SearchParams.sort must be SearchSort or str", str(cm.exception))

    def test_coordinates_params_prop_string_error(self):
        """Test TypeError for prop as string."""
        with self.assertRaises(TypeError) as cm:
            CoordinatesParams(primary=CoordinateType.ALL, prop="invalid_string")
        self.assertIn("CoordinatesParams.prop must be an iterable", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
