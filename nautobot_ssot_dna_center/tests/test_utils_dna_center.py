"""Tests of DNA Center utility methods."""

from unittest.mock import MagicMock, patch, create_autospec
from requests import Response
from parameterized import parameterized
from nautobot.utilities.testing import TestCase
from dnacentersdk.exceptions import dnacentersdkException
from nautobot_ssot_dna_center.tests.fixtures import (
    DEVICE_DETAIL_FIXTURE,
    DEVICE_FIXTURE,
    LOCATION_FIXTURE,
    PORT_FIXTURE,
    RECV_DEVICE_DETAIL_FIXTURE,
    RECV_DEVICE_FIXTURE,
    RECV_LOCATION_FIXTURE,
    RECV_PORT_FIXTURE,
)
from nautobot_ssot_dna_center.utils.dna_center import DnaCenterClient


class TestDnaCenterClient(TestCase):  # pylint: disable=too-many-public-methods
    """Test DNA Center Client and Calls."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Setup DNAC instance."""
        self.url = "https://dnac.testexample.com"
        self.username = "testuser"
        self.password = "testpassword"  # nosec B105
        self.verify = False
        self.dnac = DnaCenterClient(self.url, self.username, self.password, verify=self.verify)

        self.mock_response = create_autospec(Response)
        self.mock_response.message = MagicMock()
        self.mock_response.response = MagicMock()
        self.mock_response.response.request = MagicMock()
        self.mock_response.status_code = MagicMock()
        self.mock_response.message.return_value = "Unable to connect to DNA Center!"
        self.mock_response.response.return_value = {}
        self.mock_response.status_code.return_value = 401

    @patch("nautobot_ssot_dna_center.utils.dna_center.api.DNACenterAPI")
    def test_connect_success(self, mock_api):
        self.dnac.connect()
        mock_api.assert_called_once_with(  # nosec B106
            base_url="https://dnac.testexample.com:443", username="testuser", password="testpassword", verify=False
        )
        self.assertIsNotNone(self.dnac.conn)

    @patch("nautobot_ssot_dna_center.utils.dna_center.api.DNACenterAPI")
    def test_connect_error(self, mock_api):
        mock_api.side_effect = dnacentersdkException(self.mock_response)
        with self.assertLogs(level="ERROR") as log:
            self.dnac.connect()
            self.assertIn("Unable to connect to DNA Center", log.output[0])
        mock_api.assert_called_once_with(  # nosec B106
            base_url="https://dnac.testexample.com:443", password="testpassword", username="testuser", verify=False
        )
        self.assertIsNone(self.dnac.conn)

    def test_get_locations(self):
        """Test the get_locations method in DnaCenterClient."""
        self.dnac.conn = MagicMock()
        self.dnac.conn.sites.get_site.return_value = RECV_LOCATION_FIXTURE
        actual = self.dnac.get_locations()
        self.assertEqual(actual, LOCATION_FIXTURE)

    def test_get_locations_catches_api_error(self):
        """Test the get_locations method in DnaCenterClient catches dnacentersdkException."""
        self.dnac.conn = MagicMock()
        self.dnac.conn.sites.get_site.side_effect = dnacentersdkException(self.mock_response)
        with self.assertLogs(level="ERROR") as log:
            self.dnac.get_locations()
            self.assertIn("Unable to get site information from DNA Center.", log.output[0])

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
        self.dnac.conn = MagicMock()
        self.dnac.conn.devices.get_device_list.return_value = RECV_DEVICE_FIXTURE
        actual = self.dnac.get_devices()
        self.assertEqual(actual, DEVICE_FIXTURE)

    def test_get_devices_catches_api_error(self):
        """Test the get_devices method in DnaCenterClient catches dnacentersdkException."""
        self.dnac.conn = MagicMock()
        self.dnac.conn.devices.get_device_list.side_effect = dnacentersdkException(self.mock_response)
        with self.assertLogs(level="ERROR") as log:
            self.dnac.get_devices()
            self.assertIn("Unable to get device information from DNA Center.", log.output[0])

    def test_get_device_detail(self):
        """Test the get_device_detail method in DnaCenterClient."""
        self.dnac.conn = MagicMock()
        self.dnac.conn.devices.get_device_detail.return_value = RECV_DEVICE_DETAIL_FIXTURE
        actual = self.dnac.get_device_detail(dev_id="1234567890")
        self.assertEqual(actual, DEVICE_DETAIL_FIXTURE)

    def test_get_device_detail_catches_api_error(self):
        """Test the get_device_detail method in DnaCenterClient catches dnacentersdkException."""
        self.dnac.conn = MagicMock()
        self.dnac.conn.devices.get_device_detail.side_effect = dnacentersdkException(self.mock_response)
        with self.assertLogs(level="ERROR") as log:
            self.dnac.get_device_detail(dev_id="1234567890")
            self.assertIn("Unable to get device detail information from DNA Center.", log.output[0])

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
        self.dnac.conn = MagicMock()
        self.dnac.conn.devices.get_interface_info_by_id.return_value = RECV_PORT_FIXTURE
        actual = self.dnac.get_port_info(device_id="1234567890")
        self.assertEqual(actual, PORT_FIXTURE)

    mock_port_types = [
        ("SVI", {"portType": "Ethernet SVI"}, "virtual"),
        ("Service Module Interface", {"portType": "Service Module Interface"}, "virtual"),
        ("FastEthernet", {"portType": "Ethernet Port", "portName": "FastEth0"}, "100base-tx"),
        ("GigabitEthernet", {"portType": "Ethernet Port", "portName": "GigabitEthernet0/1"}, "1000base-t"),
        ("Number port", {"portType": "Ethernet Port", "portName": "0/1"}, "other"),
    ]

    @parameterized.expand(mock_port_types, skip_on_empty=True)
    def test_get_port_type(self, name, sent, received):  # pylint: disable=unused-argument
        """Test the get_port_type method in DnaCenterClient."""
        actual = self.dnac.get_port_type(port_info=sent)
        self.assertEqual(actual, received)

    mock_port_status = [
        ("Maintenance", {"adminStatus": "DOWN", "status": "down"}, "maintenance"),
        ("Failed", {"adminStatus": "UP", "status": "down"}, "failed"),
        ("Planned", {"adminStatus": "DOWN", "status": "up"}, "planned"),
        ("Active", {"adminStatus": "UP", "status": "up"}, "active"),
    ]

    @parameterized.expand(mock_port_status, skip_on_empty=True)
    def test_get_port_status(self, name, sent, received):  # pylint: disable=unused-argument
        """Test the get_port_status method in DnaCenterClient."""
        actual = self.dnac.get_port_status(port_info=sent)
        self.assertEqual(actual, received)
