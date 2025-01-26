"""This module contains provider of Bavaria data."""

import hashlib
import os
from xml.etree import ElementTree as ET

import requests

from maps4fs.generator.dtm.dtm import DTMProvider


class BavariaProvider(DTMProvider):
    """Provider of Bavaria Digital terrain model (DTM) 1m data.
    Data is provided by the 'Bayerische Vermessungsverwaltung' and available
    at https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=dgm1 under CC BY 4.0 license.
    """

    _code = "bavaria"
    _name = "Bavaria DGM1"
    _region = "DE"
    _icon = "🇩🇪󠁥󠁢󠁹󠁿"
    _resolution = 1
    _author = "[H4rdB4se](https://github.com/H4rdB4se)"
    _is_community = True
    _instructions = None
    _extents_identifier = "Bayern"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tiff_path = os.path.join(self._tile_directory, "tiffs")
        os.makedirs(self.tiff_path, exist_ok=True)
        self.meta4_path = os.path.join(self._tile_directory, "meta4")
        os.makedirs(self.meta4_path, exist_ok=True)

    def download_tiles(self) -> list[str]:
        download_urls = self.get_meta_file_from_coords()
        all_tif_files = self.download_tif_files(download_urls, self.tiff_path)
        return all_tif_files

    @staticmethod
    def get_meta_file_name(north: float, south: float, east: float, west: float) -> str:
        """Generate a hashed file name for the .meta4 file.

        Arguments:
            north (float): Northern latitude.
            south (float): Southern latitude.
            east (float): Eastern longitude.
            west (float): Western longitude.

        Returns:
            str: Hashed file name.
        """
        coordinates = f"{north}_{south}_{east}_{west}"
        hash_object = hashlib.md5(coordinates.encode())
        hashed_file_name = "download_" + hash_object.hexdigest() + ".meta4"
        return hashed_file_name

    def get_meta_file_from_coords(self) -> list[str]:
        """Download .meta4 (xml format) file

        Returns:
            list: List of download URLs.
        """
        (north, south, east, west) = self.get_bbox()
        file_path = os.path.join(self.meta4_path, self.get_meta_file_name(north, south, east, west))
        if not os.path.exists(file_path):
            try:
                # Make the GET request
                response = requests.post(
                    "https://geoservices.bayern.de/services/poly2metalink/metalink/dgm1",
                    (
                        f"SRID=4326;POLYGON(({west} {south},{east} {south},"
                        f"{east} {north},{west} {north},{west} {south}))"
                    ),
                    stream=True,
                    timeout=60,
                )

                # Check if the request was successful (HTTP status code 200)
                if response.status_code == 200:
                    # Write the content of the response to the file
                    with open(file_path, "wb") as meta_file:
                        for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                            meta_file.write(chunk)
                    self.logger.debug("File downloaded successfully: %s", file_path)
                else:
                    self.logger.error("Download error. HTTP Status Code: %s", response.status_code)
            except requests.exceptions.RequestException as e:
                self.logger.error("Failed to get data. Error: %s", e)
        else:
            self.logger.debug("File already exists: %s", file_path)
        return self.extract_urls_from_xml(file_path)

    def extract_urls_from_xml(self, file_path: str) -> list[str]:
        """Extract URLs from the XML file.

        Arguments:
            file_path (str): Path to the XML file.

        Returns:
            list: List of URLs.
        """
        urls: list[str] = []
        root = ET.parse(file_path).getroot()
        namespace = {"ml": "urn:ietf:params:xml:ns:metalink"}

        for file in root.findall(".//ml:file", namespace):
            url = file.find("ml:url", namespace)
            if url is not None:
                urls.append(str(url.text))

        self.logger.debug("Received %s urls", len(urls))
        return urls
