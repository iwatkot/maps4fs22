"""This module contains provider of Niedersachsen data."""

from maps4fs.generator.dtm.base.wms import WMSProvider
from maps4fs.generator.dtm.dtm import DTMProvider


class NiedersachsenProvider(WMSProvider, DTMProvider):
    """Provider of Niedersachsen data."""

    _code = "niedersachsen"
    _name = "Lower Saxony DGM1"
    _region = "DE"
    _icon = "🇩🇪󠁥󠁢󠁹󠁿"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _instructions = (
        "Warning: The Niedersachsen DGM1 data is provided as 8-bit Cloud Optimized GeoTIFF "
        "(whole meters only). You will need to use blur ('Blur Radius' under 'DEM Settings') "
        "to smooth the data."
    )
    _is_base = False
    _extents_identifier = "Niedersachsen"

    _url = "https://opendata.lgln.niedersachsen.de/doorman/noauth/dgm_wms"
    _source_crs = "EPSG:25832"
    _tile_size = 2000
    _wms_version = "1.3.0"

    def get_wms_parameters(self, tile):
        return {
            "layers": ["ni_dgm1_grau"],
            "srs": "EPSG:25832",
            "bbox": (tile[1], tile[0], tile[3], tile[2]),
            "size": (2000, 2000),
            "format": "image/tiff",
            "transparent": False,
        }
