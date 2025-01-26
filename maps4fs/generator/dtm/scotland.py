"""This module contains provider of Scotland data."""

import os

import requests

from maps4fs.generator.dtm.dtm import DTMProvider, DTMProviderSettings


class ScotlandProviderSettings(DTMProviderSettings):
    """Settings for the Scotland provider."""

    dataset: dict | str = {
        "scotland-gov/lidar/phase-1/dtm": "LiDAR for Scotland Phase I DTM",
        "scotland-gov/lidar/phase-2/dtm": "LiDAR for Scotland Phase II DTM",
        "scotland-gov/lidar/phase-3/dtm": "LiDAR for Scotland Phase III DTM",
        "scotland-gov/lidar/phase-4/dtm": "LiDAR for Scotland Phase IV DTM",
        "scotland-gov/lidar/phase-5/dtm": "LiDAR for Scotland Phase V DTM",
        "scotland-gov/lidar/phase-6/dtm": "LiDAR for Scotland Phase VI DTM",
        "scotland-gov/lidar/hes/hes-2010/dtm": (
            "HES LiDAR Data Stirling City and surrounding area (2010) DTM"
        ),
        "scotland-gov/lidar/hes/hes-2010s10/dtm": (
            "LiDAR for Historic Environment Scotland Scottish Ten Project (2010) DTM"
        ),
        "scotland-gov/lidar/hes/hes-2016-2017/dtm": (
            "LiDAR for Historic Environment Scotland Projects (2016-2017 sub project 4) DTM"
        ),
        "scotland-gov/lidar/hes/hes-2016/dtm": (
            "LiDAR for Historic Environment Scotland Projects (2016) DTM"
        ),
        "scotland-gov/lidar/hes/hes-2017/dtm": (
            "LiDAR for Historic Environment Scotland Projects (2017) DTM"
        ),
        "scotland-gov/lidar/hes/hes-2017sp3/dtm": (
            "LiDAR for Historic Environment Scotland Project (2017 Sub Project 3) DTM"
        ),
        "scotland-gov/lidar/hes/hes-luing/dtm": (
            "LiDAR for Historic Environment Scotland Projects Isle of Luing DTM"
        ),
        "scotland-gov/lidar/outerheb-2019/dtm/25cm": "LiDAR for Outer Hebrides 2019 - 25cm DTM",
        "scotland-gov/lidar/outerheb-2019/dtm/50cm": "LiDAR for Outer Hebrides 2019 - 50cm DTM",
    }


class ScotlandProvider(DTMProvider):
    """Provider of Scotland."""

    _code = "scotland"
    _name = "Scotland LiDAR"
    _region = "UK"
    _icon = "🏴󠁧󠁢󠁳󠁣󠁴󠁿"
    _resolution = "variable"
    _settings = ScotlandProviderSettings
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True
    _instructions = (
        "Coverage for Scotland is very limited. "
        "Make sure to check the [coverage map](https://remotesensingdata.gov.scot/data#/map)."
    )

    _extents_identifier = "Scotland"

    _url = "https://srsp-catalog.jncc.gov.uk/search/product"

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
            # Make the GET request
            (north, south, east, west) = self.get_bbox()
            response = requests.post(  # pylint: disable=W3101
                self.url,  # type: ignore
                json={
                    "collections": (
                        [self.user_settings.dataset] if self.user_settings else []  # type: ignore
                    ),
                    "footprint": (
                        f"POLYGON(({west} {south}, {west} {north}, "
                        f"{east} {north}, {east} {south}, {west} {south}))"
                    ),
                    "offset": 0,
                    "limit": 100,
                    "spatialop": "intersects",
                },
                timeout=60,
            )
            self.logger.debug("Getting file locations from JNCC...")

            # Check if the request was successful (HTTP status code 200)
            if response.status_code == 200:
                # Parse the JSON response
                json_data = response.json()
                items = json_data["result"]
                for item in items:
                    urls.append(item["data"]["product"]["http"]["url"])
                # self.download_tif_files(urls)
            else:
                self.logger.error("Failed to get data. HTTP Status Code: %s", response.status_code)
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to get data. Error: %s", e)
        self.logger.debug("Received %s urls", len(urls))
        return urls
