"""Nautobot DiffSync models for DNA Center SSoT."""


from nautobot.dcim.models import Device, DeviceRole, Site, Region
from nautobot.extras.models import Status
from nautobot_ssot_dna_center.diffsync.models import base


class NautobotSite(base.Site):
    """Nautobot implementation of Site DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Site in Nautobot from Site object."""
        new_site = Site(
            name=ids["name"],
            physical_address=attrs["address"] if attrs.get("address") else "",
        )
        try:
            if attrs.get("parent"):
                new_site.region = Region.objects.get(name=attrs["parent"])
        except Region.DoesNotExist:
            diffsync.job.log_info(message=f"Unable to find parent {attrs['parent']}")
        new_site.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Site in Nautobot from Site object."""
        site = Site.objects.get(id=self.uuid)
        if "address" in attrs:
            site.physical_address = attrs["address"]
        site.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Site in Nautobot from Site object."""
        site = Site.objects.get(id=self.uuid)
        super().delete()
        site.delete()
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
