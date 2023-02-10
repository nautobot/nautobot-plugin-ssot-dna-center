"""Create fixtures for tests."""
import json
from nautobot_ssot_dna_center.models import DNACInstance


def load_json(path):
    """Load a json file."""
    with open(path, encoding="utf-8") as file:
        return json.loads(file.read())


SITE_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_sites.json")
DEVICE_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_devices.json")


def create_dnacinstance():
    """Fixture to create necessary number of DNACInstance for tests."""
    DNACInstance.objects.create(name="Test One", slug="test-one", port=443)
    DNACInstance.objects.create(name="Test Two", slug="test-two", port=443)
    DNACInstance.objects.create(name="Test Three", slug="test-three", port=443)
