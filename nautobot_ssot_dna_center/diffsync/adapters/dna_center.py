"""Nautobot SSoT for Cisco DNA Center Adapter for DNA Center SSoT plugin."""
from datetime import datetime
from typing import List

from diffsync import DiffSync
from diffsync.exceptions import ObjectNotFound
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models import Device, Interface, Location, LocationType, Region, Site
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField
from nautobot.ipam.models import IPAddress
from nautobot.tenancy.models import Tenant
from netutils.ip import netmask_to_cidr

from nautobot_ssot_dna_center.constants import DNAC_PLATFORM_MAPPER
from nautobot_ssot_dna_center.diffsync.models.dna_center import (
    DnaCenterArea,
    DnaCenterBuilding,
    DnaCenterDevice,
    DnaCenterFloor,
    DnaCenterIPAddress,
    DnaCenterPort,
)
from nautobot_ssot_dna_center.utils.dna_center import DnaCenterClient


class LabelMixin:
    """Add labels onto Nautobot objects to provide information on sync status with DNA Center."""

    def label_imported_objects(self, target):
        """Add CustomFields to all objects that were successfully synced to the target."""
        # Ensure that the "ssot-last-synchronized" custom field is present; as above, it *should* already exist.
        cf_dict = {
            "type": CustomFieldTypeChoices.TYPE_DATE,
            "name": "ssot_last_synchronized",
            "slug": "ssot_last_synchronized",
            "label": "Last sync from DNA Center",
        }
        custom_field, _ = CustomField.objects.get_or_create(name=cf_dict["name"], defaults=cf_dict)
        for model in [Region, Site, Location, Device, Interface, IPAddress]:
            custom_field.content_types.add(ContentType.objects.get_for_model(model))

        for modelname in ["area", "building", "floor", "device", "port", "ipaddress"]:
            for local_instance in self.get_all(modelname):
                unique_id = local_instance.get_unique_id()
                # Verify that the object now has a counterpart in the target DiffSync
                try:
                    target.get(modelname, unique_id)
                except ObjectNotFound:
                    continue

                self.label_object(modelname, unique_id, custom_field)

    def label_object(self, modelname, unique_id, custom_field):
        """Apply the given CustomField to the identified object."""
        model_instance = self.get(modelname, unique_id)
        today = datetime.now().today()

        def _label_object(nautobot_object):
            """Apply custom field to object, if applicable."""
            nautobot_object.custom_field_data[custom_field.name] = today
            nautobot_object.custom_field_data["system_of_record"] = "DNA Center"
            nautobot_object.validated_save()

        if modelname == "area":
            _label_object(Region.objects.get(name=model_instance.name))
        elif modelname == "building":
            _label_object(Site.objects.get(name=model_instance.name))
        elif modelname == "floor":
            _label_object(
                Location.objects.get(name=model_instance.name, location_type=LocationType.objects.get(name="Floor"))
            )
        elif modelname == "device":
            _label_object(Device.objects.get(name=model_instance.name))
        elif modelname == "port":
            _label_object(Interface.objects.get(name=model_instance.name, device__name=model_instance.device))
        elif modelname == "ipaddress":
            _label_object(IPAddress.objects.get(address=model_instance.address))


