"""This module contains provider of NRW data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class NRWProvider(WCSProvider, DTMProvider):
    """Provider of NRW data."""

    _code = "NRW"
    _name = "North Rhine-Westphalia DGM1"
    _region = "DE"
    _icon = "🇩🇪󠁥󠁢󠁹󠁿"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _is_base = False
    _extents_identifier = "Nordrhein-Westfalen"

    _url = "https://www.wcs.nrw.de/geobasis/wcs_nw_dgm"
    _wcs_version = "2.0.1"
    _source_crs = "EPSG:25832"
    _tile_size = 1000

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": ["nw_dgm"],
            "subsets": [("y", str(tile[0]), str(tile[2])), ("x", str(tile[1]), str(tile[3]))],
            "format": "image/tiff",
        }
