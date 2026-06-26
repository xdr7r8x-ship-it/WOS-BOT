from .manual_alliance_provider import ManualAllianceProvider
from .http_alliance_provider import HttpAllianceProvider
from .mock_alliance_provider import MockAllianceProvider


ALLIANCE_PROVIDERS = {
    "manual": ManualAllianceProvider,
    "http": HttpAllianceProvider,
    "mock": MockAllianceProvider,
}


def get_provider(provider_type: str) -> type:
    return ALLIANCE_PROVIDERS.get(provider_type, ManualAllianceProvider)
