"""This module contains provider of Spain data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class SpainProvider(WCSProvider, DTMProvider):
    """Provider of Spain data."""

    _code = "spain"
    _name = "Spain"
    _region = "ES"
    _icon = "🇪🇸"
    _resolution = 5
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _is_base = False

    _extents_identifier = "Spain"

    _url = "https://servicios.idee.es/wcs-inspire/mdt"
    _wcs_version = "2.0.1"
    _source_crs = "EPSG:25830"
    _tile_size = 1000

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": ["Elevacion25830_5"],
            "subsets": [("y", str(tile[0]), str(tile[2])), ("x", str(tile[1]), str(tile[3]))],
            "format": "GEOTIFFINT16",
            "timeout": 600,
        }
