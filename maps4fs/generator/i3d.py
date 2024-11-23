"""This module contains the Config class for map settings and configuration."""

from __future__ import annotations

import os
from xml.etree import ElementTree as ET

from maps4fs.generator.component import Component

DEFAULT_HEIGHT_SCALE = 2000
DEFAULT_MAX_LOD_DISTANCE = 10000


# pylint: disable=R0903
class I3d(Component):
    """Component for map i3d file settings and configuration.

    Args:
        coordinates (tuple[float, float]): The latitude and longitude of the center of the map.
        map_height (int): The height of the map in pixels.
        map_width (int): The width of the map in pixels.
        map_directory (str): The directory where the map files are stored.
        logger (Any, optional): The logger to use. Must have at least three basic methods: debug,
            info, warning. If not provided, default logging will be used.
    """

    def preprocess(self) -> None:
        try:
            self._map_i3d_path = self.game.i3d_file_path(self.map_directory)
            self.logger.debug("Map I3D path: %s.", self._map_i3d_path)
        except NotImplementedError:
            self.logger.info("I3D file processing is not implemented for this game.")
            self._map_i3d_path = None

    def process(self) -> None:
        if not self._map_i3d_path:
            self.logger.info("No path to the i3d file was obtained, processing skipped.")
            return

        self._update_i3d_file()

        tree = ET.parse(self._map_i3d_path)

        # Find "Scene" element
        self.logger.debug("Map I3D file loaded from: %s.", self._map_i3d_path)

        root = tree.getroot()
        for map_elem in root.iter("Scene"):
            # Find TerrainTransformGroup element
            # Set heightScale="4000"
            # and maxLODDistance="10000"
            for terrain_elem in map_elem.iter("TerrainTransformGroup"):
                terrain_elem.set("heightScale", str(DEFAULT_HEIGHT_SCALE))
                self.logger.debug(
                    "heightScale attribute set to %s in TerrainTransformGroup element.",
                    DEFAULT_HEIGHT_SCALE,
                )
                terrain_elem.set("maxLODDistance", str(DEFAULT_MAX_LOD_DISTANCE))
                self.logger.debug(
                    "maxLODDistance attribute set to %s in TerrainTransformGroup element.",
                    DEFAULT_MAX_LOD_DISTANCE,
                )
                self.logger.debug("TerrainTransformGroup element updated in I3D file.")

        tree.write(self._map_i3d_path)
        self.logger.debug("Map I3D file saved to: %s.", self._map_i3d_path)

    def _update_i3d_file(self) -> None:
        if not os.path.isfile(self._map_i3d_path):
            self.logger.warning("I3D file not found: %s.", self._map_i3d_path)
            return

    def previews(self) -> list[str]:
        """Returns a list of paths to the preview images (empty list).
        The component does not generate any preview images so it returns an empty list.

        Returns:
            list[str]: An empty list.
        """
        return []
