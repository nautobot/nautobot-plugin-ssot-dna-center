"""API views for nautobot_ssot_dna_center."""

from nautobot.core.api.views import ModelViewSet

from nautobot_ssot_dna_center import filters, models

from nautobot_ssot_dna_center.api import serializers


class DNACInstanceViewSet(ModelViewSet):  # pylint: disable=too-many-ancestors
    """DNACInstance viewset."""

    queryset = models.DNACInstance.objects.all()
    serializer_class = serializers.DNACInstanceSerializer
    filterset_class = filters.DNACInstanceFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
