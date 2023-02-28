"""Test DNACInstance."""
from django.test import TestCase

from nautobot_ssot_dna_center import models


class TestDNACInstance(TestCase):
    """Test DNACInstance."""

    def test_create_dnacinstance_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        dnacinstance = models.DNACInstance.objects.create(name="Development", slug="development")
        self.assertEqual(dnacinstance.name, "Development")
        self.assertEqual(dnacinstance.description, "")
        self.assertEqual(str(dnacinstance), "Development")
        self.assertEqual(dnacinstance.slug, "development")

    def test_create_dnacinstance_all_fields_success(self):
        """Create DNACInstance with all fields."""
        dnacinstance = models.DNACInstance.objects.create(
            name="Development", slug="development", description="Development Test"
        )
        self.assertEqual(dnacinstance.name, "Development")
        self.assertEqual(dnacinstance.slug, "development")
        self.assertEqual(dnacinstance.description, "Development Test")

    def test_to_csv(self):
        """Test the to_csv() method to ensure it returns the correct data from the DNACInstance model."""
        expected_data = (
            "Test Instance",
            "test_instance",
            "Test description",
            "https://dnac.testexample.com",
            443,
        )
        actual_instance = models.DNACInstance(
            name="Test Instance",
            slug="test_instance",
            description="Test description",
            host_url="https://dnac.testexample.com",
            port=443,
            verify=False,
        )
        actual_instance.validated_save()
        csv_data = actual_instance.to_csv()
        self.assertEqual(expected_data, csv_data)
