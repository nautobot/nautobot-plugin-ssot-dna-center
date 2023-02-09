"""DiffSyncModel subclasses for Nautobot-to-DNA Center data sync."""
from typing import Optional
from uuid import UUID
from diffsync import DiffSyncModel


class Site(DiffSyncModel):
    """DiffSync model for DNA Center sites."""

    _modelname = "site"
    _identifiers = ("name", "parent")
    _attributes = ("address",)
    _children = {}

    name: str
    address: Optional[str]
    site_type: Optional[str]
    parent: str


class Device(DiffSyncModel):
    """DiffSync model for DNA Center devices."""

    _modelname = "device"
    _identifiers = ("name",)
    _attributes = (
        "status",
        "role",
        "model",
        "site",
    )
    _children = {}

    name: str
    status: Optional[str]
    role: Optional[str]
    model: Optional[str]
    site: Optional[str]

    uuid = Optional[UUID]
