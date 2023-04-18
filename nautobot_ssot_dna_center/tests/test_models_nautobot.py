"""Test the DiffSync models for Nautobot."""
from unittest.mock import MagicMock, patch
from diffsync import DiffSync
from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models import (
    Region,
    Site,
    Location,
    LocationType,
    Device,
    DeviceRole,
    DeviceType,
    Platform,
    Manufacturer,
)
from nautobot.extras.models import Status
from nautobot.tenancy.models import Tenant
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_dna_center.diffsync.models.nautobot import (
    NautobotArea,
    NautobotBuilding,
    NautobotFloor,
    NautobotDevice,
)


class TestNautobotArea(TransactionTestCase):
    """Test the NautobotArea class."""

    def setUp(self):
        self.diffsync = DiffSync()
        self.diffsync.job = MagicMock()
        self.diffsync.job.log_info = MagicMock()

    def test_create(self):
        """Validate the NautobotArea create() method creates a Region."""
        Region.objects.create(
            name="Global",
        )
        ids = {"name": "NY", "parent": "Global"}
        attrs = {}
        result = NautobotArea.create(self.diffsync, ids, attrs)
        self.assertIsInstance(result, NautobotArea)
        self.diffsync.job.log_info.assert_called_once_with(message="Creating Region NY.")
        region_obj = Region.objects.get(name=ids["name"])
        self.assertEqual(region_obj.parent.name, ids["parent"])

    def test_create_missing_parent(self):
        """Validate the NautobotArea create() method with missing parent Region."""
        ids = {"name": "TX", "parent": "USA"}
        attrs = {}
        NautobotArea.create(self.diffsync, ids, attrs)
        self.diffsync.job.log_warning.assert_called_once_with(
            message="Unable to find Region USA for TX. Region matching query does not exist."
        )

    def test_delete(self):
        """Validate the NautobotArea delete() method deletes a Region."""
        ds_mock_region = MagicMock(spec=Region)
        ds_mock_region.uuid = "1234567890"
        ds_mock_region.diffsync = MagicMock()
        ds_mock_region.diffsync.job.log_info = MagicMock()
        mock_region = MagicMock(spec=Region)
        mock_region.name = "Test"
        region_get_mock = MagicMock(return_value=mock_region)
        with patch.object(Region.objects, "get", region_get_mock):
            result = NautobotArea.delete(ds_mock_region)
        ds_mock_region.diffsync.job.log_info.assert_called_once_with(message="Deleting Region Test.")
        self.assertEqual(ds_mock_region, result)


