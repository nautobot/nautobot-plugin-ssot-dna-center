"""Forms for nautobot_ssot_dna_center."""
from django import forms
from nautobot.utilities.forms import (
    BootstrapMixin,
    BulkEditForm,
    SlugField,
)

from nautobot_ssot_dna_center import models


class DNACInstanceForm(BootstrapMixin, forms.ModelForm):
    """DNACInstance creation/edit form."""

    slug = SlugField()

    class Meta:
        """Meta attributes."""

        model = models.DNACInstance
        fields = [
            "name",
            "slug",
            "description",
            "host_url",
            "port",
            "auth_group",
        ]


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
        help_text="Search within Name or Slug.",
    )
    name = forms.CharField(required=False, label="Name")
    slug = forms.CharField(required=False, label="Slug")
    port = forms.IntegerField(required=False, label="Port")
    auth_group = forms.MultipleChoiceField(required=False, label="Secrets Group")

    class Meta:
        """Meta attributes."""

        model = models.DNACInstance
        # Define the fields above for ordering and widget purposes
        fields = [
            "q",
            "name",
            "slug",
            "port",
            "auth_group",
        ]
