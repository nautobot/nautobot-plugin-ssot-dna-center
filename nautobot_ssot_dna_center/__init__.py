"""Plugin declaration for nautobot_ssot_dna_center."""
from importlib import metadata
from nautobot.core.signals import nautobot_database_ready
from nautobot.extras.plugins import PluginConfig
from nautobot_ssot_dna_center.signals import nautobot_database_ready_callback

__version__ = metadata.version(__name__)


class NautobotSsotDnaCenterConfig(PluginConfig):
    """Plugin configuration for the nautobot_ssot_dna_center plugin."""

    name = "nautobot_ssot_dna_center"
    verbose_name = "Nautobot SSoT for Cisco DNA Center"
    version = __version__
    author = "Justin Drew"
    description = "Nautobot SSoT for Cisco DNA Center."
    base_url = "ssot-dna-center"
    required_settings = ["import_global", "update_locations"]
    min_version = "1.4.0"
    max_version = "1.9999"
    default_settings = {"import_global": True, "update_locations": True}
    caching_config = {}

    def ready(self):
        """Trigger callback when database is ready."""
        super().ready()

        nautobot_database_ready.connect(nautobot_database_ready_callback, sender=self)


config = NautobotSsotDnaCenterConfig  # pylint:disable=invalid-name
