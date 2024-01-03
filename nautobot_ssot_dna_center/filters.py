"""Filtering for nautobot_ssot_dna_center."""

import django_tables2 as tables
from nautobot.extras.models import SecretsGroup
from nautobot.core.filters import BaseFilterSet, NameSearchFilterSet, NaturalKeyOrPKMultipleChoiceFilter

from nautobot.core.tables import ToggleColumn
from nautobot_ssot_dna_center import models


class DNACInstanceFilterSet(BaseFilterSet, NameSearchFilterSet):
    """Filter for DNACInstance."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    host_url = tables.Column(linkify=False, verbose_name="Host URL")
    auth_group = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=SecretsGroup.objects.all(),
        label="Secrets Group",
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.DNACInstance

        # add any fields from the model that you would like to filter your searches by using those
        fields = ["id", "name", "description", "port"]
        default_columns = (
            "pk",
            "name",
            "host_url",
            "auth_group",
        )
