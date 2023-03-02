"""Nautobot Adapter for DNA Center SSoT plugin."""

from collections import defaultdict
from diffsync import DiffSync
from diffsync.exceptions import ObjectNotFound
from django.db.models import ProtectedError
from nautobot.dcim.models import Device as OrmDevice
from nautobot.dcim.models import Interface as OrmInterface
from nautobot.dcim.models import Location as OrmLocation
from nautobot.dcim.models import LocationType as OrmLocationType
from nautobot.dcim.models import Region as OrmRegion
from nautobot.dcim.models import Site as OrmSite
from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot_ssot_dna_center.diffsync.models.nautobot import (
    NautobotArea,
    NautobotBuilding,
    NautobotFloor,
    NautobotDevice,
    NautobotPort,
    NautobotIPAddress,
)


class NautobotAdapter(DiffSync):
    """DiffSync adapter for Nautobot."""

    area = NautobotArea
    building = NautobotBuilding
    floor = NautobotFloor
    device = NautobotDevice
    port = NautobotPort
    ipaddress = NautobotIPAddress

    top_level = ["area", "device", "ipaddress"]

    def __init__(self, *args, job=None, sync=None, **kwargs):
        """Initialize Nautobot.

        Args:
            job (object, optional): Nautobot job. Defaults to None.
            sync (object, optional): Nautobot DiffSync. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync
        self.objects_to_delete = defaultdict(list)

    def load_regions(self):
        """Load Region data from Nautobt into DiffSync models."""
        for region in OrmRegion.objects.all():
            try:
                self.get(self.area, {"name": region.name, "parent": region.parent.name if region.parent else None})
                self.job.log_warning(message=f"Region {region.name} already loaded so skipping duplicate.")
            except ObjectNotFound:
                new_region = self.area(
                    name=region.name,
                    parent=region.parent.name if region.parent else None,
                    uuid=region.id,
                )
                self.add(new_region)

    def load_sites(self):
        """Load Site data from Nautobot into DiffSync models."""
        for site in OrmSite.objects.all():
            try:
                self.get(self.building, {"name": site.name, "area": site.region.name})
            except ObjectNotFound:
                new_building = self.building(
                    name=site.name,
                    address=site.physical_address,
                    area=site.region.name if site.region else "",
                    latitude=str(site.latitude).rstrip("0"),
                    longitude=str(site.longitude).rstrip("0"),
                    uuid=site.id,
                )
                self.add(new_building)
                try:
                    area = self.get(
                        self.area,
                        {"name": site.region.name, "parent": site.region.parent.name if site.region.parent else None},
                    )
                    area.add_child(new_building)
                except ObjectNotFound as err:
                    self.job.log_warning(message=f"Unable to load area {site.region.name} for {site.name}. {err}")

    def load_floors(self):
        """Load LocationType floors from Nautobot into DiffSync models."""
        try:
            loc_type = OrmLocationType.objects.get(name="Floor")
            locations = OrmLocation.objects.filter(location_type=loc_type)
            for location in locations:
                new_floor = self.floor(
                    name=location.name,
                    building=location.site.name if location.site else "",
                    uuid=location.id,
                )
                self.add(new_floor)
                try:
                    if location.site:
                        building = self.get(
                            self.building, {"name": location.site.name, "area": location.site.region.name}
                        )
                        building.add_child(new_floor)
                except ObjectNotFound as err:
                    self.job.log_warning(
                        message=f"Unable to load building {location.site.name} for floor {location.name}. {err}"
                    )
        except OrmLocationType.DoesNotExist as err:
            self.job.log_warning(
                message=f"Unable to find LocationType: Floor so can't find floor Locations to load. {err}"
            )

    def load_devices(self):
        """Load Device data from Nautobot into DiffSync models."""
        for dev in OrmDevice.objects.all():
            new_dev = self.device(
                name=dev.name,
                status=dev.status.name,
                role=dev.device_role.name,
                vendor=dev.device_type.manufacturer.name,
                model=dev.device_type.model,
                area=dev.site.region.name if dev.site.region else "",
                site=dev.site.name,
                floor=dev.location.name if dev.location else "",
                serial=dev.serial,
                version=dev._custom_field_data["OS Version"] if dev._custom_field_data.get("OS Version") else "unknown",
                platform=dev.platform.slug if dev.platform else "",
                management_addr=dev.primary_ip.host if dev.primary_ip else "",
                uuid=dev.id,
            )
            self.add(new_dev)

    def load_ports(self):
        """Load Interface data from Nautobot into DiffSync models."""
        for port in OrmInterface.objects.all():
            new_port = self.port(
                name=port.name,
                device=port.device.name,
                description=port.description,
                enabled=port.enabled,
                port_type=port.type,
                port_mode=port.mode,
                mac_addr=str(port.mac_address) if getattr(port, "mac_address") else None,
                mtu=port.mtu if port.mtu else 1500,
                status=port.status.slug,
                uuid=port.id,
            )
            self.add(new_port)
            device = self.get(self.device, port.device.name)
            device.add_child(new_port)

    def load_ipaddresses(self):
        """Load IPAddress data from Nautobot into DiffSync models."""
        for ipaddr in OrmIPAddress.objects.all():
            new_ipaddr = self.ipaddress(
                address=str(ipaddr.address),
                interface=ipaddr.assigned_object.name,
                device=ipaddr.assigned_object.device.name if ipaddr.assigned_object.device else "",
                primary=hasattr(ipaddr, "primary_ip4_for") or hasattr(ipaddr, "primary_ip6_for"),
                uuid=ipaddr.id,
            )
            self.add(new_ipaddr)

    def sync_complete(self, source: DiffSync, *args, **kwargs):
        """Clean up function for DiffSync sync.

        Once the sync is complete, this function runs deleting any objects
        from Nautobot that need to be deleted in a specific order.

        Args:
            source (DiffSync): DiffSync
        """
        for grouping in ["floors", "sites", "regions"]:
            for nautobot_obj in self.objects_to_delete[grouping]:
                try:
                    self.job.log_info(message=f"Deleting {nautobot_obj}.")
                    nautobot_obj.delete()
                except ProtectedError:
                    self.job.log_info(message=f"Deletion failed protected object: {nautobot_obj}")
            self.objects_to_delete[grouping] = []
        return super().sync_complete(source, *args, **kwargs)

    def load(self):
        """Load data from Nautobot into DiffSync models."""
        self.load_regions()
        self.load_sites()
        self.load_floors()
        self.load_devices()
        self.load_ports()
        self.load_ipaddresses()
