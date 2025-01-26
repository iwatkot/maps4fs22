"""This module contains provider of Czech data."""

from maps4fs.generator.dtm.base.wcs import WCSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class CzechProvider(WCSProvider, DTMProvider):
    """Provider of Czech data."""

    _code = "czech"
    _name = "Czech Republic"
    _region = "CZ"
    _icon = "🇨🇿"
    _resolution = 5
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _instructions = None
    _is_base = False

    _extents_identifier = "Czechia"

    _url = "https://ags.cuzk.cz/arcgis2/services/INSPIRE_Nadmorska_vyska/ImageServer/WCSServer"  # pylint: disable=line-too-long
    _wcs_version = "1.0.0"
    _source_crs = "EPSG:4326"
    _tile_size = 0.05

    def get_wcs_parameters(self, tile):
        return {
            "identifier": "MD_LAS",
            "crs": "EPSG:4326",
            "bbox": tile,
            "width": 1000,
            "height": 1000,
            "format": "GeoTIFF",
        }
