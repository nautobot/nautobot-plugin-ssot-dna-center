"""Test DNA Center adapter."""

import uuid
from unittest.mock import MagicMock

from django.contrib.contenttypes.models import ContentType
from nautobot.extras.models import Job, JobResult
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_dna_center.diffsync.adapters.dna_center import DnaCenterAdapter
from nautobot_ssot_dna_center.tests.fixtures import LOCATION_FIXTURE, DEVICE_FIXTURE
from nautobot_ssot_dna_center.jobs import DnaCenterDataSource


class TestDnaCenterAdapterTestCase(TransactionTestCase):
    """Test NautobotSsotDnaCenterAdapter class."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Initialize test case."""
        self.dna_center_client = MagicMock()
        self.dna_center_client.get_locations.return_value = LOCATION_FIXTURE
        self.dna_center_client.get_devices.return_value = DEVICE_FIXTURE
        self.dna_center_client.find_address_and_type.return_value = (
            "123 Main St, New York, New York 12345",
            "Building",
        )

        self.job = DnaCenterDataSource()
        self.job.job_result = JobResult.objects.create(
            name=self.job.class_path, obj_type=ContentType.objects.get_for_model(Job), user=None, job_id=uuid.uuid4()
        )
        self.dna_center = DnaCenterAdapter(job=self.job, sync=None, client=self.dna_center_client)

    def test_data_loading(self):
        """Test Nautobot SSoT for Cisco DNA Center load() function."""
        self.dna_center.load()
        self.assertEqual(
            {
                f"{site['name']}__{self.dna_center.dnac_site_map[site['parentId']] if site.get('parentId') else ''}"
                for site in LOCATION_FIXTURE
            },
            {site.get_unique_id() for site in self.dna_center.get_all("site")},
        )
