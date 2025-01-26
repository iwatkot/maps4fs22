"""This module contains provider of England data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class England1MProvider(WCSProvider, DTMProvider):
    """Provider of England data."""

    _code = "england1m"
    _name = "England DGM1"
    _region = "UK"
    _icon = "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _instructions = None
    _is_base = False
    _extents_identifier = "England"

    _url = "https://environment.data.gov.uk/geoservices/datasets/13787b9a-26a4-4775-8523-806d13af58fc/wcs"  # pylint: disable=line-too-long
    _wcs_version = "2.0.1"
    _source_crs = "EPSG:27700"
    _tile_size = 1000

    def get_wcs_parameters(self, tile):
        return {
            "identifier": ["13787b9a-26a4-4775-8523-806d13af58fc:Lidar_Composite_Elevation_DTM_1m"],
            "subsets": [("E", str(tile[1]), str(tile[3])), ("N", str(tile[0]), str(tile[2]))],
            "format": "tiff",
        }
