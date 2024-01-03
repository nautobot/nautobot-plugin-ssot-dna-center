"""Forms for nautobot_ssot_dna_center."""
from django import forms
from nautobot.tenancy.models import Tenant
from nautobot.core.forms import (
    BootstrapMixin,
    BulkEditForm,
)

from nautobot_ssot_dna_center import models


class DNACInstanceForm(BootstrapMixin, forms.ModelForm):
    """DNACInstance creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.DNACInstance
        fields = ["name", "description", "host_url", "port", "verify", "auth_group", "tenant"]


class DNACInstanceBulkEditForm(BootstrapMixin, BulkEditForm):
    """DNACInstance bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.DNACInstance.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class DNACInstanceFilterForm(BootstrapMixin, forms.ModelForm):
    """Filter form to filter searches."""

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")
    port = forms.IntegerField(required=False, label="Port")
    verify = forms.BooleanField(required=True, label="Verify SSL")
    auth_group = forms.MultipleChoiceField(required=False, label="Secrets Group")
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False, label="Tenant")

    class Meta:
        """Meta attributes."""

        model = models.DNACInstance
        # Define the fields above for ordering and widget purposes
        fields = ["q", "name", "port", "verify", "auth_group", "tenant"]


class DNACInstanceCSVImportForm(BootstrapMixin, forms.ModelForm):
    """Form for entering CSV to bulk-import DNAC instances."""

    class Meta:
        """Class to define what is used for bulk import of instances form using CSV."""

        model = models.DNACInstance
        fields = models.DNACInstance.csv_headers
