"""Plugin declaration for nautobot_ssot_dna_center."""
# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from nautobot.extras.plugins import PluginConfig


class NautobotSsotDnaCenterConfig(PluginConfig):
    """Plugin configuration for the nautobot_ssot_dna_center plugin."""

    name = "nautobot_ssot_dna_center"
    verbose_name = "Nautobot SSoT for Cisco DNA Center"
    version = __version__
    author = "Justin Drew"
    description = "Nautobot SSoT for Cisco DNA Center."
    base_url = "ssot-dna-center"
    required_settings = []
    min_version = "1.4.0"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}


config = NautobotSsotDnaCenterConfig  # pylint:disable=invalid-name
