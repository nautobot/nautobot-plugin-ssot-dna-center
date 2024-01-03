"""DiffSyncModel subclasses for Nautobot-to-DNA Center data sync."""
from typing import Optional, List
from uuid import UUID
from diffsync import DiffSyncModel
from diffsync.enum import DiffSyncModelFlags


class Area(DiffSyncModel):
    """DiffSync model for DNA Center areas."""

    model_flags = DiffSyncModelFlags.SKIP_UNMATCHED_DST

    _modelname = "area"
    _identifiers = ("name", "parent")
    _attributes = ()
    _children = {}

    name: str
    parent: Optional[str]
    buildings: Optional[List["Building"]] = list()

    uuid: Optional[UUID]


class Building(DiffSyncModel):
    """DiffSync model for DNA Center buildings."""

    model_flags = DiffSyncModelFlags.SKIP_UNMATCHED_DST

    _modelname = "building"
    _identifiers = ("name",)
    _attributes = ("address", "area", "latitude", "longitude", "tenant")
    _children = {"floor": "floors"}

    name: str
    address: Optional[str]
    area: Optional[str]
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
    _identifiers = ("name",)
    _attributes = (
        "site",
        "serial",
        "status",
        "role",
        "vendor",
        "model",
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
    site: Optional[str]
    floor: Optional[str]
    serial: str = ""
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
    _attributes = ("description", "mac_addr", "port_type", "port_mode", "mtu", "status", "enabled")
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


class Prefix(DiffSyncModel):
    """DiffSync Model for DNA Center prefixes."""

    _modelname = "prefix"
    _identifiers = ("prefix", "namespace")
    _attributes = ("tenant",)
    _children = {}

    prefix: str
    namespace: str
    tenant: Optional[str]
    uuid: Optional[UUID]


class IPAddress(DiffSyncModel):
    """DiffSync model for DNA Center IP addresses."""

    _modelname = "ipaddress"
    _identifiers = ("address", "device", "interface", "prefix")
    _attributes = ("primary", "tenant")
    _children = {}

    address: str
    prefix: str
    interface: str
    device: str
    primary: bool
    tenant: Optional[str]

    uuid: Optional[UUID]


Area.update_forward_refs()
Building.update_forward_refs()
Device.update_forward_refs()
