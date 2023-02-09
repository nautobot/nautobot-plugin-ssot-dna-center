"""Nautobot DiffSync models for DNA Center SSoT."""

from nautobot.dcim.models import Device, DeviceRole, Site
from nautobot.extras.models import Status
from nautobot_ssot_dna_center.diffsync.models import base


class NautobotSite(base.Site):
    """Nautobot implementation of Site DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Site in Nautobot from Site object."""
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Site in Nautobot from Site object."""
        return super().update(attrs)

    def delete(self):
        """Delete Site in Nautobot from Site object."""
        return self


class NautobotDevice(base.Device):
    """Nautobot implementation of DNA Center Device model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Device in Nautobot from NautobotDevice object."""
        new_device = Device(
            name=ids["name"],
            status=Status.objects.get_or_create(name=attrs["status"]),
            role=DeviceRole.objects.get_or_create(name=attrs["role"]),
            site=Site.objects.get_or_create(name=attrs["site"]),
        )
        new_device.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Device in Nautobot from NautobotDevice object."""
        device = Device.objects.get(id=attrs["uuid"])
        if "status" in attrs:
            device.status = Status.objects.get_or_create(name=attrs["status"])
        if "role" in attrs:
            device.role = DeviceRole.objects.get_or_create(name=attrs["role"])
        if "site" in attrs:
            device.site = Site.objects.get_or_create(name=attrs["site"])
        device.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Device in Nautobot from NautobotDevice object."""
        dev = Device.objects.get(id=self.uuid)
        super().delete()
        dev.delete()
        return self
