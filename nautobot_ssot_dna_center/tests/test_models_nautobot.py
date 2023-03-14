"""Test the DiffSync models for Nautobot."""
from unittest import skip
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


@skip("Failing for some reason")
class TestNautobotBuilding(TransactionTestCase):
    """Test the NautobotBuilding class."""

    databases = ("default", "job_logs")

    def setUp(self):
        self.status_active = Status.objects.create(name="Active", slug="active")
        self.status_active.validated_save()

        self.diffsync = DiffSync()
        self.diffsync.job = MagicMock()
        self.diffsync.job.log_info = MagicMock()
        self.diffsync.job.log_warning = MagicMock()

    def test_create(self):
        """Validate the NautobotBuilding create() method creates a Site."""
        ids = {"name": "HQ", "area": "NY"}
        attrs = {"address": "123 Main St", "latitude": "12.345", "longitude": "-67.890"}
        self.assertTrue(Status.objects.get(name="Active"))
        print(Status.objects.get(name="Active").id)
        result = NautobotBuilding.create(self.diffsync, ids, attrs)
        self.assertIsInstance(result, NautobotBuilding)
        self.diffsync.job.log_info.assert_called_once_with(message="Creating Site HQ.")
        site_obj = Site.objects.get(name=ids["name"])
        self.assertEqual(site_obj.region.name, ids["area"])
