"""Test DNA Center adapter."""

import uuid
from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from nautobot.extras.models import Job, JobResult
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_dna_center.diffsync.adapters.dna_center import DnaCenterAdapter
from nautobot_ssot_dna_center.diffsync.models.dna_center import DnaCenterDevice
from nautobot_ssot_dna_center.tests.fixtures import (
    LOCATION_FIXTURE,
    EXPECTED_DNAC_LOCATION_MAP,
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
        self.dna_center.job.log_failure = MagicMock()
        self.dna_center.load()

    def test_build_dnac_location_map(self):
        """Test Nautobot adapter build_dnac_location_map method."""
        actual = self.dna_center.build_dnac_location_map(locations=LOCATION_FIXTURE)
        expected = EXPECTED_DNAC_LOCATION_MAP
        self.assertEqual(actual, expected)

    def test_parse_and_sort_locations(self):
        """Test Nautobot adapter parse_and_sort_locations method."""
        self.dna_center.dnac_location_map = self.dna_center.build_dnac_location_map(locations=LOCATION_FIXTURE)
        actual = self.dna_center.parse_and_sort_locations(locations=LOCATION_FIXTURE)
        expected = EXPECTED_AREAS, EXPECTED_BUILDINGS, EXPECTED_FLOORS
        self.assertEqual(actual, expected)

    def test_load_locations_success(self):
        """Test Nautobot SSoT for Cisco DNA Center load_locations() function successfully."""
        self.dna_center.load_areas = MagicMock()
        self.dna_center.load_buildings = MagicMock()
        self.dna_center.load_floors = MagicMock()
        self.dna_center_client.get_location.return_value = [{"name": "NY"}]
        self.dna_center.load_locations()
        self.dna_center_client.get_locations.assert_called()
        self.dna_center.load_areas.assert_called_once()
        self.dna_center.load_buildings.assert_called_once()
        self.dna_center.load_floors.assert_called_once()

    def test_load_locations_failure(self):
        """Test Nautobot SSoT for Cisco DNA Center load_locations() function fails."""
        self.dna_center_client.get_locations.return_value = []
        self.dna_center.load_locations()
        self.dna_center.job.log_failure.assert_called_once_with(
            "No location data was returned from DNAC. Unable to proceed."
        )

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_dna_center": {"import_global": True}})
    def test_load_areas_w_global(self):
        """Test Nautobot SSoT for Cisco DNA Center load_areas() function with Global area."""
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP
        self.dna_center.load_areas(areas=EXPECTED_AREAS)
        area_expected = [
            "Global__None",
            "NY__Global",
        ]
        area_actual = [area.get_unique_id() for area in self.dna_center.get_all("area")]
        self.assertEqual(area_actual, area_expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_dna_center": {"import_global": False}})
    def test_load_areas_wo_global(self):
        """Test Nautobot SSoT for Cisco DNA Center load_areas() function without Global area."""
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP
        self.dna_center.dnac_location_map.pop("9e5f9fc2-032e-45e8-994c-4a00629648e8")
        self.dna_center.load_areas(areas=EXPECTED_AREAS)
        area_expected = [
            "NY__None",
        ]
        area_actual = [area.get_unique_id() for area in self.dna_center.get_all("area")]
        self.assertEqual(area_actual, area_expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_dna_center": {"import_global": True}})
    def test_load_buildings_w_global(self):
        """Test Nautobot SSoT for Cisco DNA Center load_buildings() function with Global area."""
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP
        self.dna_center.load_buildings(buildings=EXPECTED_BUILDINGS)
        building_expected = ["Building1__NY"]
        building_actual = [building.get_unique_id() for building in self.dna_center.get_all("building")]
        self.assertEqual(building_actual, building_expected)

    def test_load_floors(self):
        """Test Nautobot SSoT for Cisco DNA Center load_floors() function."""
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP
        self.dna_center.load_floors(floors=EXPECTED_FLOORS)
        floor_expected = ["Building1 - Floor1__Building1"]
        floor_actual = [floor.get_unique_id() for floor in self.dna_center.get_all("floor")]
        self.assertEqual(floor_actual, floor_expected)

    def test_load_devices(self):
        """Test Nautobot SSoT for Cisco DNA Center load_devices() function."""
        self.assertEqual(
            {
                f"{dev['hostname']}__Building1__{dev['serialNumber']}__{dev['managementIpAddress']}"
                for dev in DEVICE_FIXTURE
            },
            {dev.get_unique_id() for dev in self.dna_center.get_all("device")},
        )

    def test_load_devices_missing_building(self):
        """Test Nautobot SSoT for Cisco DNA Center load_devices() function with device missing building."""
        self.dna_center_client.get_devices.return_value = [
            {"hostname": "test-device", "softwareType": None, "type": "Meraki", "id": "1234"}
        ]
        self.dna_center_client.get_device_detail.return_value = {}
        self.dna_center.load_devices()
        self.dna_center.job.log_warning.assert_called_with(message="Unable to find Site for test-device so skipping.")

    def test_load_ports(self):
        """Test Nautobot SSoT for Cisco DNA Center load_ports() function."""
        expected_ports = []
        for dev in DEVICE_FIXTURE:
            for port in PORT_FIXTURE:
                if port.get("portName"):
                    if port.get("macAddress"):
                        mac_addr = port["macAddress"].upper()
                    else:
                        mac_addr = "None"
                    expected_ports.append(f"{port['portName']}__{dev['hostname']}__{mac_addr}")
        actual_ports = [port.get_unique_id() for port in self.dna_center.get_all("port")]
        self.assertEqual(expected_ports, actual_ports)

    def test_load_ports_validation_error(self):
        """Test Nautobot SSoT for Cisco DNA Center load_ports() function throwing ValidationError."""
        self.dna_center.add = MagicMock(side_effect=ValidationError(message="leaf3.abc.inc not found"))
        mock_device = DnaCenterDevice(
            name="leaf3.abc.inc",
            status="Active",
            role="CORE",
            vendor="Cisco",
            model="CSR1000v",
            area="NY",
            site="Building1",
            floor="Floor 1",
            serial="FQ234567",
            version="16.2.3",
            platform="cisco_ios",
            tenant="IT",
            management_addr="10.10.0.1",
            uuid=None,
        )
        self.dna_center.load_ports(device_id="1234567890", dev=mock_device)
        self.dna_center.job.log_warning.assert_called_with(
            message="Unable to load port Vlan848 for leaf3.abc.inc. ['leaf3.abc.inc not found']"
        )
