"""This module contains provider of Arctic data."""

import os

import requests

from maps4fs.generator.dtm.dtm import DTMProvider


class ArcticProvider(DTMProvider):
    """Provider of Arctic data."""

    _code = "arctic"
    _name = "ArcticDEM"
    _region = "Global"
    _icon = "🌍"
    _resolution = 2
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True

    _extents_identifier = "Arctic"

    _instructions = (
        "This provider source includes 2 meter DEM data for the entire Arctic region above 50 "
        "degrees North. The tiles are very big, around 1 GB each, so downloading and processing "
        "them can take a long time."
    )

    _url = "https://stac.pgc.umn.edu/api/v1/collections/arcticdem-mosaics-v4.1-2m/items"

    def download_tiles(self):
        download_urls = self.get_download_urls()
        all_tif_files = self.download_tif_files(download_urls, self.shared_tiff_path)
        return all_tif_files

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared_tiff_path = os.path.join(self._tile_directory, "shared")
        os.makedirs(self.shared_tiff_path, exist_ok=True)

    def get_download_urls(self) -> list[str]:
        """Get download URLs of the GeoTIFF files from the OGC API.

        Returns:
            list: List of download URLs.
        """
        urls = []

        try:
            # Make the GET request
            north, south, east, west = self.get_bbox()
            response = requests.get(  # pylint: disable=W3101
                self.url,  # type: ignore
                params={
                    "bbox": f"{west},{south},{east},{north}",
                    "limit": "100",
                },
                timeout=60,
            )
            self.logger.debug("Getting file locations from ArcticDEM OGC API...")

            # Check if the request was successful (HTTP status code 200)
            if response.status_code == 200:
                # Parse the JSON response
                json_data = response.json()
                items = json_data["features"]
                for item in items:
                    urls.append(item["assets"]["dem"]["href"])
            else:
                self.logger.error("Failed to get data. HTTP Status Code: %s", response.status_code)
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to get data. Error: %s", e)
        self.logger.debug("Received %s urls", len(urls))
        return urls