class DnaCenterAdapter(LabelMixin, DiffSync):
    """DiffSync adapter for DNA Center."""

    area = DnaCenterArea
    building = DnaCenterBuilding
    floor = DnaCenterFloor
    device = DnaCenterDevice
    port = DnaCenterPort
    ipaddress = DnaCenterIPAddress

    top_level = ["area", "device", "ipaddress"]

    def __init__(self, *args, job=None, sync=None, client: DnaCenterClient, tenant: Tenant, **kwargs):
        """Initialize DNA Center.

        Args:
            job (object, optional): DNA Center job. Defaults to None.
            sync (object, optional): DNA Center DiffSync. Defaults to None.
            client (DnaCenterClient): DNA Center API client connection object.
            tenant (Tenant): Tenant to attach to imported objects. Can be set to None for no Tenant to be attached.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync
        self.conn = client
        self.dnac_location_map = {}
        self.tenant = tenant

    def load_locations(self):
        """Load location data from DNA Center into DiffSync models."""
        locations = self.conn.get_locations()
        if locations:
            # to ensure we process locations in the appropriate order we need to split them into their own list of locations
            self.dnac_location_map = self.build_dnac_location_map(locations)
            areas, buildings, floors = self.parse_and_sort_locations(locations)
            self.load_areas(areas)
            self.load_buildings(buildings)
            self.load_floors(floors)

    def load_areas(self, areas: List[dict]):
        """Load areas from DNAC into DiffSync model.

        Args:
            areas (List[dict]): List of dictionaries containing location information about a building.
        """
        for location in areas:
            if self.job.kwargs.get("debug"):
                self.job.log_info(message=f"Loading area {location['name']}. {location}")
            if location.get("parentId"):
                self.dnac_location_map[location["id"]]["parent"] = self.dnac_location_map[location["parentId"]]["name"]
            new_area = self.area(
                name=location["name"],
                parent=self.dnac_location_map[location["parentId"]]["name"] if location.get("parentId") else None,
                uuid=None,
            )
            try:
                self.add(new_area)
            except ValidationError as err:
                self.job.log_warning(message=f"Unable to load area {location['name']}. {err}")

    def load_buildings(self, buildings: List[dict]):
        """Load building data from DNAC into DiffSync model.

        Args:
            buildings (List[dict]): List of dictionaries containing location information about a building.
        """
        for location in buildings:
            if self.job.kwargs.get("debug"):
                self.job.log_info(message=f"Loading building {location['name']}. {location}")
            address, _ = self.conn.find_address_and_type(info=location["additionalInfo"])
            latitude, longitude = self.conn.find_latitude_and_longitude(info=location["additionalInfo"])
            _area = (
                self.dnac_location_map[location["parentId"]]
                if location.get("parentId")
                else {"name": "Global", "parent": None}
            )
            new_building = self.building(
                name=location["name"],
                address=address,
                area=_area["name"],
                latitude=latitude[:9].rstrip("0"),
                longitude=longitude[:7].rstrip("0"),
                tenant=self.tenant.name if self.tenant else None,
                uuid=None,
            )
            try:
                self.add(new_building)
                try:
                    parent = self.get(self.area, {"name": _area["name"], "parent": _area["parent"]})
                    parent.add_child(new_building)
                except ObjectNotFound as err:
                    self.job.log_warning(
                        message=f"Unable to find area {_area['name']} for building {location['name']}. {err}"
                    )
            except ValidationError as err:
                self.job.log_warning(message=f"Unable to load building {location['name']}. {err}")

    def load_floors(self, floors: List[dict]):
        """Load floor data from DNAC into DiffSync model.

        Args:
            floors (List[dict]): List of dictionaries containing location information about a floor.
        """
        for location in floors:
            if self.job.kwargs.get("debug"):
                self.job.log_info(message=f"Loading floor {location['name']}. {location}")
            _building = self.dnac_location_map[location["parentId"]] if location.get("parentId") else {}
            new_floor = self.floor(
                name=f"{_building['name']} - {location['name']}",
                building=_building["name"],
                tenant=self.tenant.name if self.tenant else None,
                uuid=None,
            )
            try:
                self.add(new_floor)
                try:
                    parent = self.get(self.building, {"name": _building["name"], "area": _building["parent"]})
                    parent.add_child(new_floor)
                except ObjectNotFound as err:
                    self.job.log_warning(
                        message=f"Unable to find building {_building['name']} in area {_building['parent']} for floor {location['name']}. {err}"
                    )
            except ValidationError as err:
                self.job.log_warning(message=f"Unable to load floor {_building['name']} - {location['name']}. {err}")

    def parse_and_sort_locations(self, locations: list):
        """Separate locations into areas, buildings, and floors for processing. Also sort by siteHierarchy.

        Args:
            locations (list): List of Locations (Sites) from DNAC to be separated.

        Returns:
            tuple (List[dict], List[dict], List[dict]): Tuple containing lists of areas, buildings, and floors in DNAC to be processed.
        """
        areas, buildings, floors = [], [], []
        for location in locations:
            for info in location["additionalInfo"]:
                if info["attributes"].get("type") == "building":
                    buildings.append(location)
                    self.dnac_location_map[location["id"]]["loc_type"] = "building"
                    break
                elif info["attributes"].get("type") == "floor":
                    floors.append(location)
                    self.dnac_location_map[location["id"]]["loc_type"] = "floor"
                    break
            else:
                areas.append(location)
            if location.get("parentId"):
                self.dnac_location_map[location["id"]]["parent"] = self.dnac_location_map[location["parentId"]]["name"]
        # sort areas by length of siteHierarchy so that parent areas loaded before child areas.
        areas = sorted(areas, key=lambda x: len(x["siteHierarchy"].split("/")))
        return areas, buildings, floors

    def build_dnac_location_map(self, locations: list):
        """Build out the initial DNAC location map for Location ID to name and type.

        Args:
            locations (list): List of Locations (Sites) from DNAC.

        Returns:
            dict: Dictionary of Locations mapped with ID to their name and location type.
        """
        return {loc["id"]: {"name": loc["name"], "parent": None, "loc_type": "area"} for loc in locations}

    def load_devices(self):
        """Load Device data from DNA Center info DiffSync models."""
        devices = self.conn.get_devices()
        for dev in devices:
            platform = "unknown"
            vendor = "Cisco"
            if dev["softwareType"] in DNAC_PLATFORM_MAPPER:
                platform = DNAC_PLATFORM_MAPPER[dev["softwareType"]]
            else:
                if not dev.get("softwareType") and dev.get("family") and "Meraki" in dev["family"]:
                    platform = "meraki"
            if "Juniper" in dev["type"]:
                vendor = "Juniper"
            dev_details = self.conn.get_device_detail(dev_id=dev["id"])
            if dev_details and dev_details.get("siteHierarchyGraphId"):
                loc_data = self.conn.parse_site_hierarchy(
                    location_map=self.dnac_location_map, site_hier=dev_details["siteHierarchyGraphId"]
                )
            else:
                self.job.log_warning(message=f"Unable to find Site for {dev['hostname']} so skipping.")
                continue
            try:
                if self.job.kwargs.get("debug"):
                    self.job.log_info(
                        message=f"Loading device {dev['hostname'] if dev.get('hostname') else dev['id']}. {dev}"
                    )
                device_found = self.get(
                    self.device,
                    {
                        "name": dev["hostname"],
                        "site": loc_data["building"],
                        "serial": dev["serialNumber"],
                        "management_addr": dev["managementIpAddress"],
                    },
                )
                if device_found:
                    self.job.log_warning(
                        message=f"Duplicate device attempting to be loaded for {dev['hostname']} with ID: {dev['id']}"
                    )
                    continue
            except ObjectNotFound:
                new_dev = self.device(
                    name=dev["hostname"],
                    status="Active" if dev.get("reachabilityStatus") != "Unreachable" else "Offline",
                    role=dev["role"],
                    vendor=vendor,
                    model=dev["platformId"] if dev.get("platformId") else "Unknown",
                    area=loc_data["areas"][-1],
                    site=loc_data["building"],
                    floor=f"{loc_data['building']} - {loc_data['floor']}" if loc_data.get("floor") else "",
                    serial=dev.get("serialNumber"),
                    version=dev.get("softwareVersion"),
                    platform=platform,
                    tenant=self.tenant.name if self.tenant else None,
                    management_addr=dev["managementIpAddress"] if dev.get("managementIpAddress") else "",
                    uuid=None,
                )
                try:
                    self.add(new_dev)
                    self.load_ports(device_id=dev["id"], dev=new_dev)
                except ValidationError as err:
                    self.job.log_warning(message=f"Unable to load device {dev['hostname']}. {err}")

    def load_ports(self, device_id: str, dev: DnaCenterDevice):
        """Load port info from DNAC into Port DiffSyncModel.

        Args:
            device_id (str): ID for Device in DNAC to retrieve ports for.
            dev (DnaCenterDevice): Device associated with ports.
        """
        ports = self.conn.get_port_info(device_id=device_id)
        for port in ports:
            if self.job.kwargs.get("debug"):
                self.job.log_info(message=f"Loading port {port['portName']} for {dev.name}. {port}")
            port_type = self.conn.get_port_type(port_info=port)
            port_status = self.conn.get_port_status(port_info=port)
            new_port = self.port(
                name=port["portName"],
                device=dev.name if dev.name else "",
                description=port["description"],
                enabled=True if port["adminStatus"] == "UP" else False,
                port_type=port_type,
                port_mode="tagged" if port["portMode"] == "trunk" else "access",
                mac_addr=port["macAddress"].upper() if port.get("macAddress") else None,
                mtu=port["mtu"] if port.get("mtu") else 1500,
                status=port_status,
                uuid=None,
            )
            try:
                self.add(new_port)
                dev.add_child(new_port)

                if port.get("addresses"):
                    for addr in port["addresses"]:
                        if addr["address"]["ipAddress"]["address"] == dev.management_addr:
                            primary = True
                        else:
                            primary = False
                        self.load_ip_address(
                            device_name=dev.name if dev.name else "",
                            interface=port["portName"],
                            address=f"{addr['address']['ipAddress']['address']}/{netmask_to_cidr(addr['address']['ipMask']['address'])}",
                            primary=primary,
                        )
            except ValidationError as err:
                self.job.log_warning(message=f"Unable to load port {port['portName']} for {dev.name}. {err}")

    def load_ip_address(self, device_name: str, interface: str, address: str, primary: bool):
        """Load IP Address info from DNAC into IPAddress DiffSyncModel.

        Args:
            device_name (str): Name of Device that will own IP Address.
            interface (str): Name of Interface on Device that IP Address will reside on.
            address (str): IP Address to be loaded.
            primary (bool): Whether the IP Address is the primary IP for the Device.
        """
        try:
            self.get(self.ipaddress, {"address": address, "device": device_name, "interface": interface})
        except ObjectNotFound:
            if self.job.kwargs.get("debug"):
                self.job.log_info(message=f"Loading IP Address {address} for {device_name} on {interface}.")
            new_ip = self.ipaddress(
                address=address,
                device=device_name,
                interface=interface,
                primary=primary,
                tenant=self.tenant.name if self.tenant else None,
                uuid=None,
            )
            self.add(new_ip)

    def load(self):
        """Load data from DNA Center into DiffSync models."""
        self.load_locations()
        self.load_devices()
