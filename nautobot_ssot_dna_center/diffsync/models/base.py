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
    _attributes = ("address", "latitude", "longitude")
    _children = {"floor": "floors"}

    name: str
    address: Optional[str]
    area: str
    latitude: Optional[str]
    longitude: Optional[str]
    floors: Optional[List["Floor"]] = list()

    uuid: Optional[UUID]


class Floor(DiffSyncModel):
    """DiffSync model for DNA Center floors."""

    _modelname = "floor"
    _identifiers = ("name", "building")
    _attributes = ()
    _children = {}

    name: str
    building: str

    uuid: Optional[UUID]


class Device(DiffSyncModel):
    """DiffSync model for DNA Center devices."""

    _modelname = "device"
    _identifiers = ("name",)
    _attributes = (
        "status",
        "role",
        "vendor",
        "model",
        "area",
        "site",
        "floor",
        "serial",
        "version",
        "platform",
    )
    _children = {"port": "ports"}

    name: str
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
    ports: Optional[List["Port"]] = list()

    uuid: Optional[UUID]


class Port(DiffSyncModel):
    """DiffSync model for DNA Center interfaces."""

    _modelname = "port"
    _identifiers = ("name", "device")
    _attributes = (
        "description",
        "port_type",
        "port_mode",
        "mac_addr",
        "mtu",
    )
    _children = {}

    name: str
    device: str
    description: Optional[str]
    port_type: str
    port_mode: str
    mac_addr: Optional[str]
    mtu: int
    status: str
