"""This module contains provider of Norway data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class NorwayProvider(WCSProvider, DTMProvider):
    """Provider of Norway data."""

    _code = "norway"
    _name = "Norway Topobathy"
    _region = "NO"
    _icon = "🇳🇴"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _instructions = None
    _is_base = False

    _extents_identifier = "Norway"

    _instructions = (
        "This is a topobathy dataset which means it includes water depth information as well. "
        "You do not have to manually set a water depth to get realistic water depths in your map."
    )

    _url = "https://wms.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-topobathy-25833"
    _wcs_version = "1.0.0"
    _source_crs = "EPSG:25833"
    _tile_size = 1000

    def get_wcs_parameters(self, tile):
        return {
            "identifier": "nhm_dtm_topobathy_25833",
            "bbox": (tile[1], tile[0], tile[3], tile[2]),
            "crs": "EPSG:25833",
            "width": 1000,
            "height": 1000,
            "format": "tiff",
        }
