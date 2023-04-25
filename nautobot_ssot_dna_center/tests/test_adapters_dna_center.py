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
    EXPECTED_DNAC_LOCATION_MAP_WO_GLOBAL,
    DEVICE_FIXTURE,
    DEVICE_DETAIL_FIXTURE,
    PORT_FIXTURE,
    EXPECTED_AREAS,
    EXPECTED_AREAS_WO_GLOBAL,
    EXPECTED_BUILDINGS,
    EXPECTED_FLOORS,
)
from nautobot_ssot_dna_center.jobs import DnaCenterDataSource


@override_settings(PLUGINS_CONFIG={"nautobot_ssot_dna_center": {"import_global": True}})
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
        self.job.kwargs["debug"] = True
        self.job.job_result = JobResult.objects.create(
            name=self.job.class_path, obj_type=ContentType.objects.get_for_model(Job), user=None, job_id=uuid.uuid4()
        )
        self.dna_center = DnaCenterAdapter(job=self.job, sync=None, client=self.dna_center_client, tenant=None)
        self.dna_center.job.log_warning = MagicMock()
        self.dna_center.job.log_failure = MagicMock()
        self.dna_center.job.log_info = MagicMock()
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP

        self.mock_device = DnaCenterDevice(
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

    def test_build_dnac_location_map(self):
        """Test Nautobot adapter build_dnac_location_map method."""
        self.dna_center.dnac_location_map = {}
        actual = self.dna_center.build_dnac_location_map(locations=LOCATION_FIXTURE)
        expected = EXPECTED_DNAC_LOCATION_MAP
        self.assertEqual(actual, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_dna_center": {"import_global": False}})
    def test_build_dnac_location_map_wo_global(self):
        """Test Nautobot adapter build_dnac_location_map method without global."""
        self.dna_center.dnac_location_map = {}
        actual = self.dna_center.build_dnac_location_map(locations=LOCATION_FIXTURE)
        expected = EXPECTED_DNAC_LOCATION_MAP_WO_GLOBAL
        self.assertEqual(actual, expected)

    def test_parse_and_sort_locations(self):
        """Test Nautobot adapter parse_and_sort_locations method."""
        actual = self.dna_center.parse_and_sort_locations(locations=LOCATION_FIXTURE)
        expected = EXPECTED_AREAS, EXPECTED_BUILDINGS, EXPECTED_FLOORS
        self.assertEqual(actual, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_dna_center": {"import_global": False}})
    def test_parse_and_sort_locations_wo_global(self):
        """Test Nautobot adapter parse_and_sort_locations method without Global region."""
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP_WO_GLOBAL
        actual_areas, actual_buildings, actual_floors = self.dna_center.parse_and_sort_locations(
            locations=LOCATION_FIXTURE
        )
        self.assertEqual(actual_areas, EXPECTED_AREAS_WO_GLOBAL)
        self.assertEqual(actual_buildings, EXPECTED_BUILDINGS)
        self.assertEqual(actual_floors, EXPECTED_FLOORS)

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

    def test_load_areas_w_global(self):
        """Test Nautobot SSoT for Cisco DNA Center load_areas() function with Global area."""
        self.dna_center.load_areas(areas=EXPECTED_AREAS)
        area_expected = [
            "Global__None",
            "NY__Global",
        ]
        area_actual = [area.get_unique_id() for area in self.dna_center.get_all("area")]
        self.assertEqual(area_actual, area_expected)
        self.dna_center.job.log_info.assert_called_with(
            message="Loading area NY. {'additionalInfo': [{'attributes': {'addressInheritedFrom': '3f07768d-6b5c-4b4d-8577-29f765bd49c9', 'type': 'area'}, 'nameSpace': 'Location'}], 'id': '3f07768d-6b5c-4b4d-8577-29f765bd49c9', 'instanceTenantId': '623f029857259506a56ad9bd', 'name': 'NY', 'parentId': '9e5f9fc2-032e-45e8-994c-4a00629648e8', 'siteHierarchy': '9e5f9fc2-032e-45e8-994c-4a00629648e8/3f07768d-6b5c-4b4d-8577-29f765bd49c9', 'siteNameHierarchy': 'Global/NY'}"
        )

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_dna_center": {"import_global": False}})
    def test_load_areas_wo_global(self):
        """Test Nautobot SSoT for Cisco DNA Center load_areas() function without Global area."""
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP_WO_GLOBAL
        self.dna_center.load_areas(areas=EXPECTED_AREAS)
        area_expected = [
            "NY__None",
        ]
        area_actual = [area.get_unique_id() for area in self.dna_center.get_all("area")]
        self.assertEqual(area_actual, area_expected)

    def test_load_areas_with_validation_error(self):
        """Test Nautobot SSoT for Cisco DNA Center load_areas() function with a ValidationError."""
        self.dna_center.add = MagicMock()
        self.dna_center.add.side_effect = ValidationError(message="Device load failed!")
        self.dna_center.load_areas(areas=EXPECTED_AREAS_WO_GLOBAL)
        self.dna_center.job.log_warning.assert_called_with(message="Unable to load area NY. ['Device load failed!']")

    def test_load_buildings_w_global(self):
        """Test Nautobot SSoT for Cisco DNA Center load_buildings() function with Global area."""
        self.dna_center.load_buildings(buildings=EXPECTED_BUILDINGS)
        building_expected = ["Building1", "DC1"]
        building_actual = [building.get_unique_id() for building in self.dna_center.get_all("building")]
        self.assertEqual(building_actual, building_expected)

    def test_load_buildings_wo_global(self):
        """Test Nautobot SSoT for Cisco DNA Center load_buildings() function without Global area."""
        self.dna_center.dnac_location_map = EXPECTED_DNAC_LOCATION_MAP_WO_GLOBAL
        self.dna_center.load_buildings(buildings=EXPECTED_BUILDINGS)
        building_expected = ["Building1", "DC1"]
        building_actual = [building.get_unique_id() for building in self.dna_center.get_all("building")]
        self.assertEqual(building_actual, building_expected)

    def test_load_buildings_duplicate(self):
        """Test Nautobot SSoT for Cisco DNA Center load_buildings() function with duplicate building."""
        self.dna_center.load_buildings(buildings=EXPECTED_BUILDINGS)
        self.dna_center.load_buildings(buildings=EXPECTED_BUILDINGS)
        self.dna_center.job.log_warning.assert_called_with(message="Building DC1 already loaded so skipping.")

    def test_load_floors(self):
        """Test Nautobot SSoT for Cisco DNA Center load_floors() function."""
        self.dna_center.load_floors(floors=EXPECTED_FLOORS)
        floor_expected = ["Building1 - Floor1__Building1", "DC1 - Main Floor__DC1"]
        floor_actual = [floor.get_unique_id() for floor in self.dna_center.get_all("floor")]
        self.assertEqual(floor_actual, floor_expected)

    def test_load_devices(self):
        """Test Nautobot SSoT for Cisco DNA Center load_devices() function."""
        self.dna_center.load_ports = MagicMock()
        self.dna_center.load_devices()
        self.assertEqual(
            {
                f"{dev['hostname']}__Building1__{dev['serialNumber']}__{dev['managementIpAddress']}"
                for dev in DEVICE_FIXTURE
            },
            {dev.get_unique_id() for dev in self.dna_center.get_all("device")},
        )
        self.dna_center.load_ports.assert_called()

    def test_load_ports(self):
        """Test Nautobot SSoT for Cisco DNA Center load_ports() function."""
        expected_ports = []
        for port in PORT_FIXTURE:
            if port.get("portName"):
                if port.get("macAddress"):
                    mac_addr = port["macAddress"].upper()
                else:
                    mac_addr = "None"
                expected_ports.append(f"{port['portName']}__leaf3.abc.inc__{mac_addr}")
        self.dna_center.load_ports(device_id="1234567890", dev=self.mock_device)
        actual_ports = [port.get_unique_id() for port in self.dna_center.get_all("port")]
        self.assertEqual(expected_ports, actual_ports)

    def test_load_ports_validation_error(self):
        """Test Nautobot SSoT for Cisco DNA Center load_ports() function throwing ValidationError."""
        self.dna_center.add = MagicMock(side_effect=ValidationError(message="leaf3.abc.inc not found"))
        self.dna_center.load_ports(device_id="1234567890", dev=self.mock_device)
        self.dna_center.job.log_warning.assert_called_with(
            message="Unable to load port Vlan848 for leaf3.abc.inc. ['leaf3.abc.inc not found']"
        )
