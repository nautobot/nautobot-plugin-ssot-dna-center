"""Test the DiffSync models for Nautobot."""
from unittest.mock import MagicMock, patch
from diffsync import DiffSync
from nautobot.dcim.models import Region, Site
from nautobot.extras.models import Status
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_dna_center.diffsync.models.nautobot import NautobotArea, NautobotBuilding


class TestNautobotArea(TransactionTestCase):
    """Test the NautobotArea class."""

    def setUp(self):
        self.diffsync = DiffSync()
        self.diffsync.job = MagicMock()
        self.diffsync.job.log_info = MagicMock()
        self.diffsync.job.log_warning = MagicMock()

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
        self.diffsync.job.log_warning = MagicMock()

    def test_create_wo_parent(self):
        """Validate the NautobotBuilding create() method creates a Site without a matching parent Region."""
        ids = {"name": "HQ", "area": "NY"}
        attrs = {"address": "123 Main St", "latitude": "12.345", "longitude": "-67.890"}
        result = NautobotBuilding.create(self.diffsync, ids, attrs)
        self.assertIsInstance(result, NautobotBuilding)
        self.diffsync.job.log_info.assert_called_with(message="Unable to find parent NY")
        site_obj = Site.objects.get(name=ids["name"])
        self.assertFalse(getattr(site_obj, "region"))

    def test_create_w_parent(self):
        """Validate the NautobotBuilding create() method creates a Site with a matching parent Region."""
        ids = {"name": "HQ", "area": "NY"}
        attrs = {"address": "123 Main St", "latitude": "12.345", "longitude": "-67.890"}
        ny_area = Region.objects.create(name="NY", slug="ny")
        ny_area.validated_save()
        result = NautobotBuilding.create(self.diffsync, ids, attrs)
        self.assertIsInstance(result, NautobotBuilding)
        self.diffsync.job.log_info.assert_called_once_with(message="Creating Site HQ.")
        site_obj = Site.objects.get(name=ids["name"])
        self.assertEqual(site_obj.region.name, ids["area"])

    def test_update(self):
        """Validate the NautobotBuilding update() method updates a Site."""
        hq_site = Site.objects.create(name="HQ", slug="hq", status=Status.objects.get(name="Active"))
        hq_site.validated_save()
        test_bldg = NautobotBuilding(name="HQ", address="", area="NY", latitude="", longitude="", uuid=hq_site.id)
        test_bldg.diffsync = MagicMock()
        test_bldg.diffsync.job = MagicMock()
        test_bldg.diffsync.job.log_info = MagicMock()
        update_attrs = {
            "address": "123 Main St",
            "latitude": "12.345",
            "longitude": "-67.890",
        }
        actual = NautobotBuilding.update(self=test_bldg, attrs=update_attrs)
        test_bldg.diffsync.job.log_info.assert_called_once_with(message="Updating Site HQ.")
        hq_site.refresh_from_db()
        self.assertEqual(hq_site.physical_address, update_attrs["address"])
        self.assertEqual(str(hq_site.latitude).rstrip("0"), update_attrs["latitude"])
        self.assertEqual(f"{hq_site.longitude:.3f}", update_attrs["longitude"])
        self.assertEqual(actual, test_bldg)
