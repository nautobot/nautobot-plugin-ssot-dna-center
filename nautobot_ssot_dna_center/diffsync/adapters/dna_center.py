"""Nautobot SSoT for Cisco DNA Center Adapter for DNA Center SSoT plugin."""

from diffsync import DiffSync
from diffsync.exceptions import ObjectNotFound
from nautobot_ssot_dna_center.constants import DNAC_PLATFORM_MAPPER
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
            # to ensure we process locations in the appropriate order we need to split them into their own list of locations
            self.dnac_location_map = self.build_dnac_location_map(locations)
            areas, buildings, floors = self.parse_and_sort_locations(locations)
            for location in areas:
                address = ""
                if location.get("parentId"):
                    self.dnac_location_map[location["id"]]["parent"] = self.dnac_location_map[location["parentId"]][
                        "name"
                    ]
                if location.get("additionalInfo"):
                    address, _ = self.conn.find_address_and_type(info=location["additionalInfo"])
                new_area = self.area(
                    name=location["name"],
                    parent=self.dnac_location_map[location["parentId"]]["name"] if location.get("parentId") else None,
                    uuid=None,
                )
                self.add(new_area)
            for location in buildings:
                address, _ = self.conn.find_address_and_type(info=location["additionalInfo"])
                latitude, longitude = self.conn.find_latitude_and_longitude(info=location["additionalInfo"])
                _area = (
                    self.dnac_location_map[location["parentId"]]
                    if location.get("parentId")
                    else {"name": "Global", "parent": None}
                )
                new_building = self.building(
                    name=location["name"],
                    address=address,
                    area=_area["name"],
                    latitude=latitude[:9].rstrip("0"),
                    longitude=longitude[:7].rstrip("0"),
                    uuid=None,
                )
                self.add(new_building)
                try:
                    parent = self.get(self.area, {"name": _area["name"], "parent": _area["parent"]})
                    parent.add_child(new_building)
                except ObjectNotFound as err:
                    self.job.log_warning(
                        message=f"Unable to find area {_area['name']} for building {location['name']}. {err}"
                    )
            for location in floors:
                _building = self.dnac_location_map[location["parentId"]] if location.get("parentId") else {}
                new_floor = self.floor(
                    name=f"{_building['name']} - {location['name']}",
                    building=_building["name"],
                    uuid=None,
                )
                self.add(new_floor)
                try:
                    parent = self.get(self.building, {"name": _building["name"], "area": _building["parent"]})
                    parent.add_child(new_floor)
                except ObjectNotFound as err:
                    self.job.log_warning(
                        message=f"Unable to find building {_building['name']} in area {_building['parent']} for floor {location['name']}. {err}"
                    )

    def parse_and_sort_locations(self, locations: list):
        """Separate locations into areas, buildings, and floors for processing. Also sort by siteHierarchy.

        Args:
            locations (list): List of Locations (Sites) from DNAC to be separated.

        Returns:
            tuple (List[dict], List[dict], List[dict]): Tuple containing lists of areas, buildings, and floors in DNAC to be processed.
        """
        areas, buildings, floors = [], [], []
        for location in locations:
            for info in location["additionalInfo"]:
                if info["attributes"].get("type") == "building":
                    buildings.append(location)
                    self.dnac_location_map[location["id"]]["loc_type"] = "building"
                    break
                elif info["attributes"].get("type") == "floor":
                    floors.append(location)
                    self.dnac_location_map[location["id"]]["loc_type"] = "floor"
                    break
            else:
                areas.append(location)
            if location.get("parentId"):
                self.dnac_location_map[location["id"]]["parent"] = self.dnac_location_map[location["parentId"]]["name"]
        # sort areas by length of siteHierarchy so that parent areas loaded before child areas.
        areas = sorted(areas, key=lambda x: len(x["siteHierarchy"].split("/")))
        return areas, buildings, floors

    def build_dnac_location_map(self, locations: list):
        """Build out the initial DNAC location map for Location ID to name and type.

        Args:
            locations (list): List of Locations (Sites) from DNAC.

        Returns:
            dict: Dictionary of Locations mapped with ID to their name and location type.
        """
        return {loc["id"]: {"name": loc["name"], "parent": None, "loc_type": "area"} for loc in locations}

    def load_devices(self):
        """Load Device data from DNA Center info DiffSync models."""
        devices = self.conn.get_devices()
        for dev in devices:
            platform = "unknown"
            vendor = "Cisco"
            if dev["softwareType"] in DNAC_PLATFORM_MAPPER:
                platform = DNAC_PLATFORM_MAPPER[dev["softwareType"]]
            else:
                if not dev.get("softwareType") and "Meraki" in dev["family"]:
                    platform = "meraki"
            if "Juniper" in dev["type"]:
                vendor = "Juniper"
            dev_details = self.conn.get_device_detail(dev_id=dev["id"])
            if dev_details and dev_details.get("siteHierarchyGraphId"):
                loc_data = self.conn.parse_site_hierarchy(
                    location_map=self.dnac_location_map, site_hier=dev_details["siteHierarchyGraphId"]
                )
            else:
                self.job.log_warning(message=f"Unable to find Site for {dev['hostname']} so skipping.")
                continue
            print(f"Loc Data: {loc_data}")
            new_dev = self.device(
                name=dev["hostname"],
                status="Active" if dev.get("reachabilityStatus") != "Unreachable" else "Offline",
                role=dev["role"],
                vendor=vendor,
                model=dev["platformId"],
                area=loc_data["areas"][-1],
                site=loc_data["building"],
                floor=f"{loc_data['building']} - {loc_data['floor']}" if loc_data.get("floor") else "",
                serial=dev.get("serialNumber"),
                version=dev.get("softwareVersion"),
                platform=platform,
                uuid=None,
            )
            self.add(new_dev)

    def load(self):
        """Load data from DNA Center into DiffSync models."""
        self.load_locations()
        self.load_devices()
