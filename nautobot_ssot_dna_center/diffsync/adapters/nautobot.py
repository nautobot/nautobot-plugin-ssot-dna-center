"""Nautobot Adapter for DNA Center SSoT plugin."""

from diffsync import DiffSync
from nautobot.dcim.models import Site as OrmSite
from nautobot_ssot_dna_center.diffsync.models.nautobot import NautobotDevice, NautobotSite


class NautobotAdapter(DiffSync):
    """DiffSync adapter for Nautobot."""

    site = NautobotSite
    device = NautobotDevice

    top_level = ["site", "device"]

    def __init__(self, *args, job=None, sync=None, **kwargs):
        """Initialize Nautobot.

        Args:
            job (object, optional): Nautobot job. Defaults to None.
            sync (object, optional): Nautobot DiffSync. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync

    def load_sites(self):
        """Load Site data from Nautobot into DiffSync models."""
        for site in OrmSite.objects.all():
            new_site = self.site(
                name=site.name,
                address=site.physical_address,
                site_type=None,
                parent=site.region.name,
                uuid=site.id,
            )
            self.add(new_site)

    def load(self):
        """Load data from Nautobot into DiffSync models."""
        self.load_sites()
