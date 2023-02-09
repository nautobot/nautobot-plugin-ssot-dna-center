"""Utility functions for working with DNA Center."""

import logging
from dnacentersdk import api
from dnacentersdk.exceptions import ApiError

LOGGER = logging.getLogger(__name__)


class DnaCenterClient:
    """Client for handling all interactions with DNA Center."""

    def __init__(self, url: str, username: str, password: str, port: int = 443, verify: bool = True):
        """Initialize instance of client."""
        self.url = url
        self.port = port
        self.base_url = f"{self.url}:{self.port}"
        self.username = username
        self.password = password
        self.verify = verify
        self.conn = self.connect

    def connect(self):
        """Connect to Cisco DNA Center."""
        try:
            return api.DNACenterAPI(
                base_url=self.base_url, username=self.username, password=self.password, verify=self.verify
            )
        except ApiError as err:
            LOGGER.error("Unable to connect to DNA Center: %s", err)

    def get_sites(self):
        """Retrieve all Site data from DNA Center."""
        try:
            return self.conn.sites.get_site()["response"]
        except ApiError as err:
            LOGGER.error("Unable to get site information from DNA Center. %s", err)

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

    def get_devices(self):
        """Retrieve all Device data from DNA Center."""
        try:
            return self.conn.devices.get_device_list()["response"]
        except ApiError as err:
            LOGGER.error("Unable to get device information from DNA Center. %s", err)
