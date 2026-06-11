from packaging.version import Version

from src.core.version_exception import VersionException

def check_version_compatibility(client_required_min_version: str, mycel_version: str) -> None:
    client = Version(client_required_min_version)
    mycel = Version(mycel_version)
    
    if client.major != mycel.major:
        raise VersionException(code="INCOMPATIBLE", message=f"Your current Mycel instance (major v{mycel.major}) is incompatible with your implementation (major v{client.major}). Please upgrade your Mycel instance or implementation to the highest major version, or use a different mycel instance.")
    if (client.major, client.minor, client.micro) > (mycel.major, mycel.minor, mycel.micro):
        raise VersionException(code="IMPL_TOO_RECENT", message=f"Your Mycel instance (v{mycel_version}) is outdated. Your implementation requires at least v{client_required_min_version}. Please update your Mycel instance.")
