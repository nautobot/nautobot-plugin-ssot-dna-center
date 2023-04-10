"""Test DNA Center adapter."""

import uuid
from unittest.mock import MagicMock

from django.contrib.contenttypes.models import ContentType
from diffsync.exceptions import ObjectNotFound
from nautobot.extras.models import Job, JobResult
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_dna_center.diffsync.adapters.dna_center import DnaCenterAdapter
from nautobot_ssot_dna_center.tests.fixtures import (
    LOCATION_FIXTURE,
    DEVICE_FIXTURE,
    DEVICE_DETAIL_FIXTURE,
    PORT_FIXTURE,
    EXPECTED_AREAS,
    EXPECTED_BUILDINGS,
    EXPECTED_FLOORS,
)
from nautobot_ssot_dna_center.jobs import DnaCenterDataSource


class TestDnaCenterAdapterTestCase(TransactionTestCase):
    """Test NautobotSsotDnaCenterAdapter class."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Initialize test case."""
        self.dna_center_client = MagicMock()
        self.dna_center_client.get_locations.return_value = LOCATION_FIXTURE
        self.dna_center_client.get_devices.return_value = DEVICE_FIXTURE
        self.dna_center_client.find_address_and_type.side_effect = [
            ("", "floor"),
            ("", "building"),
            ("", "area"),
        ]
        self.dna_center_client.find_latitude_and_longitude.return_value = ("", "")
        self.dna_center_client.get_device_detail.return_value = DEVICE_DETAIL_FIXTURE
        self.dna_center_client.parse_site_hierarchy.return_value = {
            "areas": ["Global", "NY"],
            "building": "Building1",
            "floor": "Floor1",
        }
        self.dna_center_client.get_port_info.return_value = PORT_FIXTURE
        self.dna_center_client.get_port_type.return_value = "virtual"
        self.dna_center_client.get_port_status.return_value = "active"

        self.job = DnaCenterDataSource()
        self.job.job_result = JobResult.objects.create(
            name=self.job.class_path, obj_type=ContentType.objects.get_for_model(Job), user=None, job_id=uuid.uuid4()
        )
        self.dna_center = DnaCenterAdapter(job=self.job, sync=None, client=self.dna_center_client, tenant=None)
        self.dna_center.job.log_warning = MagicMock()
        self.dna_center.load()

    def test_build_dnac_location_map(self):
        """Test Nautobot adapter build_dnac_location_map method."""
        actual = self.dna_center.build_dnac_location_map(locations=LOCATION_FIXTURE)
        expected = {
            "9e5f9fc2-032e-45e8-994c-4a00629648e8": {
                "name": "Global",
                "loc_type": "area",
                "parent": None,
            },
            "49aa97a7-5d45-4303-89dd-f76dfbfc624a": {
                "name": "Floor1",
                "loc_type": "area",
                "parent": None,
            },
            "5c59e37a-f12d-4e84-a085-ac5c02f240d4": {
                "name": "Building1",
                "loc_type": "area",
                "parent": None,
            },
            "3f07768d-6b5c-4b4d-8577-29f765bd49c9": {
                "name": "NY",
                "loc_type": "area",
                "parent": None,
            },
        }
        self.assertEqual(actual, expected)

    def test_parse_and_sort_locations(self):
        """Test Nautobot adapter parse_and_sort_locations method."""
        self.dna_center.dnac_location_map = self.dna_center.build_dnac_location_map(locations=LOCATION_FIXTURE)
        actual = self.dna_center.parse_and_sort_locations(locations=LOCATION_FIXTURE)
        expected = EXPECTED_AREAS, EXPECTED_BUILDINGS, EXPECTED_FLOORS
        self.assertEqual(actual, expected)

    def test_load_locations(self):
        """Test Nautobot SSoT for Cisco DNA Center load_locations() function."""
        area_actual, building_actual, floor_actual = [], [], []
        area_expected = [area.get_unique_id() for area in self.dna_center.get_all("area")]
        building_expected = [building.get_unique_id() for building in self.dna_center.get_all("building")]
        floor_expected = [floor.get_unique_id() for floor in self.dna_center.get_all("floor")]

        for location in LOCATION_FIXTURE:
            name = location["name"]
            parent = (
                self.dna_center.dnac_location_map[location["parentId"]]["name"] if location.get("parentId") else None
            )
            loc_name = f"{name}__{parent}"
            if location.get("additionalInfo"):
                for info in location["additionalInfo"]:
                    if info["attributes"].get("type") == "area":
                        area_actual.append(loc_name)
                    if info["attributes"].get("type") == "building":
                        building_actual.append(loc_name)
                    if info["attributes"].get("type") == "floor":
                        loc_name = f"{parent} - {loc_name}"
                        floor_actual.append(loc_name)
            else:
                area_actual.append(loc_name)
        self.assertEqual(area_actual, area_expected)
        self.assertEqual(building_actual, building_expected)
        self.assertEqual(floor_actual, floor_expected)

    def test_load_devices(self):
        """Test Nautobot SSoT for Cisco DNA Center load_devices() function."""
        self.assertEqual(
            {dev["hostname"] for dev in DEVICE_FIXTURE},
            {dev.get_unique_id() for dev in self.dna_center.get_all("device")},
        )

    def test_load_devices_missing_hostname(self):
        """Test Nautobot SSoT for Cisco DNA Center load_devices() function with device missing hostname."""
        self.dna_center_client.get_devices.return_value = [{"hostname": "", "id": "1234"}]
        self.dna_center.load_devices()
        self.dna_center.job.log_warning.assert_called_once_with(
            message="Device found in DNAC without hostname so will be skipped. Ref device ID: 1234"
        )

    def test_load_ports(self):
        """Test Nautobot SSoT for Cisco DNA Center load_ports() function."""
        expected_ports = []
        for dev in DEVICE_FIXTURE:
            for port in PORT_FIXTURE:
                if port.get("portName"):
                    expected_ports.append(f"{port['portName']}__{dev['hostname']}")
        actual_ports = [port.get_unique_id() for port in self.dna_center.get_all("port")]
        self.assertEqual(expected_ports, actual_ports)

    def test_load_ports_missing_device(self):
        """Test Nautobot SSoT for Cisco DNA Center load_ports() function with missing device."""
        self.dna_center.get = MagicMock(side_effect=ObjectNotFound("Device not found"))
        self.dna_center.load_ports(device_id="1234567890", device_name="missing_device")
        self.dna_center.job.log_warning.assert_called_once_with(
            message="Unable to find Device missing_device to assign Ports to so skipping. Device not found"
        )
