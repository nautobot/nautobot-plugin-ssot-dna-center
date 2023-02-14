"""Nautobot SSoT for Cisco DNA Center Adapter for DNA Center SSoT plugin."""

from diffsync import DiffSync
from diffsync.exceptions import ObjectNotFound
from nautobot_ssot_dna_center.diffsync.models.dna_center import (
    DnaCenterArea,
    DnaCenterBuilding,
    DnaCenterFloor,
    DnaCenterDevice,
)
from nautobot_ssot_dna_center.utils.dna_center import DnaCenterClient


class DnaCenterAdapter(DiffSync):
    """DiffSync adapter for DNA Center."""

    area = DnaCenterArea
    building = DnaCenterBuilding
    floor = DnaCenterFloor
    device = DnaCenterDevice

    top_level = ["area", "device"]

    def __init__(self, *args, job=None, sync=None, client: DnaCenterClient, **kwargs):
        """Initialize DNA Center.

        Args:
            job (object, optional): DNA Center job. Defaults to None.
            sync (object, optional): DNA Center DiffSync. Defaults to None.
            client (DnaCenterClient): DNA Center API client connection object.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync
        self.conn = client
        self.dnac_location_map = {}

    def load_locations(self):
        """Load location data from DNA Center into DiffSync models."""
        locations = self.conn.get_locations()
        if locations:
            self.dnac_location_map = {loc["id"]: {"name": loc["name"], "parent": None, "loc_type": "area"} for loc in locations}
            for location in locations:
                address = ""
                location_type = "area"
                if location.get("parentId"):
                    self.dnac_location_map[location["id"]]["parent"] = self.dnac_location_map[location["parentId"]][
                        "name"
                    ]
                if location.get("additionalInfo"):
                    address, location_type = self.conn.find_address_and_type(info=location["additionalInfo"])
                    self.dnac_location_map[location["id"]]["loc_type"] = location_type
                if location_type == "area":
                    new_area = self.area(
                        name=location["name"],
                        parent=self.dnac_location_map[location["parentId"]]["name"] if location.get("parentId") else "",
                        uuid=None,
                    )
                    self.add(new_area)
                if location_type == "building":
                    latitude, longitude = self.conn.find_latitude_and_longitude(info=location["additionalInfo"])
                    _area = self.dnac_location_map[location["parentId"]]["name"] if location.get("parentId") else ""
                    new_building = self.building(
                        name=location["name"],
                        address=address,
                        area=_area,
                        latitude=latitude,
                        longitude=longitude,
                        uuid=None,
                    )
                    self.add(new_building)
                    try:
                        parent = self.get(self.area, _area)
                        parent.add_child(new_building)
                    except ObjectNotFound as err:
                        self.job.log_warning(
                            message=f"Unable to find area {parent} for building {location['name']}. {err}"
                        )
                if location_type == "floor":
                    _building = self.dnac_location_map[location["parentId"]]["name"] if location.get("parentId") else ""
                    _area = self.dnac_location_map[location["parentId"]]["parent"]
                    new_floor = self.floor(
                        name=location["name"],
                        building=_building,
                        uuid=None,
                    )
                    self.add(new_floor)
                    try:
                        parent = self.get(self.building, {"name": _building, "area": _area})
                        parent.add_child(new_floor)
                    except ObjectNotFound as err:
                        self.job.log_warning(
                            message=f"Unable to find building {_building} in area {_area} for floor {location['name']}. {err}"
                        )

    def load_devices(self):
        """Load Device data from DNA Center info DiffSync models."""
        pass

    def load(self):
        """Load data from DNA Center into DiffSync models."""
        self.load_sites()
        self.load_devices()
