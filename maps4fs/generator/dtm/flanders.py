"""This module contains provider of Flanders data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class FlandersProvider(WCSProvider, DTMProvider):
    """Provider of Flanders data."""

    _code = "flanders"
    _name = "Flanders DHM II"
    _region = "BE"
    _icon = "🇧🇪"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _is_base = False
    _extents_identifier = "Flanders"

    _url = "https://geo.api.vlaanderen.be/el-dtm/wcs"
    _wcs_version = "1.0.0"
    _source_crs = "EPSG:4258"
    _tile_size = 0.02

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": "EL.GridCoverage.DTM",
            "bbox": tile,
            "format": "GeoTIFF",
            "crs": "EPSG:4258",
            "width": 1000,
            "height": 1000,
            "timeout": 600,
        }