class TestNautobotBuilding(TransactionTestCase):
    """Test the NautobotBuilding class."""

    databases = ("default", "job_logs")

    def setUp(self):
        super().setUp()

        self.diffsync = DiffSync()
        self.diffsync.job = MagicMock()
        self.diffsync.job.log_info = MagicMock()
        Tenant.objects.create(name="G&A")
        self.sec_site = Site.objects.create(name="Site 2", slug="site-2", status=Status.objects.get(name="Active"))
        self.sec_site.validated_save()
        self.test_bldg = NautobotBuilding(
            name="Site 2", address="", area="NY", latitude="", longitude="", tenant="G&A", uuid=self.sec_site.id
        )
        self.test_bldg.diffsync = MagicMock()
        self.test_bldg.diffsync.job = MagicMock()
        self.test_bldg.diffsync.job.log_info = MagicMock()

    def test_create_wo_parent(self):
        """Validate the NautobotBuilding create() method creates a Site without a matching parent Region."""
        ids = {"name": "HQ", "area": "NY"}
        attrs = {"address": "123 Main St", "latitude": "12.345", "longitude": "-67.890", "tenant": "G&A"}
        result = NautobotBuilding.create(self.diffsync, ids, attrs)
        self.assertIsInstance(result, NautobotBuilding)
        self.diffsync.job.log_info.assert_called_with(message="Unable to find parent NY")
        site_obj = Site.objects.get(name=ids["name"])
        self.assertFalse(getattr(site_obj, "region"))
        self.assertEqual(site_obj.physical_address, attrs["address"])
        self.assertEqual(site_obj.tenant.name, attrs["tenant"])

    def test_create_w_parent(self):
        """Validate the NautobotBuilding create() method creates a Site with a matching parent Region."""
        ids = {"name": "HQ", "area": "NY"}
        attrs = {"address": "123 Main St", "latitude": "12.345", "longitude": "-67.890", "tenant": "G&A"}
        ny_area = Region.objects.create(name="NY", slug="ny")
        ny_area.validated_save()
        result = NautobotBuilding.create(self.diffsync, ids, attrs)
        self.assertIsInstance(result, NautobotBuilding)
        self.diffsync.job.log_info.assert_called_once_with(message="Creating Site HQ.")
        site_obj = Site.objects.get(name=ids["name"])
        self.assertEqual(site_obj.region.name, ids["area"])
        self.assertEqual(site_obj.physical_address, attrs["address"])
        self.assertEqual(site_obj.tenant.name, attrs["tenant"])

    def test_update_w_tenant(self):
        """Validate the NautobotBuilding update() method updates a Site with a tenant."""
        update_attrs = {
            "address": "456 Wall St",
            "latitude": "23.456",
            "longitude": "-78.901",
            "tenant": "G&A",
        }
        actual = NautobotBuilding.update(self=self.test_bldg, attrs=update_attrs)
        self.test_bldg.diffsync.job.log_info.assert_called_once_with(message="Updating Site Site 2.")
        self.sec_site.refresh_from_db()
        self.assertEqual(self.sec_site.physical_address, update_attrs["address"])
        self.assertEqual(str(self.sec_site.latitude).rstrip("0"), update_attrs["latitude"])
        self.assertEqual(f"{self.sec_site.longitude:.3f}", update_attrs["longitude"])
        self.assertEqual(self.sec_site.tenant.name, update_attrs["tenant"])
        self.assertEqual(actual, self.test_bldg)

    def test_update_wo_tenant(self):
        """Validate the NautobotBuilding update() method updates a Site without a tenant."""
        update_attrs = {
            "address": "456 Wall St",
            "latitude": "23.456",
            "longitude": "-78.901",
            "tenant": "",
        }
        NautobotBuilding.update(self=self.test_bldg, attrs=update_attrs)
        self.sec_site.refresh_from_db()
        self.assertIsNone(self.sec_site.tenant)

    def test_delete(self):
        """Validate the NautobotBuilding delete() method deletes a Site."""
        ds_mock_site = MagicMock(spec=Site)
        ds_mock_site.uuid = "1234567890"
        ds_mock_site.diffsync = MagicMock()
        ds_mock_site.diffsync.job.log_info = MagicMock()
        mock_site = MagicMock(spec=Site)
        mock_site.name = "Test"
        site_get_mock = MagicMock(return_value=mock_site)
        with patch.object(Site.objects, "get", site_get_mock):
            result = NautobotBuilding.delete(ds_mock_site)
        ds_mock_site.diffsync.job.log_info.assert_called_once_with(message="Deleting Site Test.")
        self.assertEqual(ds_mock_site, result)


