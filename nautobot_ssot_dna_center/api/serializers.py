"""API serializers for nautobot_ssot_dna_center."""
from rest_framework import serializers

from nautobot.core.api.serializers import ValidatedModelSerializer

from nautobot_ssot_dna_center import models

from . import nested_serializers  # noqa: F401, pylint: disable=unused-import


class DNACInstanceSerializer(ValidatedModelSerializer):
    """DNACInstance Serializer."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_ssot_dna_center-api:dnacinstance-detail")

    class Meta:
        """Meta attributes."""

        model = models.DNACInstance
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []
