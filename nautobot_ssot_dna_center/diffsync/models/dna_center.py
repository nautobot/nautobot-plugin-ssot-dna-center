"""Nautobot SSoT for Cisco DNA Center DiffSync models for Nautobot SSoT for Cisco DNA Center SSoT."""

from nautobot_ssot_dna_center.diffsync.models.base import Device, Site


class DnaCenterSite(Site):
    """DNA Center implementation of Site DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Site in DNA Center from Site object."""
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Site in DNA Center from Site object."""
        return super().update(attrs)

    def delete(self):
        """Delete Site in DNA Center from Site object."""
        return self


class DnaCenterDevice(Device):
    """DNA Center implementation of Device DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Device in DNA Center from Device object."""
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Device in DNA Center from Device object."""
        return super().update(attrs)

    def delete(self):
        """Delete Device in DNA Center from Device object."""
        return self
