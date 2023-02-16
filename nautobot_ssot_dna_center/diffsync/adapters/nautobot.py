"""Nautobot Adapter for DNA Center SSoT plugin."""

from diffsync import DiffSync
from diffsync.exceptions import ObjectNotFound
from nautobot.dcim.models import Device as OrmDevice
from nautobot.dcim.models import Location as OrmLocation
from nautobot.dcim.models import LocationType as OrmLocationType
from nautobot.dcim.models import Region as OrmRegion
from nautobot.dcim.models import Site as OrmSite
from nautobot_ssot_dna_center.diffsync.models.nautobot import (
    NautobotArea,
    NautobotBuilding,
    NautobotFloor,
    NautobotDevice,
)


class NautobotAdapter(DiffSync):
    """DiffSync adapter for Nautobot."""

    area = NautobotArea
    building = NautobotBuilding
    floor = NautobotFloor
    device = NautobotDevice

    top_level = ["area", "device"]

    def __init__(self, *args, job=None, sync=None, **kwargs):
        """Initialize Nautobot.

        Args:
            job (object, optional): Nautobot job. Defaults to None.
            sync (object, optional): Nautobot DiffSync. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync

    def load_regions(self):
        """Load Region data from Nautobt into DiffSync models."""
        for region in OrmRegion.objects.all():
            try:
                self.get(self.area, region.name)
                self.job.log_warning(message=f"Region {region.name} already loaded so skipping duplicate.")
            except ObjectNotFound:
                new_region = self.area(
                    name=region.name,
                    parent=region.parent.name if region.parent else "",
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
                    latitude=site.latitude,
                    longitude=site.longitude,
                    uuid=site.id,
                )
                self.add(new_building)
                try:
                    area = self.get(self.area, site.region.name)
                    area.add_child(new_building)
                except ObjectNotFound as err:
                    self.job.log_warning(message=f"Unable to load area {site.region.name} for {site.name}. {err}")

    def load_floors(self):
        """Load LocationType floors from Nautobot into DiffSync models."""
        try:
            loc_type = OrmLocationType.objects.get(name="Floor")
            if loc_type:
                locations = OrmLocation.objects.get(location_type=loc_type)
                for location in locations:
                    new_floor = self.floor(
                        name=location.name,
                        building=location.site.name,
                        uuid=location.id,
                    )
                    self.add(new_floor)
                    try:
                        building = self.get(
                            self.building, {"name": location.site.name, "area": location.site.region.name}
                        )
                        building.add_child(new_floor)
                    except ObjectNotFound as err:
                        self.job.log_warning(
                            message=f"Unable to load building {location.site.name} for floor {location.name}. {err}"
                        )
        except ObjectNotFound as err:
            self.job.log_warning(
                message=f"Unable to find LocationType: Floor so can't find floor Locations to load. {err}"
            )

    def load_devices(self):
        """Load Device data from Nautobot into DiffSync models."""
        for dev in OrmDevice.objects.all():
            new_dev = self.device(
                name=dev.name,
                status=dev.status.slug,
                role=dev.devicerole.name,
                vendor=dev.devicetype.manufacturer.name,
                model=dev.devicetype.model,
                area=dev.region.name if dev.region else "",
                site=dev.site.name,
                floor=dev.location.name if dev.location else "",
                serial=dev.serial,
                version=dev._custom_field_data["os_version"] if dev._custom_field_data.get("os_version") else "unknown",
                platform=dev.platform.slug,
                uuid=dev.id,
            )
            self.add(new_dev)

    def load(self):
        """Load data from Nautobot into DiffSync models."""
        self.load_regions()
        self.load_sites()
        self.load_floors()
        self.load_devices()
