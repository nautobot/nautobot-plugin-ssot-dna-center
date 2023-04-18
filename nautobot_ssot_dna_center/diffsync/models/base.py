"""DiffSyncModel subclasses for Nautobot-to-DNA Center data sync."""
from typing import Optional, List
from uuid import UUID
from diffsync import DiffSyncModel


class Area(DiffSyncModel):
    """DiffSync model for DNA Center areas."""

    _modelname = "area"
    _identifiers = ("name", "parent")
    _attributes = ()
    _children = {"building": "buildings"}

    name: str
    parent: Optional[str]
    buildings: Optional[List["Building"]] = list()

    uuid: Optional[UUID]


class Building(DiffSyncModel):
    """DiffSync model for DNA Center buildings."""

    _modelname = "building"
    _identifiers = ("name", "area")
    _attributes = ("address", "latitude", "longitude", "tenant")
    _children = {"floor": "floors"}

    name: str
    address: Optional[str]
    area: str
    latitude: Optional[str]
    longitude: Optional[str]
    tenant: Optional[str]
    floors: Optional[List["Floor"]] = list()

    uuid: Optional[UUID]


class Floor(DiffSyncModel):
    """DiffSync model for DNA Center floors."""

    _modelname = "floor"
    _identifiers = ("name", "building")
    _attributes = ("tenant",)
    _children = {}

    name: str
    building: str
    tenant: Optional[str]

    uuid: Optional[UUID]


class Device(DiffSyncModel):
    """DiffSync model for DNA Center devices."""

    _modelname = "device"
    _identifiers = ("name", "site", "serial", "management_addr")
    _attributes = (
        "status",
        "role",
        "vendor",
        "model",
        "area",
        "floor",
        "version",
        "platform",
        "tenant",
    )
    _children = {"port": "ports"}

    name: Optional[str]
    status: Optional[str]
    role: Optional[str]
    vendor: str
    model: str
    area: Optional[str]
    site: Optional[str]
    floor: Optional[str]
    serial: Optional[str]
    version: Optional[str]
    platform: str
    tenant: Optional[str]
    ports: Optional[List["Port"]] = list()
    management_addr: Optional[str]

    uuid: Optional[UUID]


class Port(DiffSyncModel):
    """DiffSync model for DNA Center interfaces."""

    _modelname = "port"
    _identifiers = ("name", "device")
    _attributes = ("description", "port_type", "port_mode", "mac_addr", "mtu", "status", "enabled")
    _children = {}

    name: str
    device: str
    description: Optional[str]
    port_type: str
    port_mode: str
    mac_addr: Optional[str]
    mtu: int
    status: str
    enabled: bool

    uuid: Optional[UUID]


class IPAddress(DiffSyncModel):
    """DiffSync model for DNA Center IP addresses."""

    _modelname = "ipaddress"
    _identifiers = ("address", "device", "interface")
    _attributes = ("primary", "tenant")
    _children = {}

    address: str
    interface: str
    device: str
    primary: bool
    tenant: Optional[str]

    uuid: Optional[UUID]


Area.update_forward_refs()
Building.update_forward_refs()
Device.update_forward_refs()
