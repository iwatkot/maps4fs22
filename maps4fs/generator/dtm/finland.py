"""This module contains provider of Finland data."""

from owslib.util import Authentication

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider, DTMProviderSettings


class FinlandProviderSettings(DTMProviderSettings):
    """Settings for the Finland provider."""

    api_key: str = ""


class FinlandProvider(WCSProvider, DTMProvider):
    """Provider of Finland data."""

    _code = "finland"
    _name = "Finland"
    _region = "FI"
    _icon = "🇫🇮"
    _resolution = 2
    _settings = FinlandProviderSettings
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _is_base = False
    _extents_identifier = "Finland"

    _url = "https://avoin-karttakuva.maanmittauslaitos.fi/ortokuvat-ja-korkeusmallit/wcs/v2"
    _wcs_version = "2.0.1"
    _source_crs = "EPSG:3067"
    _tile_size = 1000

    _instructions = (
        "ℹ️ This provider requires an API Key. See [here](https://www.maanmittausl"
        "aitos.fi/rajapinnat/api-avaimen-ohje) for more information on how to create one, then "
        "enter it below in the settings field for API Key."
    )

    def get_wcs_instance_parameters(self):
        if not self.user_settings.api_key:
            raise ValueError("API Key is required for this provider.")

        settings = super().get_wcs_instance_parameters()
        settings["auth"] = Authentication(
            username=self.user_settings.api_key, password=self.user_settings.api_key
        )
        return settings

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": ["korkeusmalli_2m"],
            "subsets": [("N", str(tile[0]), str(tile[2])), ("E", str(tile[1]), str(tile[3]))],
            "format": "image/tiff",
            "timeout": 600,
        }
