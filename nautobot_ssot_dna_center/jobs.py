"""Jobs for DNA Center SSoT integration."""

from django.urls import reverse
from django.templatetags.static import static
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
        self.diffsync_flags = (
            self.diffsync_flags | DiffSyncFlags.CONTINUE_ON_FAILURE  # pylint: disable=unsupported-binary-operation
        )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta data for DNA Center."""

        name = "DNA Center to Nautobot"
        data_source = "DNA Center"
        data_target = "Nautobot"
        description = "Sync information from DNA Center to Nautobot"
        data_source_icon = static("nautobot_ssot_dna_center/dna_center_logo.png")

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
            DataMapping("IP Addresses", None, "IP Addresses", reverse("ipam:ipaddress_list")),
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
            self.source_adapter = dna_center.DnaCenterAdapter(
                job=self, sync=self.sync, client=client, tenant=instance.tenant
            )
            self.source_adapter.load()

    def load_target_adapter(self):
        """Load data from Nautobot into DiffSync models."""
        self.target_adapter = nautobot.NautobotAdapter(job=self, sync=self.sync)
        self.target_adapter.load()

    def execute_sync(self):
        """Execute the synchronization of data from DNA Center to Nautobot."""

    def post_run(self):
        """Execute sync after Job is complete so the transactions are not atomic."""
        if not self.kwargs["dry_run"]:
            self.log_info(message="Beginning synchronization of data from DNA Center into Nautobot.")
            if self.source_adapter is not None and self.target_adapter is not None:
                self.source_adapter.sync_to(self.target_adapter, flags=self.diffsync_flags)
            else:
                self.log_warning(message="Not both adapters were properly initialized prior to synchronization.")
        self.log_info(message="Synchronization from DNA Center into Nautobot is complete.")


jobs = [DnaCenterDataSource]
