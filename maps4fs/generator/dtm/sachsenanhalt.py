"""This module contains provider of Sachsen-Anhalt data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class SachsenAnhaltProvider(WCSProvider, DTMProvider):
    """Provider of Sachsen-Anhalt data."""

    _code = "sachsen-anhalt"
    _name = "Sachsen-Anhalt"
    _region = "DE"
    _icon = "🇩🇪"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _is_base = False

    _extents_identifier = "Sachsen-Anhalt"

    _url = "https://www.geodatenportal.sachsen-anhalt.de/wss/service/ST_LVermGeo_DGM1_WCS_OpenData/guest"  # pylint: disable=line-too-long
    _wcs_version = "1.0.0"
    _source_crs = "EPSG:4326"
    _tile_size = 0.02

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": "1",
            "bbox": tile,
            "format": "GeoTIFF",
            "crs": "EPSG:4326",
            "width": 1000,
            "height": 1000,
            "timeout": 600,
        }
