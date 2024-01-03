"""Test DNACInstance."""
from django.test import TestCase
from nautobot.tenancy.models import Tenant
from nautobot_ssot_dna_center import models


class TestDNACInstance(TestCase):
    """Test DNACInstance."""

    def test_create_dnacinstance_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        dnacinstance = models.DNACInstance.objects.create(
            name="Development",
            host_url="https://dnac.testexample.com",
        )
        self.assertEqual(dnacinstance.name, "Development")
        self.assertEqual(dnacinstance.description, "")
        self.assertEqual(str(dnacinstance), "Development")

    def test_create_dnacinstance_all_fields_success(self):
        """Create DNACInstance with all fields."""
        tenant = Tenant.objects.create(name="Dev")
        dnacinstance = models.DNACInstance.objects.create(
            name="Development",
            description="Development Test",
            host_url="https://dnac.testexample.com",
            tenant=tenant,
        )
        self.assertEqual(dnacinstance.name, "Development")
        self.assertEqual(dnacinstance.description, "Development Test")
        self.assertTrue(dnacinstance.verify)
        self.assertEqual(dnacinstance.tenant.name, "Dev")

    def test_to_csv(self):
        """Test the to_csv() method to ensure it returns the correct data from the DNACInstance model."""
        expected_data = (
            "Test Instance",
            "Test description",
            "https://dnac.testexample.com",
            443,
            False,
            None,
        )
        actual_instance = models.DNACInstance(
            name="Test Instance",
            description="Test description",
            host_url="https://dnac.testexample.com",
            port=443,
            verify=False,
        )
        actual_instance.validated_save()
        csv_data = actual_instance.to_csv()
        self.assertEqual(expected_data, csv_data)
