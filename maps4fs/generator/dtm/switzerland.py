"""This module contains provider of Switzerland data."""

import json
import os

import requests

from maps4fs.generator.dtm import utils
from maps4fs.generator.dtm.dtm import DTMProvider, DTMProviderSettings


class SwitzerlandProviderSettings(DTMProviderSettings):
    """Settings for the Switzerland provider."""

    resolution: tuple | str = ("0.5", "2.0")


class SwitzerlandProvider(DTMProvider):
    """Provider of Switzerland."""

    _code = "switzerland"
    _name = "Switzerland"
    _region = "CH"
    _icon = "🇨🇭"
    _resolution = "0.5-2"
    _settings = SwitzerlandProviderSettings
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True

    _extents_identifier = "Switzerland"

    _url = (
        "https://ogd.swisstopo.admin.ch/services/swiseld/"
        "services/assets/ch.swisstopo.swissalti3d/search"
    )

    def download_tiles(self):
        download_urls = self.get_download_urls()
        all_tif_files = self.download_tif_files(download_urls, self.shared_tiff_path)
        return all_tif_files

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared_tiff_path = os.path.join(self._tile_directory, "shared")
        os.makedirs(self.shared_tiff_path, exist_ok=True)

    def get_download_urls(self) -> list[str]:
        """Get download URLs of the GeoTIFF files from the USGS API.

        Returns:
            list: List of download URLs.
        """
        urls = []
        try:
            bbox = self.get_bbox()
            north, south, east, west = utils.transform_bbox(bbox, "EPSG:2056")

            params = {
                "format": "image/tiff; application=geotiff; profile=cloud-optimized",
                "resolution": self.user_settings.resolution,  # type: ignore
                "srid": 2056,
                "state": "current",
            }

            data = {
                "geometry": json.dumps(
                    {
                        "type": "Polygon",
                        "crs": {"type": "name", "properties": {"name": "EPSG:2056"}},
                        "coordinates": [
                            [
                                [north, east],
                                [south, east],
                                [south, west],
                                [north, west],
                                [north, east],
                            ]
                        ],
                    }
                )
            }

            response = requests.post(  # pylint: disable=W3101
                self.url,  # type: ignore
                params=params,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=60,
            )
            self.logger.debug("Getting file locations...")

            # Check if the request was successful (HTTP status code 200)
            if response.status_code == 200:
                # Parse the JSON response
                json_data = response.json()
                items = json_data["items"]
                for item in items:
                    urls.append(item["ass_asset_href"])
            else:
                self.logger.error("Failed to get data. HTTP Status Code: %s", response.status_code)
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to get data. Error: %s", e)
        self.logger.debug("Received %s urls", len(urls))
        return urls
