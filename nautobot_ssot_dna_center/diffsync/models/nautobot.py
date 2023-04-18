"""Nautobot DiffSync models for DNA Center SSoT."""

from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Manufacturer,
    Site,
    Rack,
    RackGroup,
    Region,
    Location,
    LocationType,
)
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField, Status
from nautobot.ipam.models import IPAddress
from nautobot.tenancy.models import Tenant
from nautobot_ssot_dna_center.diffsync.models import base
from nautobot_ssot_dna_center.utils.nautobot import add_software_lcm, assign_version_to_device, verify_platform

try:
    import nautobot_device_lifecycle_mgmt  # noqa: F401

    LIFECYCLE_MGMT = True
except ImportError:
    LIFECYCLE_MGMT = False


class NautobotArea(base.Area):
    """Nautobot implementation of Area DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Region in Nautobot from Area object."""
        diffsync.job.log_info(message=f"Creating Region {ids['name']}.")
        new_region = Region(
            name=ids["name"],
        )
        if ids.get("parent"):
            try:
                new_region.parent = Region.objects.get(name=ids["parent"])
            except Region.DoesNotExist as err:
                diffsync.job.log_warning(message=f"Unable to find Region {ids['parent']} for {ids['name']}. {err}")
        new_region.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def delete(self):
        """Delete Region in Nautobot from Area object."""
        region = Region.objects.get(id=self.uuid)
        self.diffsync.job.log_info(message=f"Deleting Region {region.name}.")
        self.diffsync.objects_to_delete["regions"].append(region)
        return self


