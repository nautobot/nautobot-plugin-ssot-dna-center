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
