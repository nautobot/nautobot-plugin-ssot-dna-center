"""Nautobot DiffSync models for DNA Center SSoT."""

from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Manufacturer,
    Platform,
    Site,
    Rack,
    RackGroup,
    Region,
    Location,
    LocationType,
)
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField, Status
from nautobot_ssot_dna_center.diffsync.models import base


class NautobotArea(base.Area):
    """Nautobot implementation of Area DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Region in Nautobot from Area object."""
        new_region = Region(
            name=ids["name"],
        )
        if ids.get("parent"):
            try:
                new_region.parent = Region.objects.get(name=ids["parent"])
            except Region.DoesNotExist as err:
                diffsync.log_warning(message=f"Unable to find Region {ids['parent']} for {ids['name']}. {err}")
        new_region.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def delete(self):
        """Delete Region in Nautobot from Area object."""
        region = Region.objects.get(id=self.uuid)
        self.diffsync.objects_to_delete["regions"].append(region)
        return self


class NautobotBuilding(base.Building):
    """Nautobot implementation of Building DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Site in Nautobot from Building object."""
        new_site = Site(
            name=ids["name"],
            physical_address=attrs["address"] if attrs.get("address") else "",
            status=Status.objects.get(name="Active"),
            latitude=attrs["latitude"],
            longitude=attrs["longitude"],
        )
        try:
            if ids.get("area"):
                new_site.region = Region.objects.get(name=ids["area"])
        except Region.DoesNotExist:
            diffsync.job.log_info(message=f"Unable to find parent {ids['area']}")
        new_site.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Site in Nautobot from Building object."""
        site = Site.objects.get(id=self.uuid)
        if "address" in attrs:
            site.physical_address = attrs["address"]
        if "latitude" in attrs:
            site.latitude = attrs["latitude"]
        if "longitude" in attrs:
            site.longitude = attrs["longitude"]
        site.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Site in Nautobot from Building object."""
        site = Site.objects.get(id=self.uuid)
        self.diffsync.objects_to_delete["sites"].append(site)
        return self


class NautobotFloor(base.Floor):
    """Nautobot implementation of Floor DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create LocationType: Floor in Nautobot from Floor object."""
        loc_type, created = LocationType.objects.get_or_create(
            name="Floor",
            nestable=False,
        )
        if created:
            loc_type.content_types.add(ContentType.objects.get_for_model(Device))
            loc_type.content_types.add(ContentType.objects.get_for_model(Rack))
            loc_type.content_types.add(ContentType.objects.get_for_model(RackGroup))
        new_floor = Location(
            name=ids["name"],
            status=Status.objects.get(name="Active"),
            site=Site.objects.get(name=ids["building"]),
            location_type=loc_type,
        )
        new_floor.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def delete(self):
        """Delete LocationType: Floor in Nautobot from Floor object."""
        floor = Location.objects.get(id=self.uuid)
        self.diffsync.objects_to_delete["floors"].append(floor)
        return self


class NautobotDevice(base.Device):
    """Nautobot implementation of DNA Center Device model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Device in Nautobot from NautobotDevice object."""
        site = Site.objects.get(name=attrs["site"])
        manufacturer, _ = Manufacturer.objects.get_or_create(name=attrs["vendor"])
        device_role, _ = DeviceRole.objects.get_or_create(name=attrs["role"])
        device_type, _ = DeviceType.objects.get_or_create(model=attrs["model"], manufacturer=manufacturer)
        platform, _ = Platform.objects.get_or_create(name=attrs["platform"])
        status = Status.objects.get(name=attrs["status"])
        new_device = Device(
            name=ids["name"],
            status=status,
            device_role=device_role,
            site=site,
            device_type=device_type,
            serial=attrs["serial"],
            platform=platform,
        )
        if attrs.get("floor"):
            loc_type = LocationType.objects.get(name="Floor")
            new_device.location = Location.objects.get_or_create(name=f"{site} - {ids['name']}", location_type=loc_type)
        if attrs.get("version"):
            _cf_dict = {
                "name": "OS Version",
                "slug": "os_version",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "OS Version",
            }
            field, _ = CustomField.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(Device))
            new_device.custom_field_data.update({"OS Version": attrs["version"]})
        new_device.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Device in Nautobot from NautobotDevice object."""
        device = Device.objects.get(id=self.uuid)
        self.diffsync.job.log_info(message=f"Updating device {device.name} with {attrs}")
        if "status" in attrs:
            device.status = Status.objects.get(name=attrs["status"])
        if "role" in attrs:
            device.device_role = DeviceRole.objects.get_or_create(name=attrs["role"])
        if "site" in attrs:
            device.site = Site.objects.get(name=attrs["site"])
        if "floor" in attrs:
            loc_type = LocationType.objects.get(name="Floor")
            if attrs.get("site"):
                site = attrs["site"]
            else:
                site = device.site.name
            location, _ = Location.objects.get_or_create(
                name=f"{site} - {attrs['floor']}", location_type=loc_type, site=Site.objects.get(name=site)
            )
            device.location = location
        if "model" in attrs:
            device.device_type = DeviceType.objects.get_or_create(model=attrs["model"])
        if "serial" in attrs:
            device.serial = attrs["serial"]
        if "platform" in attrs:
            device.platform = Platform.objects.get_or_create(name=attrs["platform"])
        if "version" in attrs:
            _cf_dict = {
                "name": "OS Version",
                "slug": "os_version",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "OS Version",
            }
            field, _ = CustomField.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(Device))
            device.custom_field_data.update({"OS Version": attrs["version"]})
        device.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Device in Nautobot from NautobotDevice object."""
        dev = Device.objects.get(id=self.uuid)
        super().delete()
        dev.delete()
        return self


class NautobotPort(base.Port):
    """Nautobot implementation of Port DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Interface in Nautobot from Port object."""
        new_port = Interface(
            name=ids["name"],
            device=Device.objects.get(name=ids["device"]),
            description=attrs["description"],
            enabled=attrs["enabled"],
            type=attrs["port_type"],
            mode=attrs["port_mode"],
            mac_address=attrs["mac_addr"],
            mtu=attrs["mtu"],
            status=Status.objects.get(slug=attrs["status"]),
            mgmt_only=True if "Management" in ids["name"] else False,
        )
        new_port.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Interface in Nautobot from Port object."""
        port = Interface.objects.get(id=self.uuid)
        if "description" in attrs:
            port.description = attrs["description"]
        if "port_type" in attrs:
            port.type = attrs["port_type"]
        if "port_mode" in attrs:
            port.mode = attrs["port_mode"]
        if "mac_addr" in attrs:
            port.mac_address = attrs["mac_addr"]
        if "mtu" in attrs:
            port.mtu = attrs["mtu"]
        if "status" in attrs:
            port.status = Status.objects.get(slug=attrs["status"])
        if "enabled" in attrs:
            port.enabled = attrs["enabled"]
        port.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Interface in Nautobot from Port object."""
        port = Interface.objects.get(id=self.uuid)
        super().delete()
        port.delete()
        return self
