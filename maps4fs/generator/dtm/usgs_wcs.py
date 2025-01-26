"""This module contains provider of USGS data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class USGSWCSProvider(WCSProvider, DTMProvider):
    """Provider of USGS data."""

    _code = "usgs_wcs"
    _name = "USGS"
    _region = "USA"
    _icon = "🇺🇸"
    _resolution = "1-90"
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _instructions = None
    _is_base = False
    _extents_identifier = "United States of America"

    _url = "https://elevation.nationalmap.gov/arcgis/services/3DEPElevation/ImageServer/WCSServer"
    _wcs_version = "1.0.0"
    _source_crs = "EPSG:3857"
    _tile_size = 1000
    _is_multipart = False

    def get_wcs_parameters(self, tile):
        return {
            "identifier": "DEP3Elevation",
            "bbox": (tile[1], tile[0], tile[3], tile[2]),
            "crs": "EPSG:3857",
            "width": 1000,
            "height": 1000,
            "format": "GeoTIFF",
        }
