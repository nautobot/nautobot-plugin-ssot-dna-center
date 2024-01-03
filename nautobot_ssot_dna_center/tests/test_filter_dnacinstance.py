"""Test DNACInstance Filter."""
from django.test import TestCase
from nautobot_ssot_dna_center import filters
from nautobot_ssot_dna_center import models
from nautobot_ssot_dna_center.tests import fixtures


class DNACInstanceFilterTestCase(TestCase):
    """DNACInstance Filter Test Case."""

    queryset = models.DNACInstance.objects.all()
    filterset = filters.DNACInstanceFilterSet

    @classmethod
    def setUpTestData(cls):
        """Setup test data for DNACInstance Model."""
        fixtures.create_dnacinstance()

    def test_q_search_name(self):
        """Test using Q search with name of DNACInstance."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for DNACInstance."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
