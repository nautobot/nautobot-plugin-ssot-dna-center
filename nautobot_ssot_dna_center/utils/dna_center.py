"""Utility functions for working with DNA Center."""

import logging
from dnacentersdk import api
from dnacentersdk.exceptions import ApiError

LOGGER = logging.getLogger(__name__)


class DnaCenterClient:
    """Client for handling all interactions with DNA Center."""

    def __init__(
        self, url: str, username: str, password: str, port: int = 443, verify: bool = True
    ):  # pylint: disable=too-many-arguments
        """Initialize instance of client."""
        self.url = url
        self.port = port
        self.base_url = f"{self.url}:{self.port}"
        self.username = username
        self.password = password
        self.verify = verify
        self.conn = None

    def connect(self):  # pylint: disable=inconsistent-return-statements
        """Connect to Cisco DNA Center."""
        try:
            self.conn = api.DNACenterAPI(
                base_url=self.base_url, username=self.username, password=self.password, verify=self.verify
            )
        except ApiError as err:
            LOGGER.error("Unable to connect to DNA Center: %s", err)

    def get_locations(self):
        """Retrieve all location data from DNA Center.

        Returns:
            list: List of Locations (Sites) from DNAC.
        """
        locations = []
        try:
            locations = self.conn.sites.get_site()["response"]
        except ApiError as err:
            LOGGER.error("Unable to get site information from DNA Center. %s", err)
        return locations

    @staticmethod
    def find_address_and_type(info: dict):
        """Find Site address and type from additionalInfo dict.

        Args:
            info (dict): Site additionalInfo property from DNA Center.

        Returns:
            tuple: Tuple of Site address and type.
        """
        address = ""
        site_type = ""
        for element in info:
            if element["nameSpace"] == "Location":
                address = element["attributes"]["address"]
                site_type = element["attributes"]["type"]
        return (address, site_type)

    @staticmethod
    def find_latitude_and_longitude(info: dict):
        """Find Site latitude and longitude from additionalInfo dict.

        Args:
            info (dict): Site additionalInfo property from DNA Center.

        Returns:
            tuple: Tuple of Site latitude and longitude.
        """
        latitude = ""
        longitude = ""
        for element in info:
            if element["nameSpace"] == "Location":
                latitude = element["attributes"]["latitude"]
                longitude = element["attributes"]["longitude"]
        return (latitude, longitude)

    def get_devices(self):
        """Retrieve all Device data from DNA Center."""
        dev_list = {}
        try:
            dev_list = self.conn.devices.get_device_list()["response"]
        except ApiError as err:
            LOGGER.error("Unable to get device information from DNA Center. %s", err)
        return dev_list

    def get_device_detail(self, dev_id: str):
        """Retrieve all Device data from DNA Center.

        Args:
            dev_id (str): ID of device in DNAC to query for details.

        Returns:
            dict: Details about specified dev_id.
        """
        dev_detail = {}
        try:
            dev_detail = self.conn.devices.get_device_detail(search_by=dev_id, identifier="uuid")["response"]
        except ApiError as err:
            LOGGER.error("Unable to get device detail information from DNA Center. %s", err)
        return dev_detail

    @staticmethod
    def parse_site_hierarchy(location_map: dict, site_hier: str):
        """Parse siteHierarchyGraphId attribute from get_device_detail response.

        Args:
            location_map (dict): Dictionary mapping location ID to name, parent, and location type.
            site_hier (str): The siteHierarchyGraphId field from the get_device_detail response.

        Returns:
            dict: Dictionary of location hierarchy for a device.
        """
        locations = site_hier.lstrip("/").rstrip("/").split("/")
        loc_data = {
            "areas": [],
            "building": None,
            "floor": None,
        }
        for location in locations:
            loc_type = location_map[location]["loc_type"]
            loc_name = location_map[location]["name"]
            if loc_type == "area":
                loc_data["areas"].append(loc_name)
            if loc_type == "building":
                loc_data["building"] = loc_name
            if loc_type == "floor":
                loc_data["floor"] = loc_name
        return loc_data

    def get_port_info(self, device_id: str):
        """Retrieve all interfaces for specified device_id from DNAC.

        Args:
            device_id (str): The ID of the Device that the Ports belong to.

        Returns:
            List[dict]: List of dictionaries of information about Ports on specified device_id.
        """
        ports = []
        try:
            ports = self.conn.devices.get_interface_info_by_id(device_id=device_id)["response"]
        except ApiError as err:
            LOGGER.error("Unable to get port information from DNA Center. %s", err)
        return ports
