"""Nautobot SSoT for Cisco DNA Center Adapter for DNA Center SSoT plugin."""

from diffsync import DiffSync
from nautobot_ssot_dna_center.diffsync.models.dna_center import DnaCenterSite, DnaCenterDevice
from nautobot_ssot_dna_center.utils.dna_center import DnaCenterClient


class DnaCenterAdapter(DiffSync):
    """DiffSync adapter for DNA Center."""

    site = DnaCenterSite
    device = DnaCenterDevice

    top_level = ["site", "device"]

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
        self.dnac_site_map = {}

    def load_sites(self):
        """Load Site data from DNA Center into DiffSync models."""
        sites = self.conn.get_sites()
        if sites:
            self.dnac_site_map = {site["id"]: site["name"] for site in sites}
            for site in sites:
                address, site_type = self.conn.find_address_and_type(info=site["additionalInfo"])
                new_site = self.site(
                    name=site["name"],
                    address=address,
                    site_type=site_type,
                    parent=self.dnac_site_map[site["parentId"]] if site.get("parentId") else "",
                )
                self.add(new_site)

    def load_devices(self):
        """Load Device data from DNA Center info DiffSync models."""
        pass

    def load(self):
        """Load data from DNA Center into DiffSync models."""
        self.load_sites()
        self.load_devices()
