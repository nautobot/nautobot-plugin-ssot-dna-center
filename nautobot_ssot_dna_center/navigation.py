"""Menu items."""

from nautobot.extras.plugins import PluginMenuButton, PluginMenuItem
from nautobot.utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_ssot_dna_center:dnacinstance_list",
        link_text="Nautobot SSoT for Cisco DNA Center",
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_ssot_dna_center:dnacinstance_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_ssot_dna_center.add_dnacinstance"],
            ),
            PluginMenuButton(
                link="plugins:nautobot_ssot_dna_center:dnacinstance_import",
                title="Bulk Import",
                icon_class="mdi mdi-database-import-outline",
                color=ButtonColorChoices.BLUE,
                permissions=["nautobot_ssot_dna_center.add_dnacinstance"],
            ),
        ),
    ),
)
