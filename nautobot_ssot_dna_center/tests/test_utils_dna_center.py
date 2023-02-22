"""Tests of DNA Center utility methods."""

from unittest.mock import MagicMock
from nautobot.utilities.testing import TestCase
from nautobot_ssot_dna_center.tests.fixtures import (
    DEVICE_DETAIL_FIXTURE,
    DEVICE_FIXTURE,
    RECV_DEVICE_DETAIL_FIXTURE,
    RECV_DEVICE_FIXTURE,
    LOCATION_FIXTURE,
    RECV_LOCATION_FIXTURE,
    RECV_PORT_FIXTURE,
    PORT_FIXTURE,
)
from nautobot_ssot_dna_center.utils.dna_center import DnaCenterClient


class TestDnaCenterClient(TestCase):  # pylint: disable=too-many-public-methods
    """Test DNA Center Client and Calls."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Setup DNAC instance."""
        self.uri = "https://dnac.testexample.com"
        self.username = "testuser"
        self.password = "testpassword"  # nosec B105
        self.verify = False
        self.dnac = DnaCenterClient(self.uri, self.username, self.password, verify=self.verify)
        self.dnac.conn = MagicMock()

    def test_get_locations(self):
        """Test the get_locations method in DnaCenterClient."""
        self.dnac.conn.sites.get_site.return_value = RECV_LOCATION_FIXTURE
        actual = self.dnac.get_locations()
        self.assertEqual(actual, LOCATION_FIXTURE)

    def test_find_address_and_type(self):
        """Test the find_address_and_type method in DnaCenterClient."""
        mock_info = [
            {
                "attributes": {
                    "address": "123 Main St, New York, NY 12345",
                    "country": "United States",
                    "latitude": "38.581405819248886",
                    "longitude": "-121.49309067224416",
                    "type": "building",
                },
                "nameSpace": "Location",
            }
        ]
        actual = self.dnac.find_address_and_type(info=mock_info)
        expected = ("123 Main St, New York, NY 12345", "building")
        self.assertEqual(actual, expected)

    def test_find_latitude_and_longitude(self):
        """Test the find_latitude_and_longitude method in DnaCenterClient."""
        mock_info = [
            {
                "attributes": {
                    "latitude": "38.581405819248886",
                    "longitude": "-121.49309067224416",
                },
                "nameSpace": "Location",
            }
        ]
        actual = self.dnac.find_latitude_and_longitude(info=mock_info)
        expected = ("38.581405819248886", "-121.49309067224416")
        self.assertEqual(actual, expected)

    def test_get_devices(self):
        """Test the get_devices method in DnaCenterClient."""
        self.dnac.conn.devices.get_device_list.return_value = RECV_DEVICE_FIXTURE
        actual = self.dnac.get_devices()
        self.assertEqual(actual, DEVICE_FIXTURE)

    def test_get_device_detail(self):
        """Test the get_device_detail method in DnaCenterClient."""
        self.dnac.conn.devices.get_device_detail.return_value = RECV_DEVICE_DETAIL_FIXTURE
        actual = self.dnac.get_device_detail(dev_id="1234567890")
        self.assertEqual(actual, DEVICE_DETAIL_FIXTURE)

    def test_parse_site_hierarchy(self):
        """Test the parse_site_hierarchy method in DnaCenterClient."""
        mock_location_map = {
            "1": {
                "loc_type": "area",
                "name": "Global",
            },
            "2": {
                "loc_type": "area",
                "name": "NY",
            },
            "3": {
                "loc_type": "building",
                "name": "Building1",
            },
            "4": {"loc_type": "floor", "name": "Floor1"},
        }
        actual = self.dnac.parse_site_hierarchy(location_map=mock_location_map, site_hier="1/2/3/4")
        expected = {
            "areas": ["Global", "NY"],
            "building": "Building1",
            "floor": "Floor1",
        }
        self.assertEqual(actual, expected)

    def test_get_port_info(self):
        """Test the get_port_info method in DnaCenterClient."""
        self.dnac.conn.devices.get_interface_info_by_id.return_value = RECV_PORT_FIXTURE
        actual = self.dnac.get_port_info(device_id="1234567890")
        self.assertEqual(actual, PORT_FIXTURE)
