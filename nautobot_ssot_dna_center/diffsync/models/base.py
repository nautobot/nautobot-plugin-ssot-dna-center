"""DiffSyncModel subclasses for Nautobot-to-DNA Center data sync."""
from typing import Optional
from uuid import UUID
from diffsync import DiffSyncModel


class Device(DiffSyncModel):
    """DiffSync model for DNA Center devices."""

    _modelname = "device"
    _identifiers = ("name",)
    _attributes = (
        "status",
        "role",
        "model",
        "site",
        "ip_address",
    )
    _children = {}

    name: str
    status: Optional[str]
    role: Optional[str]
    model: Optional[str]
    site: Optional[str]
    ip_address = Optional[str]

    uuid = Optional[UUID]