class NautobotBuilding(base.Building):
    """Nautobot implementation of Building DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Site in Nautobot from Building object."""
        diffsync.job.log_info(message=f"Creating Site {ids['name']}.")
        new_site = Site(
            name=ids["name"],
            physical_address=attrs["address"] if attrs.get("address") else "",
            status=Status.objects.get(name="Active"),
            latitude=attrs["latitude"],
            longitude=attrs["longitude"],
        )
        if attrs.get("tenant"):
            new_site.tenant = Tenant.objects.get(name=attrs["tenant"])
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
        self.diffsync.job.log_info(message=f"Updating Site {site.name}.")
        if "address" in attrs:
            site.physical_address = attrs["address"]
        if "latitude" in attrs:
            site.latitude = attrs["latitude"]
        if "longitude" in attrs:
            site.longitude = attrs["longitude"]
        if "tenant" in attrs:
            if attrs.get("tenant"):
                site.tenant = Tenant.objects.get(name=attrs["tenant"])
            else:
                site.tenant = None
        site.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Site in Nautobot from Building object."""
        site = Site.objects.get(id=self.uuid)
        self.diffsync.job.log_info(message=f"Deleting Site {site.name}.")
        self.diffsync.objects_to_delete["sites"].append(site)
        return self


class NautobotFloor(base.Floor):
    """Nautobot implementation of Floor DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create LocationType: Floor in Nautobot from Floor object."""
        diffsync.job.log_info(message=f"Creating Floor {ids['name']}.")
        loc_type, created = LocationType.objects.get_or_create(
            name="Floor",
            nestable=False,
        )
        if created:
            loc_type.content_types.add(ContentType.objects.get_for_model(Device))
            loc_type.content_types.add(ContentType.objects.get_for_model(Rack))
            loc_type.content_types.add(ContentType.objects.get_for_model(RackGroup))
        loc_type.validated_save()
        new_floor = Location(
            name=ids["name"],
            status=Status.objects.get(name="Active"),
            site=Site.objects.get(name=ids["building"]),
            location_type=loc_type,
        )
        if attrs.get("tenant"):
            new_floor.tenant = Tenant.objects.get(name=attrs["tenant"])
        new_floor.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update LocationType: Floor in Nautobot from Floor object."""
        floor = Location.objects.get(name=self.name, location_type=LocationType.objects.get(name="Floor"))
        self.diffsync.job.log_info(message=f"Updating Floor {floor.name} with {attrs}")
        if "tenant" in attrs:
            if attrs.get("tenant"):
                floor.tenant = Tenant.objects.get(name=attrs["tenant"])
            else:
                floor.tenant = None
        floor.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete LocationType: Floor in Nautobot from Floor object."""
        floor = Location.objects.get(id=self.uuid)
        self.diffsync.job.log_info(message=f"Deleting Floor {floor.name} in {floor.site.name}.")
        self.diffsync.objects_to_delete["floors"].append(floor)
        return self


class NautobotDevice(base.Device):
    """Nautobot implementation of DNA Center Device model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Device in Nautobot from NautobotDevice object."""
        diffsync.job.log_info(message=f"Creating Device {ids['name']}.")
        site = Site.objects.get(name=ids["site"])
        manufacturer, _ = Manufacturer.objects.get_or_create(name=attrs["vendor"])
        device_role, _ = DeviceRole.objects.get_or_create(name=attrs["role"])
        device_type, _ = DeviceType.objects.get_or_create(model=attrs["model"], manufacturer=manufacturer)
        platform = verify_platform(platform_name=attrs["platform"], manu=manufacturer.id)
        status = Status.objects.get(name=attrs["status"])
        new_device = Device(
            name=ids["name"],
            status=status,
            device_role=device_role,
            site=site,
            device_type=device_type,
            serial=ids["serial"],
            platform_id=platform.id,
        )
        if attrs.get("floor"):
            loc_type = LocationType.objects.get(name="Floor")
            loc, _ = Location.objects.get_or_create(
                name=attrs["floor"], location_type=loc_type, site=site, status=Status.objects.get(name="Active")
            )
            new_device.location = loc
        if attrs.get("tenant"):
            new_device.tenant = Tenant.objects.get(name=attrs["tenant"])
        if attrs.get("version"):
            _cf_dict = {
                "name": "os_version",
                "slug": "os_version",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "OS Version",
            }
            field, _ = CustomField.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(Device))
            new_device.custom_field_data.update({"os_version": attrs["version"]})
            if LIFECYCLE_MGMT:
                lcm_obj = add_software_lcm(diffsync=diffsync, platform=platform.slug, version=attrs["version"])
                assign_version_to_device(diffsync=diffsync, device=new_device, software_lcm=lcm_obj)
        new_device.validated_save()
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update Device in Nautobot from NautobotDevice object."""
        device = Device.objects.get(id=self.uuid)
        self.diffsync.job.log_info(message=f"Updating Device {device.name} with {attrs}")
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
                name=attrs["floor"],
                location_type=loc_type,
                site=Site.objects.get(name=site),
                status=Status.objects.get(name="Active"),
            )
            device.location = location
        if "model" in attrs:
            device.device_type = DeviceType.objects.get_or_create(model=attrs["model"])
        if "serial" in attrs:
            device.serial = attrs["serial"]
        if "platform" in attrs:
            vendor = attrs["vendor"] if attrs.get("vendor") else self.vendor
            manufacturer = Manufacturer.objects.get(name=vendor)
            device.platform = verify_platform(platform_name=attrs["platform"], manu=manufacturer.id)
        if "tenant" in attrs:
            if attrs.get("tenant"):
                device.tenant = Tenant.objects.get(name=attrs["tenant"])
            else:
                device.tenant = None
        if "version" in attrs:
            _cf_dict = {
                "name": "os_version",
                "slug": "os_version",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "OS Version",
            }
            field, _ = CustomField.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(Device))
            device.custom_field_data.update({"os_version": attrs["version"]})
        if LIFECYCLE_MGMT:
            platform_slug = attrs["platform"] if attrs.get("platform") else self.platform
            lcm_obj = add_software_lcm(diffsync=self.diffsync, platform=platform_slug, version=attrs["version"])
            assign_version_to_device(diffsync=self.diffsync, device=device, software_lcm=lcm_obj)
        device.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Device in Nautobot from NautobotDevice object."""
        dev = Device.objects.get(id=self.uuid)
        self.diffsync.job.log_info(message=f"Deleting Device: {dev.name}.")
        super().delete()
        dev.delete()
        return self


class NautobotPort(base.Port):
    """Nautobot implementation of Port DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Interface in Nautobot from Port object."""
        diffsync.job.log_info(message=f"Creating Port {ids['name']} for Device {ids['device']}.")
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
        self.diffsync.job.log_info(message=f"Updating Port {port.name} for Device {port.device.name}.")
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
        self.diffsync.job.log_info(message=f"Deleting Interface {port.name} for {port.device.name}.")
        super().delete()
        port.delete()
        return self


class NautobotIPAddress(base.IPAddress):
    """Nautobot implementation of the IPAddress DiffSync model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create IPAddress in Nautobot from IPAddress object."""
        try:
            device = Device.objects.get(name=ids["device"])
            intf = Interface.objects.get(name=ids["interface"], device=device)
            new_ip = IPAddress(
                address=ids["address"],
                assigned_object_type=ContentType.objects.get_for_model(Interface),
                assigned_object_id=intf.id,
                status=Status.objects.get(name="Active"),
            )
            if attrs.get("tenant"):
                new_ip.tenant = Tenant.objects.get(name=attrs["tenant"])
            new_ip.validated_save()
            if attrs.get("primary"):
                if ":" in ids["address"]:
                    device.primary_ip6 = new_ip
                else:
                    device.primary_ip4 = new_ip
                device.validated_save()
        except Device.DoesNotExist as err:
            diffsync.job.log_warning(
                message=f"Unable to find Device {ids['device']} for IPAddress {ids['address']}. {err}"
            )
            return None
        return super().create(diffsync=diffsync, ids=ids, attrs=attrs)

    def update(self, attrs):
        """Update IPAddress in Nautobot from IPAddress object."""
        ipaddr = IPAddress.objects.get(id=self.uuid)
        if attrs.get("primary"):
            device = ipaddr.assigned_object.device
            if ":" in self.address:
                device.primary_ip6 = ipaddr
            else:
                device.primary_ip4 = ipaddr
            device.validated_save()
        if "tenant" in attrs:
            if attrs.get("tenant"):
                ipaddr.tenant = Tenant.objects.get(name=attrs["tenant"])
            else:
                ipaddr.tenant = None
        ipaddr.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete IPAddress in Nautobot from IPAddress object."""
        ipaddr = IPAddress.objects.get(id=self.uuid)
        super().delete()
        ipaddr.delete()
        return self
