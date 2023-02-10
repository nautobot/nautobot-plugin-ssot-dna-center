"""Unit tests for views."""
from nautobot.utilities.testing import ViewTestCases

from nautobot_ssot_dna_center import models
from nautobot_ssot_dna_center.tests import fixtures


class DNACInstanceViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the DNACInstance views."""

    model = models.DNACInstance
    bulk_edit_data = {"description": "Bulk edit views"}
    form_data = {
        "name": "Test 1",
        "slug": "test-1",
        "description": "Initial model",
        "port": 443,
    }

    @classmethod
    def setUpTestData(cls):
        fixtures.create_dnacinstance()

    def test_bulk_import_objects_with_constrained_permission(self):
        pass

    def test_bulk_import_objects_with_permission(self):
        pass

    def test_bulk_import_objects_without_permission(self):
        pass

    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    def test_has_advanced_tab(self):
        pass
