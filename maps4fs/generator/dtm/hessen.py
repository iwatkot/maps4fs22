"""This module contains provider of Hessen data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class HessenProvider(WCSProvider, DTMProvider):
    """Provider of Hessen data."""

    _code = "hessen"
    _name = "Hessen DGM1"
    _region = "DE"
    _icon = "🇩🇪󠁥"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _is_base = False
    _extents_identifier = "Hessen"

    _url = "https://inspire-hessen.de/raster/dgm1/ows"
    _wcs_version = "2.0.1"
    _source_crs = "EPSG:25832"
    _tile_size = 1000

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": ["he_dgm1"],
            "subsets": [("N", str(tile[0]), str(tile[2])), ("E", str(tile[1]), str(tile[3]))],
            "format": "image/gtiff",
            "timeout": 600,
        }
