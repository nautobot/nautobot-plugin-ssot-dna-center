"""Models for Nautobot SSoT for Cisco DNA Center."""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from nautobot.core.fields import AutoSlugField
from nautobot.core.models.generics import PrimaryModel


class DNACInstance(PrimaryModel):  # pylint: disable=too-many-ancestors
    """Base model for Nautobot SSoT for Cisco DNA Center plugin."""

    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True)
    description = models.CharField(max_length=200, blank=True)
    host_url = models.CharField(
        max_length=255, blank=True, help_text="URL to DNAC instance including protocol.", verbose_name="Host URL"
    )
    port = models.IntegerField(default=443)
    verify = models.BooleanField(verbose_name="Verify SSL", default=True)
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
        verbose_name="Tenant",
    )
    auth_group = models.ForeignKey(
        to="extras.SecretsGroup",
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
        verbose_name="Secrets Group",
    )

    csv_headers = ["name", "slug", "description", "host_url", "port", "verify", "tenant"]

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name = "DNA Center Instance"
        verbose_name_plural = "DNA Center Instances"

    def get_absolute_url(self):
        """Return detail view for DNACInstance."""
        return reverse("plugins:nautobot_ssot_dna_center:dnacinstance", args=[self.slug])

    def __str__(self):
        """Stringify instance."""
        return self.name

    def to_csv(self):
        """Export model fields to CSV file."""
        return (self.name, self.slug, self.description, self.host_url, self.port, self.verify, self.tenant)

    def clean(self):
        """Validate all required object attributes have been defined or throw ValidationError."""
        if not self.name:
            raise ValidationError({"name": "Name for DNAC Instance must be defined."})

        if not self.host_url:
            raise ValidationError({"host_url": "Host URL for DNAC instance must be defined."})
