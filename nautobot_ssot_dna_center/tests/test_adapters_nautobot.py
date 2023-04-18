"""Unit tests for the Nautobot DiffSync adapter."""

import uuid
from unittest.mock import MagicMock, patch
from diffsync.exceptions import ObjectNotFound
from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models import (
    Manufacturer,
    Region,
    Location,
    LocationType,
    Site,
    Device,
    DeviceType,
    DeviceRole,
    Platform,
    Interface,
)
from nautobot.extras.models import Status, Job, JobResult
from nautobot.ipam.models import IPAddress
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_dna_center.jobs import DnaCenterDataSource
from nautobot_ssot_dna_center.diffsync.adapters.nautobot import NautobotAdapter


class NautobotDiffSyncTestCase(TransactionTestCase):
    """Test the NautobotAdapter class."""

    databases = ("default", "job_logs")

    def __init__(self, *args, **kwargs):
        """Initialize shared variables."""
        super().__init__(*args, **kwargs)
        self.ny_region = None
        self.hq_site = None
        self.loc_type = None
        self.floor_loc = None

    def setUp(self):  # pylint: disable=too-many-locals
        """Per-test-case data setup."""
        super().setUp()
        self.status_active = Status.objects.get(name="Active")

        job = DnaCenterDataSource()
        job.job_result = JobResult.objects.create(
            name=job.class_path, obj_type=ContentType.objects.get_for_model(Job), user=None, job_id=uuid.uuid4()
        )
        self.nb_adapter = NautobotAdapter(job=job, sync=None)
        self.nb_adapter.job = MagicMock()
        self.nb_adapter.job.log_info = MagicMock()
        self.nb_adapter.job.log_warning = MagicMock()

    def build_nautobot_objects(self):  # pylint: disable=too-many-locals, too-many-statements
        """Build out Nautobot objects to test loading."""
        global_region = Region.objects.create(name="Global", slug="global")
        global_region.custom_field_data["system_of_record"] = "DNA Center"
        global_region.validated_save()
        self.ny_region = Region.objects.create(name="NY", parent=global_region, slug="ny")
        self.ny_region.custom_field_data["system_of_record"] = "DNA Center"
        self.ny_region.validated_save()

        self.hq_site = Site.objects.create(region=self.ny_region, name="HQ", slug="hq", status=self.status_active)
        self.hq_site.custom_field_data["system_of_record"] = "DNA Center"
        self.hq_site.validated_save()

        self.loc_type = LocationType.objects.create(name="Floor", slug="floor")
        self.loc_type.content_types.add(ContentType.objects.get_for_model(Device))
        self.floor_loc = Location.objects.create(
            name="HQ Floor 1",
            slug="hq_floor_1",
            site=self.hq_site,
            location_type=self.loc_type,
            status=self.status_active,
        )
        self.floor_loc.custom_field_data["system_of_record"] = "DNA Center"
        self.floor_loc.validated_save()

        cisco_manu = Manufacturer.objects.create(name="Cisco", slug="cisco")
        csr_devicetype = DeviceType.objects.create(model="Cisco Catalyst 9300 Switch", manufacturer=cisco_manu)
        leaf_role = DeviceRole.objects.create(name="LEAF", slug="leaf")
        spine_role = DeviceRole.objects.create(name="SPINE", slug="spine")
        ios_platform = Platform.objects.create(name="IOS", slug="cisco_ios", napalm_driver="ios")
        leaf1_dev = Device.objects.create(
            name="leaf1.abc.inc",
            site=self.hq_site,
            location=self.floor_loc,
            status=self.status_active,
            device_type=csr_devicetype,
            device_role=leaf_role,
            platform=ios_platform,
            serial="FCW2214L0VK",
        )
        leaf1_dev.custom_field_data["system_of_record"] = "DNA Center"
        leaf2_dev = Device.objects.create(
            name="leaf2.abc.inc",
            site=self.hq_site,
            location=self.floor_loc,
            status=self.status_active,
            device_type=csr_devicetype,
            device_role=leaf_role,
            platform=ios_platform,
            serial="FCW2214L0UZ",
        )
        leaf2_dev.custom_field_data["system_of_record"] = "DNA Center"
        spine1_dev = Device.objects.create(
            name="spine1.abc.in",
            site=self.hq_site,
            location=self.floor_loc,
            status=self.status_active,
            device_type=csr_devicetype,
            device_role=spine_role,
            platform=ios_platform,
            serial="FCW2212D05S",
        )
        spine1_dev.custom_field_data["system_of_record"] = "DNA Center"
        spine1_dev.validated_save()

        meraki_ap = Device.objects.create(
            name="",
            site=self.hq_site,
            location=self.floor_loc,
            status=self.status_active,
            device_type=DeviceType.objects.create(model="MR42", manufacturer=cisco_manu),
            device_role=DeviceRole.objects.create(name="UNKNOWN", slug="unknown"),
            platform=Platform.objects.create(name="meraki", slug="meraki", napalm_driver="meraki"),
            serial="R3JE-OYG4-RCDE",
        )
        meraki_ap.custom_field_data["system_of_record"] = "DNA Center"
        meraki_ap.validated_save()

        leaf1_mgmt = Interface.objects.create(
            device=leaf1_dev,
            name="Management",
            status=self.status_active,
            mtu=1500,
            type="virtual",
            mac_address="aa:bb:cc:dd:ee:f1",
        )
        leaf1_mgmt.custom_field_data["system_of_record"] = "DNA Center"
        leaf1_mgmt.validated_save()
        leaf2_mgmt = Interface.objects.create(
            device=leaf2_dev,
            name="Management",
            status=self.status_active,
            mtu=1500,
            type="virtual",
            mac_address="aa:bb:cc:dd:ee:f2",
        )
        leaf2_mgmt.custom_field_data["system_of_record"] = "DNA Center"
        leaf2_mgmt.validated_save()
        spine1_mgmt = Interface.objects.create(
            device=spine1_dev,
            name="Management",
            status=self.status_active,
            mtu=1500,
            type="virtual",
            mac_address="aa:bb:cc:dd:ee:f3",
        )
        spine1_mgmt.custom_field_data["system_of_record"] = "DNA Center"
        spine1_mgmt.validated_save()

        ap_mgmt = Interface.objects.create(
            device=meraki_ap,
            name="Management",
            status=self.status_active,
            mtu=1500,
            type="virtual",
            mac_address="aa:bb:cc:dd:ee:f4",
        )
        ap_mgmt.custom_field_data["system_of_record"] = "DNA Center"
        ap_mgmt.validated_save()

        leaf1_ip = IPAddress.objects.create(
            address="10.10.10.1/24",
            status=self.status_active,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
            assigned_object_id=leaf1_mgmt.id,
        )
        leaf1_ip.custom_field_data["system_of_record"] = "DNA Center"
        leaf1_ip.validated_save()
        leaf1_mgmt.device.primary_ip4 = leaf1_ip
        leaf1_mgmt.device.validated_save()

        leaf2_ip = IPAddress.objects.create(
            address="10.10.11.1/24",
            status=self.status_active,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
            assigned_object_id=leaf2_mgmt.id,
        )
        leaf2_ip.custom_field_data["system_of_record"] = "DNA Center"
        leaf2_ip.validated_save()
        leaf2_mgmt.device.primary_ip4 = leaf2_ip
        leaf2_mgmt.device.validated_save()

        spine1_ip = IPAddress.objects.create(
            address="10.10.12.1/24",
            status=self.status_active,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
            assigned_object_id=spine1_mgmt.id,
        )
        spine1_ip.custom_field_data["system_of_record"] = "DNA Center"
        spine1_ip.validated_save()
        spine1_mgmt.device.primary_ip4 = spine1_ip
        spine1_mgmt.device.validated_save()

        ap_ip = IPAddress.objects.create(
            address="10.10.13.1/24",
            status=self.status_active,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
            assigned_object_id=ap_mgmt.id,
        )
        ap_ip.custom_field_data["system_of_record"] = "DNA Center"
        ap_ip.validated_save()
        ap_mgmt.device.primary_ip4 = ap_ip
        ap_mgmt.device.validated_save()

    def test_data_loading(self):
        """Test the load() function."""
        self.build_nautobot_objects()
        self.nb_adapter.load()
        self.assertEqual(
            ["Global__None", "NY__Global"],
            sorted(loc.get_unique_id() for loc in self.nb_adapter.get_all("area")),
        )
        self.assertEqual(
            ["HQ__NY"],
            sorted(site.get_unique_id() for site in self.nb_adapter.get_all("building")),
        )
        self.assertEqual(
            ["HQ Floor 1__HQ"],
            sorted(loc.get_unique_id() for loc in self.nb_adapter.get_all("floor")),
        )
        self.assertEqual(
            [
                "__HQ__R3JE-OYG4-RCDE__10.10.13.1",
                "leaf1.abc.inc__HQ__FCW2214L0VK__10.10.10.1",
                "leaf2.abc.inc__HQ__FCW2214L0UZ__10.10.11.1",
                "spine1.abc.in__HQ__FCW2212D05S__10.10.12.1",
            ],
            sorted(dev.get_unique_id() for dev in self.nb_adapter.get_all("device")),
        )
        self.assertEqual(
            [
                "Management____AA:BB:CC:DD:EE:F4",
                "Management__leaf1.abc.inc__AA:BB:CC:DD:EE:F1",
                "Management__leaf2.abc.inc__AA:BB:CC:DD:EE:F2",
                "Management__spine1.abc.in__AA:BB:CC:DD:EE:F3",
            ],
            sorted(port.get_unique_id() for port in self.nb_adapter.get_all("port")),
        )
        self.assertEqual(
            [
                "10.10.10.1/24__leaf1.abc.inc__Management",
                "10.10.11.1/24__leaf2.abc.inc__Management",
                "10.10.12.1/24__spine1.abc.in__Management",
                "10.10.13.1/24____Management",
            ],
            sorted(ipaddr.get_unique_id() for ipaddr in self.nb_adapter.get_all("ipaddress")),
        )

    def test_load_regions_failure(self):
        """Test the load_regions method failing with loading duplicate Regions."""
        self.build_nautobot_objects()
        self.nb_adapter.load()
        self.nb_adapter.load_regions()
        self.nb_adapter.job.log_warning.assert_called_with(message="Region NY already loaded so skipping duplicate.")

    @patch("nautobot_ssot_dna_center.diffsync.adapters.nautobot.OrmSite")
    def test_load_sites_failure(self, mock_sites):
        """Test the load_sites method failing with missing Area."""
        mock_site = MagicMock()
        mock_site.name = "Test"
        mock_site.region = MagicMock()
        mock_site.region.name = "Missing"
        mock_site.region.parent = None
        mock_site.physical_address = "123 Main St"
        mock_site.latitude = 42.654321
        mock_site.longitude = -71.345678
        mock_site.tenant = None
        mock_site.id = uuid.uuid4()
        mock_sites.objects.filter.return_value = [mock_site]
        self.nb_adapter.get = MagicMock()
        self.nb_adapter.get.side_effect = [ObjectNotFound(), ObjectNotFound()]
        self.nb_adapter.load_sites()
        self.nb_adapter.job.log_warning.assert_called_once_with(message="Unable to load area Missing for Test. ")

    def test_load_floors_missing_location_type(self):
        """Test the load_floors method failing with missing Location Type."""
        self.nb_adapter.load_floors()
        self.nb_adapter.job.log_warning.assert_called_with(
            message="Unable to find LocationType: Floor so can't find floor Locations to load. LocationType matching query does not exist."
        )

    @patch("nautobot_ssot_dna_center.diffsync.adapters.nautobot.OrmLocationType")
    @patch("nautobot_ssot_dna_center.diffsync.adapters.nautobot.OrmLocation")
    def test_load_floors_missing_building(self, mock_floors, mock_loc_type):
        """Test the load_floors method failing with missing Building."""
        mock_floor = MagicMock()
        mock_floor.name = "HQ - Floor 1"
        mock_floor.site = MagicMock()
        mock_floor.site.name = "Missing"
        mock_floor.tenant = None
        mock_floor.id = uuid.uuid4()
        mock_loc_type.objects.get.return_value = mock_loc_type
        mock_floors.objects.filter.return_value = [mock_floor]
        self.nb_adapter.get = MagicMock()
        self.nb_adapter.get.side_effect = [ObjectNotFound()]
        self.nb_adapter.load_floors()
        self.nb_adapter.job.log_warning.assert_called_with(
            message="Unable to load building Missing for floor HQ - Floor 1. "
        )

    def test_sync_complete(self):
        """Test the sync_complete() method in the NautobotAdapter."""
        self.nb_adapter.objects_to_delete = {
            "floors": [MagicMock(), MagicMock()],
            "sites": [MagicMock()],
            "regions": [],
        }
        self.nb_adapter.job = MagicMock()
        self.nb_adapter.job.log_info = MagicMock()

        deleted_objs = []
        for group in ["floors", "sites"]:
            deleted_objs.extend(self.nb_adapter.objects_to_delete[group])

        self.nb_adapter.sync_complete(diff=MagicMock(), source=MagicMock())

        for obj in deleted_objs:
            self.assertTrue(obj.delete.called)
        self.assertEqual(len(self.nb_adapter.objects_to_delete["floors"]), 0)
        self.assertEqual(len(self.nb_adapter.objects_to_delete["sites"]), 0)
        self.assertEqual(len(self.nb_adapter.objects_to_delete["regions"]), 0)
        self.assertTrue(self.nb_adapter.job.log_info.called)
        self.assertTrue(self.nb_adapter.job.log_info.call_count, 3)
        self.assertTrue(self.nb_adapter.job.log_info.call_args_list[0].startswith("Deleting"))
        self.assertTrue(self.nb_adapter.job.log_info.call_args_list[1].startswith("Deleting"))
        self.assertTrue(self.nb_adapter.job.log_info.call_args_list[2].startswith("Deleting"))
