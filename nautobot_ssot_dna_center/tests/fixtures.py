"""Create fixtures for tests."""
from nautobot_ssot_dna_center.models import DNACInstance


def create_dnacinstance():
    """Fixture to create necessary number of DNACInstance for tests."""
    DNACInstance.objects.create(name="Test One", slug="test-one", port=443)
    DNACInstance.objects.create(name="Test Two", slug="test-two", port=443)
    DNACInstance.objects.create(name="Test Three", slug="test-three", port=443)
