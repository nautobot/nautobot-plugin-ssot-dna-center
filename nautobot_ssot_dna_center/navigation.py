"""Menu items."""

from nautobot.apps.ui import NavMenuGroup, NavMenuItem, NavMenuTab, NavMenuAddButton, NavMenuImportButton


menu_items = (
    NavMenuTab(
        name="DNA_SSoT",
        groups=[
            NavMenuGroup(
                name="Device",
                items=[
                    NavMenuItem(
                        link="plugins:nautobot_ssot_dna_center:dnacinstance_list",
                        name="Nautobot SSoT for Cisco DNA Center",
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_ssot_dna_center:dnacinstance_add",
                                title="Add",
                                icon_class="mdi mdi-plus-thick",
                                permissions=["nautobot_ssot_dna_center.add_dnacinstance"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_ssot_dna_center:dnacinstance_import",
                                title="Bulk Import",
                                icon_class="mdi mdi-database-import-outline",
                                permissions=["nautobot_ssot_dna_center.add_dnacinstance"],
                            ),
                        ),
                    ),
                ],
            ),
        ],
    ),
)
