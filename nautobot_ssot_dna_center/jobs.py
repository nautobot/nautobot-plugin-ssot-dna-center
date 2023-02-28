"""Jobs for DNA Center SSoT integration."""

from django.urls import reverse
from diffsync import DiffSyncFlags
from nautobot.extras.choices import SecretsGroupAccessTypeChoices, SecretsGroupSecretTypeChoices
from nautobot.extras.jobs import BooleanVar, Job, MultiObjectVar
from nautobot_ssot.jobs.base import DataSource, DataMapping
from nautobot_ssot_dna_center.diffsync.adapters import dna_center, nautobot
from nautobot_ssot_dna_center.models import DNACInstance
from nautobot_ssot_dna_center.utils.dna_center import DnaCenterClient


name = "DNA Center SSoT"  # pylint: disable=invalid-name


class DnaCenterDataSource(DataSource, Job):
    """DNA Center SSoT Data Source."""

    instances = MultiObjectVar(
        model=DNACInstance,
        queryset=DNACInstance.objects.all(),
        display_field="display_name",
    )
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
        return {"Instances": "Found in Plugins menu."}

    @classmethod
    def data_mappings(cls):
        """List describing the data mappings involved in this DataSource."""
        return (
            DataMapping("Areas", None, "Regions", reverse("dcim:region_list")),
            DataMapping("Buildings", None, "Sites", reverse("dcim:site_list")),
            DataMapping("Floors", None, "Locations", reverse("dcim:location_list")),
            DataMapping("Devices", None, "Devices", reverse("dcim:device_list")),
            DataMapping("Interfaces", None, "Interfaces", reverse("dcim:interface_list")),
        )

    def load_source_adapter(self):
        """Load data from DNA Center into DiffSync models."""
        for instance in self.kwargs["instances"]:
            self.log_info(message=f"Loading data from {instance.name}")
            _sg = instance.auth_group
            username = _sg.get_secret_value(
                access_type=SecretsGroupAccessTypeChoices.TYPE_HTTP,
                secret_type=SecretsGroupSecretTypeChoices.TYPE_USERNAME,
            )
            password = _sg.get_secret_value(
                access_type=SecretsGroupAccessTypeChoices.TYPE_HTTP,
                secret_type=SecretsGroupSecretTypeChoices.TYPE_PASSWORD,
            )
            client = DnaCenterClient(
                url=instance.host_url,
                username=username,
                password=password,
                port=instance.port,
                verify=instance.verify,
            )
            client.connect()
            self.source_adapter = dna_center.DnaCenterAdapter(job=self, sync=self.sync, client=client)
            self.source_adapter.load()

    def load_target_adapter(self):
        """Load data from Nautobot into DiffSync models."""
        self.target_adapter = nautobot.NautobotAdapter(job=self, sync=self.sync)
        self.target_adapter.load()


jobs = [DnaCenterDataSource]
