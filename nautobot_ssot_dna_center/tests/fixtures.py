"""Create fixtures for tests."""
import json
from nautobot_ssot_dna_center.models import DNACInstance


def load_json(path):
    """Load a json file."""
    with open(path, encoding="utf-8") as file:
        return json.loads(file.read())


LOCATION_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_locations.json")
RECV_LOCATION_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_locations_recv.json")
DEVICE_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_devices.json")
RECV_DEVICE_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_devices_recv.json")
DEVICE_DETAIL_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_device_detail.json")
RECV_DEVICE_DETAIL_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_device_detail_recv.json")
PORT_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_port_info.json")
RECV_PORT_FIXTURE = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/get_port_info_recv.json")

EXPECTED_AREAS = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/expected_areas.json")
EXPECTED_BUILDINGS = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/expected_buildings.json")
EXPECTED_FLOORS = load_json(path="./nautobot_ssot_dna_center/tests/fixtures/expected_floors.json")


def create_dnacinstance():
    """Fixture to create necessary number of DNACInstance for tests."""
    url = "http://dnac.testexample.com"
    DNACInstance.objects.create(name="Test One", slug="test-one", port=443, host_url=url)
    DNACInstance.objects.create(name="Test Two", slug="test-two", port=443, host_url=url)
    DNACInstance.objects.create(name="Test Three", slug="test-three", port=443, host_url=url)
