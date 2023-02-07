"""Jobs for DNA Center SSoT integration."""

from diffsync import DiffSyncFlags
from nautobot.extras.jobs import BooleanVar, Job
from nautobot_ssot.jobs.base import DataSource
from nautobot_ssot_dna_center.diffsync.adapters import dna_center, nautobot


name = "DNA Center SSoT"  # pylint: disable=invalid-name


class DnaCenterDataSource(DataSource, Job):
    """DNA Center SSoT Data Source."""

    debug = BooleanVar(description="Enable for more verbose debug logging", default=False)

    def __init__(self):
        """Initialize DNA Center Data Source."""
        super().__init__()
        self.diffsync_flags = self.diffsync_flags | DiffSyncFlags.CONTINUE_ON_FAILURE

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta data for DNA Center."""

        name = "DNA Center to Nautobot"
        data_source = "DNA Center"
        data_target = "Nautobot"
        description = "Sync information from DNA Center to Nautobot"

    @classmethod
    def config_information(cls):
        """Dictionary describing the configuration of this DataSource."""
        return {}

    @classmethod
    def data_mappings(cls):
        """List describing the data mappings involved in this DataSource."""
        return ()

    def load_source_adapter(self):
        """Load data from DNA Center into DiffSync models."""
        self.source_adapter = dna_center.DnaCenterAdapter(job=self, sync=self.sync)
        self.source_adapter.load()

    def load_target_adapter(self):
        """Load data from Nautobot into DiffSync models."""
        self.target_adapter = nautobot.NautobotAdapter(job=self, sync=self.sync)
        self.target_adapter.load()


jobs = [DnaCenterDataSource]
