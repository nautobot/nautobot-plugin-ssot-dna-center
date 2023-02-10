"""Test dnacinstance forms."""
from django.test import TestCase

from nautobot_ssot_dna_center import forms


class DNACInstanceTest(TestCase):
    """Test DNACInstance forms."""

    def test_specifying_all_fields_success(self):
        form = forms.DNACInstanceForm(
            data={
                "name": "Development",
                "slug": "development",
                "description": "Development Testing",
                "port": 443,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.DNACInstanceForm(
            data={
                "name": "Development",
                "slug": "development",
                "port": 443,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_dnacinstance_is_required(self):
        form = forms.DNACInstanceForm(data={"slug": "development"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])

    def test_validate_slug_is_required(self):
        form = forms.DNACInstanceForm(data={"name": "Development"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["slug"])

    def test_validate_port_is_required(self):
        form = forms.DNACInstanceForm(data={"name": "Development", "slug": "development"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["port"])
