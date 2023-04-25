"""Tables for nautobot_ssot_dna_center."""

import django_tables2 as tables
from nautobot.utilities.tables import BaseTable, ButtonsColumn, ToggleColumn

from nautobot_ssot_dna_center import models


class DNACInstanceTable(BaseTable):
    # pylint: disable=too-few-public-methods
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    host_url = tables.Column(linkify=False)
    port = tables.Column(linkify=False)
    auth_group = tables.Column(linkify=True)
    tenant = tables.Column(linkify=True)
    actions = ButtonsColumn(
        models.DNACInstance,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        # pk_field="slug",
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.DNACInstance
        fields = (
            "pk",
            "name",
            "port",
            "auth_group",
            "tenant",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = ("pk", "name", "host_url", "port", "auth_group", "tenant")
