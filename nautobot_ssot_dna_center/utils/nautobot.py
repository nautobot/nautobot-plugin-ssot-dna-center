"""Utility functions for working with Nautobot."""
from uuid import UUID
from django.contrib.contenttypes.models import ContentType
from netutils.lib_mapper import ANSIBLE_LIB_MAPPER_REVERSE, NAPALM_LIB_MAPPER_REVERSE
from nautobot.dcim.models import Device, Platform
from nautobot.extras.models import Relationship, RelationshipAssociation

try:
    from nautobot_device_lifecycle_mgmt.models import SoftwareLCM

    LIFECYCLE_MGMT = True
except ImportError:
    LIFECYCLE_MGMT = False


def verify_platform(platform_name: str, manu: UUID) -> Platform:
    """Verifies Platform object exists in Nautobot. If not, creates it.

    Args:
        platform_name (str): Name of platform to verify.
        manu (UUID): The ID (primary key) of platform manufacturer.

    Returns:
        Platform: Found or created Platform object.
    """
    if ANSIBLE_LIB_MAPPER_REVERSE.get(platform_name):
        _name = ANSIBLE_LIB_MAPPER_REVERSE[platform_name]
    else:
        _name = platform_name
    if NAPALM_LIB_MAPPER_REVERSE.get(platform_name):
        napalm_driver = NAPALM_LIB_MAPPER_REVERSE[platform_name]
    else:
        napalm_driver = platform_name
    try:
        platform_obj = Platform.objects.get(slug=platform_name)
    except Platform.DoesNotExist:
        platform_obj = Platform(
            name=_name,
            slug=platform_name,
            manufacturer_id=manu,
            napalm_driver=napalm_driver[:50],
        )
        platform_obj.validated_save()
    return platform_obj


def add_software_lcm(diffsync, platform: str, version: str):
    """Add OS Version as SoftwareLCM if Device Lifecycle Plugin found.

    Args:
        diffsync (DiffSyncAdapter): DiffSync adapter with Job and maps.
        platform (str): Name of platform to associate version to.
        version (str): The software version to be created for specified platform.

    Returns:
        UUID: UUID of the OS Version that is being found or created.
    """
    platform = Platform.objects.get(slug=platform)
    try:
        os_ver = SoftwareLCM.objects.get(device_platform=platform, version=version).id
    except SoftwareLCM.DoesNotExist:
        diffsync.job.log_info(message=f"Creating Version {version} for {platform}.")
        os_ver = SoftwareLCM(
            device_platform=platform,
            version=version,
        )
        os_ver.validated_save()
        os_ver = os_ver.id
    return os_ver


def assign_version_to_device(diffsync, device: Device, software_lcm: UUID):
    """Add Relationship between Device and SoftwareLCM."""
    try:
        software_relation = Relationship.objects.get(slug="device_soft")
        relationship = RelationshipAssociation.objects.get(relationship=software_relation, destination_id=device.id)
        diffsync.job.log_warning(
            message=f"Deleting Software Version Relationships for {device.name} to assign a new version."
        )
        relationship.delete()
    except RelationshipAssociation.DoesNotExist:
        pass
    new_assoc = RelationshipAssociation(
        relationship=Relationship.objects.get(slug="device_soft"),
        source_type=ContentType.objects.get_for_model(SoftwareLCM),
        source_id=software_lcm,
        destination_type=ContentType.objects.get_for_model(Device),
        destination_id=device.id,
    )
    new_assoc.validated_save()
