"""Nautobot Adapter for DNA Center SSoT plugin."""
try:
    from nautobot_device_lifecycle_mgmt.models import SoftwareLCM  # noqa: F401

    LIFECYCLE_MGMT = True
except ImportError:
    LIFECYCLE_MGMT = False

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
from nautobot.extras.models import Relationship as OrmRelationship
from nautobot.extras.models import RelationshipAssociation as OrmRelationshipAssociation
from nautobot.ipam.models import IPAddress as OrmIPAddress

from nautobot_ssot_dna_center.diffsync.models.nautobot import (
    NautobotArea,
    NautobotBuilding,
    NautobotDevice,
    NautobotFloor,
    NautobotIPAddress,
    NautobotPort,
)


class NautobotAdapter(DiffSync):
    """DiffSync adapter for Nautobot."""

    area = NautobotArea
    building = NautobotBuilding
    floor = NautobotFloor
    device = NautobotDevice
    port = NautobotPort
    ipaddress = NautobotIPAddress

    top_level = ["area", "building", "device", "ipaddress"]

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
                self.get(self.building, {"name": site.name, "area": site.region.name if site.region else None})
            except ObjectNotFound:
                new_building = self.building(
                    name=site.name,
                    address=site.physical_address,
                    area=site.region.name if site.region else "",
                    latitude=str(site.latitude).rstrip("0"),
                    longitude=str(site.longitude).rstrip("0"),
                    tenant=site.tenant.name if site.tenant else None,
                    uuid=site.id,
                )
                self.add(new_building)

    def load_floors(self):
        """Load LocationType floors from Nautobot into DiffSync models."""
        try:
            loc_type = OrmLocationType.objects.get(name="Floor")
            locations = OrmLocation.objects.filter(
                _custom_field_data__system_of_record="DNA Center", location_type=loc_type
            )
            for location in locations:
                new_floor = self.floor(
                    name=location.name,
                    building=location.site.name if location.site else "",
                    tenant=location.tenant.name if location.tenant else None,
                    uuid=location.id,
                )
                self.add(new_floor)
                try:
                    if location.site:
                        building = self.get(self.building, location.site.name)
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
        for dev in OrmDevice.objects.filter(_custom_field_data__system_of_record="DNA Center"):
            version = dev.custom_field_data.get("os_version")
            if LIFECYCLE_MGMT:
                try:
                    soft_lcm = OrmRelationship.objects.get(slug="device_soft")
                    version = OrmRelationshipAssociation.objects.get(
                        relationship=soft_lcm, destination_id=dev.id
                    ).source.version
                except OrmRelationshipAssociation.DoesNotExist:
                    pass
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
                version=version,
                platform=dev.platform.slug if dev.platform else "",
                tenant=dev.tenant.name if dev.tenant else None,
                management_addr=dev.primary_ip.host if dev.primary_ip else "",
                uuid=dev.id,
            )
            self.add(new_dev)

    def load_ports(self):
        """Load Interface data from Nautobot into DiffSync models."""
        for port in OrmInterface.objects.filter(_custom_field_data__system_of_record="DNA Center"):
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
            device = self.get(
                self.device,
                {
                    "name": port.device.name,
                    "site": port.device.site.name,
                    "serial": port.device.serial,
                    "management_addr": port.device.primary_ip.host if port.device.primary_ip else "",
                },
            )
            device.add_child(new_port)

    def load_ipaddresses(self):
        """Load IPAddress data from Nautobot into DiffSync models."""
        for ipaddr in OrmIPAddress.objects.filter(_custom_field_data__system_of_record="DNA Center"):
            new_ipaddr = self.ipaddress(
                address=str(ipaddr.address),
                interface=ipaddr.assigned_object.name,
                device=ipaddr.assigned_object.device.name if ipaddr.assigned_object.device else "",
                primary=hasattr(ipaddr, "primary_ip4_for") or hasattr(ipaddr, "primary_ip6_for"),
                tenant=ipaddr.tenant.name if ipaddr.tenant else None,
                uuid=ipaddr.id,
            )
            self.add(new_ipaddr)

    def sync_complete(self, source: DiffSync, *args, **kwargs):
        """Label and clean up function for DiffSync sync.

        Once the sync is complete, this function labels all imported objects and then
        deletes any objects from Nautobot that need to be deleted in a specific order.

        Args:
            source (DiffSync): DiffSync
        """
        self.job.log_info(message="Sync is complete. Labelling imported objects from DNA Center.")
        source.label_imported_objects(target=self)

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
