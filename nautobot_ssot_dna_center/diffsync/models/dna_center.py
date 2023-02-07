"""Nautobot SSoT for Cisco DNA Center DiffSync models for Nautobot SSoT for Cisco DNA Center SSoT."""

from nautobot_ssot_dna_center.diffsync.models.base import Device


class DnaCenterDevice(Device):
    """DNA Center implementation of Device DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Device in DNA Center from NautobotSsotDnaCenterDevice object."""
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Device in DNA Center from NautobotSsotDnaCenterDevice object."""
        return super().update(attrs)

    def delete(self):
        """Delete Device in DNA Center from NautobotSsotDnaCenterDevice object."""
        return self
