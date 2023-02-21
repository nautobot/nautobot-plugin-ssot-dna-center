"""Unit tests for nautobot_ssot_dna_center."""
from unittest import skip
from nautobot.utilities.testing import APIViewTestCases
from nautobot_ssot_dna_center import models
from nautobot_ssot_dna_center.tests import fixtures


class DNACInstanceAPIViewTest(APIViewTestCases.APIViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the API viewsets for DNACInstance."""

    model = models.DNACInstance
    create_data = [
        {
            "name": "Test Model 1",
            "slug": "test-model-1",
            "port": 443,
        },
        {
            "name": "Test Model 2",
            "slug": "test-model-2",
            "port": 443,
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}
    brief_fields = [
        "auth_group",
        "created",
        "description",
        "display",
        "host_url",
        "id",
        "last_updated",
        "name",
        "port",
        "slug",
        "url",
        "verify",
    ]

    @classmethod
    def setUpTestData(cls):
        fixtures.create_dnacinstance()

    @skip("Not Implemented")
    def test_get_object(self):
        pass
