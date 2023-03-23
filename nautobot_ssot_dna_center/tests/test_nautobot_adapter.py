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
        self.status_active = Status.objects.create(name="Active", slug="active")
        self.status_active.validated_save()

        job = DnaCenterDataSource()
        job.job_result = JobResult.objects.create(
            name=job.class_path, obj_type=ContentType.objects.get_for_model(Job), user=None, job_id=uuid.uuid4()
        )
        self.nb_adapter = NautobotAdapter(job=job, sync=None)
        self.nb_adapter.job = MagicMock()
        self.nb_adapter.job.log_info = MagicMock()
        self.nb_adapter.job.log_warning = MagicMock()

    def build_nautobot_objects(self):
        """Build out Nautobot objects to test loading."""
        global_region = Region.objects.create(name="Global", slug="global")
        self.ny_region = Region.objects.create(name="NY", parent=global_region, slug="ny")

        self.hq_site = Site.objects.create(region=self.ny_region, name="HQ", slug="hq", status=self.status_active)

        self.loc_type = LocationType.objects.create(name="Floor", slug="floor")
        self.loc_type.content_types.add(ContentType.objects.get_for_model(Device))
        self.floor_loc = Location.objects.create(
            name="HQ Floor 1",
            slug="hq_floor_1",
            site=self.hq_site,
            location_type=self.loc_type,
            status=self.status_active,
        )

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
        )
        leaf2_dev = Device.objects.create(
            name="leaf2.abc.inc",
            site=self.hq_site,
            location=self.floor_loc,
            status=self.status_active,
            device_type=csr_devicetype,
            device_role=leaf_role,
            platform=ios_platform,
        )
        spine1_dev = Device.objects.create(
            name="spine1.abc.in",
            site=self.hq_site,
            location=self.floor_loc,
            status=self.status_active,
            device_type=csr_devicetype,
            device_role=spine_role,
            platform=ios_platform,
        )

        leaf1_mgmt = Interface.objects.create(device=leaf1_dev, name="Management", status=self.status_active, mtu=1500)
        leaf2_mgmt = Interface.objects.create(device=leaf2_dev, name="Management", status=self.status_active, mtu=1500)
        spine1_mgmt = Interface.objects.create(
            device=spine1_dev, name="Management", status=self.status_active, mtu=1500
        )

        leaf1_ip = IPAddress.objects.create(
            address="10.10.10.1/24",
            status=self.status_active,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
            assigned_object_id=leaf1_mgmt.id,
        )
        leaf1_mgmt.device.primary_ip4 = leaf1_ip
        leaf1_mgmt.device.save()

        leaf2_ip = IPAddress.objects.create(
            address="10.10.11.1/24",
            status=self.status_active,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
            assigned_object_id=leaf2_mgmt.id,
        )
        leaf2_mgmt.device.primary_ip4 = leaf2_ip
        leaf2_mgmt.device.save()

        IPAddress.objects.create(
            address="10.10.12.1/24",
            status=self.status_active,
            assigned_object_type=ContentType.objects.get_for_model(Interface),
            assigned_object_id=spine1_mgmt.id,
        )

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
            ["leaf1.abc.inc", "leaf2.abc.inc", "spine1.abc.in"],
            sorted(dev.get_unique_id() for dev in self.nb_adapter.get_all("device")),
        )
        self.assertEqual(
            ["Management__leaf1.abc.inc", "Management__leaf2.abc.inc", "Management__spine1.abc.in"],
            sorted(port.get_unique_id() for port in self.nb_adapter.get_all("port")),
        )
        self.assertEqual(
            [
                "10.10.10.1/24__leaf1.abc.inc__Management",
                "10.10.11.1/24__leaf2.abc.inc__Management",
                "10.10.12.1/24__spine1.abc.in__Management",
            ],
            sorted(ipaddr.get_unique_id() for ipaddr in self.nb_adapter.get_all("ipaddress")),
        )

    def test_load_regions_failure(self):
        """Test the load_regions method failing with loading duplicate Regions."""
        self.build_nautobot_objects()
        self.nb_adapter.load()
        self.nb_adapter.load_regions()
        self.nb_adapter.job.log_warning.assert_called_with(message="Region NY already loaded so skipping duplicate.")

    def test_load_floors_missing_location_type(self):
        """Test the load_floors method failing with missing Location Type."""
        self.nb_adapter.job.log_warning = MagicMock()
        Device.objects.all().delete()
        Location.objects.all().delete()
        LocationType.objects.all().delete()
        self.nb_adapter.load_floors()
        self.nb_adapter.job.log_warning.assert_called_with(
            message="Unable to find LocationType: Floor so can't find floor Locations to load. LocationType matching query does not exist."
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
