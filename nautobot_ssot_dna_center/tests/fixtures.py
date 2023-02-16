"""Create fixtures for tests."""
import json
from nautobot_ssot_dna_center.models import DNACInstance


def load_json(path):
    """Load a json file."""
    with open(path, encoding="utf-8") as file:
        return json.loads(file.read())


LOCATION_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_locations.json")
DEVICE_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_devices.json")
DEVICE_DETAIL_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_device_detail.json")

EXPECTED_AREAS = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/expected_areas.json")
EXPECTED_BUILDINGS = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/expected_buildings.json")
EXPECTED_FLOORS = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/expected_floors.json")


def create_dnacinstance():
    """Fixture to create necessary number of DNACInstance for tests."""
    DNACInstance.objects.create(name="Test One", slug="test-one", port=443)
    DNACInstance.objects.create(name="Test Two", slug="test-two", port=443)
    DNACInstance.objects.create(name="Test Three", slug="test-three", port=443)
