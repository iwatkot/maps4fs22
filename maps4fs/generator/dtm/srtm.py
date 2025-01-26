"""This module contains provider of Shuttle Radar Topography Mission (SRTM) 30m data."""

# Author: https://github.com/iwatkot

import gzip
import math
import os
import shutil

import requests

from maps4fs.generator.dtm.dtm import DTMProvider


class SRTM30Provider(DTMProvider):
    """Provider of Shuttle Radar Topography Mission (SRTM) 30m data."""

    _code = "srtm30"
    _name = "SRTM 30 m"
    _region = "Global"
    _icon = "🌎"
    _resolution = 30.0

    _extents_identifier = "SRTM"

    _url = "https://elevation-tiles-prod.s3.amazonaws.com/skadi/{latitude_band}/{tile_name}.hgt.gz"

    _author = "[iwatkot](https://github.com/iwatkot)"

    _instructions = "ℹ️ Recommended settings:  \nDEM Settings -> Blur Radius: **35**"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hgt_directory = os.path.join(self._tile_directory, "hgt")
        self.gz_directory = os.path.join(self._tile_directory, "gz")
        os.makedirs(self.hgt_directory, exist_ok=True)
        os.makedirs(self.gz_directory, exist_ok=True)
        self.data_info: dict[str, int | str | float] | None = None  # type: ignore

    def download_tiles(self):
        """Download SRTM tiles."""
        north, south, east, west = self.get_bbox()

        tiles = []
        # Look at each corner of the bbox in case the bbox spans across multiple tiles
        for pair in [(north, east), (south, west), (south, east), (north, west)]:
            tile_parameters = self.get_tile_parameters(*pair)
            tile_name = tile_parameters["tile_name"]
            decompressed_tile_path = os.path.join(self.hgt_directory, f"{tile_name}.hgt")

            if not os.path.isfile(decompressed_tile_path):
                compressed_tile_path = os.path.join(self.gz_directory, f"{tile_name}.hgt.gz")
                if not self.get_or_download_tile(compressed_tile_path, **tile_parameters):
                    raise FileNotFoundError(f"Tile {tile_name} not found.")

                with gzip.open(compressed_tile_path, "rb") as f_in:
                    with open(decompressed_tile_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            tiles.append(decompressed_tile_path)

        return list(set(tiles))

    # region provider specific helpers
    def download_tile(self, output_path: str, **kwargs) -> bool:
        """Download a tile from the provider.

        Arguments:
            output_path (str): Path to save the downloaded tile.

        Returns:
            bool: True if the tile was downloaded successfully, False otherwise.
        """
        url = self.formatted_url(**kwargs)
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            return True
        return False

    def get_or_download_tile(self, output_path: str, **kwargs) -> str | None:
        """Get or download a tile from the provider.

        Arguments:
            output_path (str): Path to save the downloaded tile.

        Returns:
            str: Path to the downloaded tile or None if the tile not exists and was
                not downloaded.
        """
        if not os.path.exists(output_path):
            if not self.download_tile(output_path, **kwargs):
                return None
        return output_path

    def get_tile_parameters(self, *args) -> dict[str, str]:
        """Returns latitude band and tile name for SRTM tile from coordinates.

        Arguments:
            lat (float): Latitude.
            lon (float): Longitude.

        Returns:
            dict: Tile parameters.
        """
        lat, lon = args

        tile_latitude = math.floor(lat)
        tile_longitude = math.floor(lon)

        latitude_band = f"N{abs(tile_latitude):02d}" if lat >= 0 else f"S{abs(tile_latitude):02d}"
        if lon < 0:
            tile_name = f"{latitude_band}W{abs(tile_longitude):03d}"
        else:
            tile_name = f"{latitude_band}E{abs(tile_longitude):03d}"

        self.logger.debug(
            "Detected tile name: %s for coordinates: lat %s, lon %s.", tile_name, lat, lon
        )
        return {"latitude_band": latitude_band, "tile_name": tile_name}

    # endregion
