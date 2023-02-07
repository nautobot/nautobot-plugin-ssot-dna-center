"""API nested serializers for nautobot_ssot_dna_center."""
from rest_framework import serializers

from nautobot.core.api import WritableNestedSerializer

from nautobot_ssot_dna_center import models


class DNACInstanceNestedSerializer(WritableNestedSerializer):
    """DNACInstance Nested Serializer."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_ssot_dna_center-api:dnacinstance-detail")

    class Meta:
        """Meta attributes."""

        model = models.DNACInstance
        fields = "__all__"