class TestNautobotFloor(TransactionTestCase):
    """Test the NautobotFloor class."""

    databases = ("default", "job_logs")

    def setUp(self):
        super().setUp()

        self.diffsync = DiffSync()
        self.diffsync.job = MagicMock()
        self.diffsync.job.log_info = MagicMock()
        Tenant.objects.create(name="G&A")
        self.hq_site, _ = Site.objects.get_or_create(name="HQ")

    def test_create(self):
        """Test the NautobotFloor create() method creates a LocationType: Floor."""
        ids = {"name": "HQ - Floor 1", "building": "HQ"}
        attrs = {"tenant": "G&A"}
        result = NautobotFloor.create(self.diffsync, ids, attrs)
        self.assertIsInstance(result, NautobotFloor)
        self.diffsync.job.log_info.assert_called_with(message="Creating Floor HQ - Floor 1.")
        floor_loc = LocationType.objects.get(name="Floor")
        self.assertEqual(len(floor_loc.content_types.filter(model="device")), 1)
        self.assertEqual(len(floor_loc.content_types.filter(model="rack")), 1)
        self.assertEqual(len(floor_loc.content_types.filter(model="rackgroup")), 1)
        floor_obj = Location.objects.get(name="HQ - Floor 1")
        self.assertEqual(floor_obj.name, ids["name"])
        self.assertEqual(floor_obj.site, self.hq_site)
        self.assertEqual(floor_obj.tenant.name, attrs["tenant"])

    def test_update_w_tenant(self):
        """Test the NautobotFloor update() method updates a LocationType: Floor with tenant."""
        floor_type, _ = LocationType.objects.get_or_create(name="Floor")
        mock_floor = Location.objects.create(
            name="HQ - Floor 2",
            slug="hq-floor2",
            location_type=floor_type,
            site=self.hq_site,
            status=Status.objects.get(name="Active"),
        )
        mock_floor.validated_save()
        test_floor = NautobotFloor(name="HQ - Floor 2", building="HQ", tenant="", uuid=mock_floor.id)
        test_floor.diffsync = MagicMock()
        test_floor.diffsync.job.log_info = MagicMock()
        update_attrs = {
            "tenant": "G&A",
        }
        actual = NautobotFloor.update(self=test_floor, attrs=update_attrs)
        test_floor.diffsync.job.log_info.assert_called_once_with(
            message="Updating Floor HQ - Floor 2 with {'tenant': 'G&A'}"
        )
        mock_floor.refresh_from_db()
        self.assertEqual(mock_floor.tenant.name, update_attrs["tenant"])
        self.assertEqual(actual, test_floor)

    def test_update_wo_tenant(self):
        """Test the NautobotFloor update() method updates a LocationType: Floor without tenant."""
        # I hate having to duplicate with above method but we can't have in setUp and test for ContentTypes.
        floor_type, _ = LocationType.objects.get_or_create(name="Floor")
        mock_floor = Location.objects.create(
            name="HQ - Floor 2",
            slug="hq-floor2",
            location_type=floor_type,
            site=self.hq_site,
            status=Status.objects.get(name="Active"),
        )
        mock_floor.validated_save()
        test_floor = NautobotFloor(name="HQ - Floor 2", building="HQ", tenant="", uuid=mock_floor.id)
        test_floor.diffsync = MagicMock()
        test_floor.diffsync.job.log_info = MagicMock()
        update_attrs = {
            "tenant": None,
        }
        NautobotFloor.update(self=test_floor, attrs=update_attrs)
        test_floor.diffsync.job.log_info.assert_called_once_with(
            message="Updating Floor HQ - Floor 2 with {'tenant': None}"
        )
        mock_floor.refresh_from_db()
        self.assertIsNone(mock_floor.tenant)

    def test_delete(self):
        """Validate the NautobotFloor delete() method deletes a LocationType: Floor."""
        ds_mock_floor = MagicMock(spec=Location)
        ds_mock_floor.uuid = "1234567890"
        ds_mock_floor.diffsync = MagicMock()
        ds_mock_floor.diffsync.job.log_info = MagicMock()
        mock_floor = MagicMock(spec=Location)
        mock_floor.name = "Test"
        mock_floor.site.name = "HQ"
        floor_get_mock = MagicMock(return_value=mock_floor)
        with patch.object(Location.objects, "get", floor_get_mock):
            result = NautobotFloor.delete(ds_mock_floor)
        ds_mock_floor.diffsync.job.log_info.assert_called_once_with(message="Deleting Floor Test in HQ.")
        self.assertEqual(ds_mock_floor, result)


class TestNautobotDevice(TransactionTestCase):
    """Test NautobotDevice class."""

    def setUp(self):
        super().setUp()

        self.diffsync = DiffSync()
        self.diffsync.job = MagicMock()
        self.diffsync.job.log_info = MagicMock()
        Tenant.objects.create(name="G&A")

        self.status_active = Status.objects.get(name="Active")
        self.ids = {
            "name": "core-router.testexample.com",
            "site": "HQ",
            "serial": "1234567890",
            "management_addr": "10.10.0.1",
        }
        self.attrs = {
            "floor": "HQ - Floor 1",
            "model": "Nexus 9300",
            "platform": "cisco_ios",
            "role": "core",
            "status": "Active",
            "tenant": "G&A",
            "vendor": "Cisco",
            "version": "16.12.3",
        }

    @patch("nautobot_ssot_dna_center.diffsync.models.nautobot.LIFECYCLE_MGMT", True)
    def test_create(self):
        """Test the NautobotDevice create() method creates a Device."""
        hq_site = Site.objects.create(name="HQ", slug="hq", status=self.status_active)
        floors = LocationType.objects.create(name="Floor", slug="floor")
        floors.content_types.add(ContentType.objects.get_for_model(Device))

        NautobotDevice.create(self.diffsync, self.ids, self.attrs)
        self.diffsync.job.log_info.assert_called_with(message="Creating Version 16.12.3 for cisco.ios.ios.")
        new_dev = Device.objects.get(name=self.ids["name"])
        self.assertEqual(new_dev.site, hq_site)
        self.assertEqual(new_dev.device_role, DeviceRole.objects.get(slug=self.attrs["role"]))
        self.assertEqual(
            new_dev.device_type,
            DeviceType.objects.get(
                model=self.attrs["model"], manufacturer=Manufacturer.objects.get(name=self.attrs["vendor"])
            ),
        )
        self.assertEqual(new_dev.platform, Platform.objects.get(slug=self.attrs["platform"]))
        self.assertEqual(new_dev.serial, self.ids["serial"])
        self.assertTrue(new_dev.location)
        self.assertEqual(new_dev.location.name, self.attrs["floor"])
        self.assertEqual(new_dev.tenant.name, self.attrs["tenant"])
        self.assertTrue(new_dev.custom_field_data["os_version"], self.attrs["version"])
