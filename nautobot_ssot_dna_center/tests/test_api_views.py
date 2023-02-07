"""Unit tests for nautobot_ssot_dna_center."""
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
        },
        {
            "name": "Test Model 2",
            "slug": "test-model-2",
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}
    brief_fields = ["created", "description", "display", "id", "last_updated", "name", "slug", "url"]

    @classmethod
    def setUpTestData(cls):
        fixtures.create_dnacinstance()
