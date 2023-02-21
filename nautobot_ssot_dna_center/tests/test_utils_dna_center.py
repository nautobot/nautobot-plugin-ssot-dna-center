"""Tests of DNA Center utility methods."""

from unittest.mock import MagicMock
from nautobot.utilities.testing import TestCase
from nautobot_ssot_dna_center.tests.fixtures import (
    DEVICE_FIXTURE,
    RECV_DEVICE_FIXTURE,
    LOCATION_FIXTURE,
    RECV_LOCATION_FIXTURE,
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

    def test_get_devices(self):
        """Test the get_devices method in DnaCenterClient."""
        self.dnac.conn.devices.get_device_list.return_value = RECV_DEVICE_FIXTURE
        actual = self.dnac.get_devices()
        self.assertEqual(actual, DEVICE_FIXTURE)
