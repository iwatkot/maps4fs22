"""This module contains Map class, which is used to generate map using all components."""

from __future__ import annotations

import json
import os
import shutil
from typing import Any, Generator

from geopy.geocoders import Nominatim

from maps4fs.generator.component import Background, Component, Layer, Texture
from maps4fs.generator.dtm.dtm import DTMProvider, DTMProviderSettings
from maps4fs.generator.game import Game
from maps4fs.generator.settings import (
    BackgroundSettings,
    DEMSettings,
    GRLESettings,
    I3DSettings,
    SatelliteSettings,
    SharedSettings,
    SplineSettings,
    TextureSettings,
)
from maps4fs.generator.statistics import send_advanced_settings, send_main_settings
from maps4fs.logger import Logger


class Map:
    """Class used to generate map using all components.

    Arguments:
        game (Type[Game]): Game for which the map is generated.
        coordinates (tuple[float, float]): Coordinates of the center of the map.
        size (int): Height and width of the map in pixels (it's a square).
        map_directory (str): Path to the directory where map files will be stored.
        logger (Any): Logger instance
    """

    def __init__(
        self,
        game: Game,
        dtm_provider: DTMProvider,
        dtm_provider_settings: DTMProviderSettings | None,
        coordinates: tuple[float, float],
        size: int,
        rotation: int,
        map_directory: str,
        logger: Any = None,
        custom_osm: str | None = None,
        dem_settings: DEMSettings = DEMSettings(),
        background_settings: BackgroundSettings = BackgroundSettings(),
        grle_settings: GRLESettings = GRLESettings(),
        i3d_settings: I3DSettings = I3DSettings(),
        texture_settings: TextureSettings = TextureSettings(),
        spline_settings: SplineSettings = SplineSettings(),
        satellite_settings: SatelliteSettings = SatelliteSettings(),
        **kwargs,
    ):
        if not logger:
            logger = Logger(to_stdout=True, to_file=False)
        self.logger = logger
        self.size = size

        if rotation:
            rotation_multiplier = 1.5
        else:
            rotation_multiplier = 1

        self.rotation = rotation
        self.rotated_size = int(size * rotation_multiplier)

        self.game = game
        self.dtm_provider = dtm_provider
        self.dtm_provider_settings = dtm_provider_settings
        self.components: list[Component] = []
        self.coordinates = coordinates
        self.map_directory = map_directory

        try:
            main_settings = {
                "game": game.code,
                "latitude": coordinates[0],
                "longitude": coordinates[1],
                "country": self.get_country_by_coordinates(),
                "size": size,
                "rotation": rotation,
                "dtm_provider": dtm_provider.name(),
                "custom_osm": bool(custom_osm),
                "is_public": kwargs.get("is_public", False),
            }
            send_main_settings(main_settings)
        except Exception as e:
            self.logger.error("Error sending main settings: %s", e)

        log_entry = ""
        log_entry += f"Map instance created for Game: {game.code}. "
        log_entry += f"Coordinates: {coordinates}. Size: {size}. Rotation: {rotation}. "
        log_entry += f"DTM provider is {dtm_provider.name()}. "

        self.custom_osm = custom_osm
        log_entry += f"Custom OSM file: {custom_osm}. "

        # Make a copy of a custom osm file to the map directory, so it will be
        # included in the output archive.
        if custom_osm:
            copy_path = os.path.join(self.map_directory, "custom_osm.osm")
            shutil.copyfile(custom_osm, copy_path)
            self.logger.debug("Custom OSM file copied to %s", copy_path)

        self.dem_settings = dem_settings
        log_entry += f"DEM settings: {dem_settings}. "
        if self.dem_settings.water_depth > 0:
            # Make sure that the plateau value is >= water_depth
            self.dem_settings.plateau = max(
                self.dem_settings.plateau, self.dem_settings.water_depth
            )

        self.background_settings = background_settings
        log_entry += f"Background settings: {background_settings}. "
        self.grle_settings = grle_settings
        log_entry += f"GRLE settings: {grle_settings}. "
        self.i3d_settings = i3d_settings
        log_entry += f"I3D settings: {i3d_settings}. "
        self.texture_settings = texture_settings
        log_entry += f"Texture settings: {texture_settings}. "
        self.spline_settings = spline_settings
        log_entry += f"Spline settings: {spline_settings}. "
        self.satellite_settings = satellite_settings

        self.logger.info(log_entry)
        os.makedirs(self.map_directory, exist_ok=True)
        self.logger.debug("Map directory created: %s", self.map_directory)

        settings = [
            dem_settings,
            background_settings,
            grle_settings,
            i3d_settings,
            texture_settings,
            spline_settings,
            satellite_settings,
        ]

        settings_json = {}

        for setting in settings:
            settings_json[setting.__class__.__name__] = setting.model_dump()

        try:
            send_advanced_settings(settings_json)
        except Exception as e:
            self.logger.error("Error sending advanced settings: %s", e)

        save_path = os.path.join(self.map_directory, "generation_settings.json")

        with open(save_path, "w", encoding="utf-8") as file:
            json.dump(settings_json, file, indent=4)

        self.shared_settings = SharedSettings()

        self.texture_custom_schema = kwargs.get("texture_custom_schema", None)
        if self.texture_custom_schema:
            save_path = os.path.join(self.map_directory, "texture_custom_schema.json")
            with open(save_path, "w", encoding="utf-8") as file:
                json.dump(self.texture_custom_schema, file, indent=4)
            self.logger.debug("Texture custom schema saved to %s", save_path)

        self.tree_custom_schema = kwargs.get("tree_custom_schema", None)
        if self.tree_custom_schema:
            save_path = os.path.join(self.map_directory, "tree_custom_schema.json")
            with open(save_path, "w", encoding="utf-8") as file:
                json.dump(self.tree_custom_schema, file, indent=4)
            self.logger.debug("Tree custom schema saved to %s", save_path)

        self.custom_background_path = kwargs.get("custom_background_path", None)
        if self.custom_background_path:
            save_path = os.path.join(self.map_directory, "custom_background.png")
            shutil.copyfile(self.custom_background_path, save_path)

        try:
            shutil.unpack_archive(game.template_path, self.map_directory)
            self.logger.debug("Map template unpacked to %s", self.map_directory)
        except Exception as e:
            raise RuntimeError(f"Can not unpack map template due to error: {e}") from e

    @property
    def texture_schema(self) -> list[dict[str, Any]] | None:
        """Return texture schema (custom if provided, default otherwise).

        Returns:
            list[dict[str, Any]] | None: Texture schema.
        """
        if self.texture_custom_schema:
            return self.texture_custom_schema
        with open(self.game.texture_schema, "r", encoding="utf-8") as file:
            return json.load(file)

    def generate(self) -> Generator[str, None, None]:
        """Launch map generation using all components. Yield component names during the process.

        Yields:
            Generator[str, None, None]: Component names.
        """
        self.logger.debug(
            "Starting map generation. Game code: %s. Coordinates: %s, size: %s. Rotation: %s.",
            self.game.code,
            self.coordinates,
            self.size,
            self.rotation,
        )

        for game_component in self.game.components:
            component = game_component(
                self.game,
                self,
                self.coordinates,
                self.size,
                self.rotated_size,
                self.rotation,
                self.map_directory,
                self.logger,
                texture_custom_schema=self.texture_custom_schema,
                tree_custom_schema=self.tree_custom_schema,
            )
            self.components.append(component)

            yield component.__class__.__name__

            try:
                component.process()
            except Exception as e:
                self.logger.error(
                    "Error processing component %s: %s",
                    component.__class__.__name__,
                    e,
                )
                raise e

            try:
                component.commit_generation_info()
            except Exception as e:
                self.logger.error(
                    "Error committing generation info for component %s: %s",
                    component.__class__.__name__,
                    e,
                )
                raise e

        self.logger.debug(
            "Map generation completed. Game code: %s. Coordinates: %s, size: %s. Rotation: %s.",
            self.game.code,
            self.coordinates,
            self.size,
            self.rotation,
        )

    def get_component(self, component_name: str) -> Component | None:
        """Get component by name.

        Arguments:
            component_name (str): Name of the component.

        Returns:
            Component | None: Component instance or None if not found.
        """
        for component in self.components:
            if component.__class__.__name__ == component_name:
                return component
        return None

    def get_texture_component(self) -> Texture | None:
        """Get texture component.

        Returns:
            Texture | None: Texture instance or None if not found.
        """
        component = self.get_component("Texture")
        if not isinstance(component, Texture):
            return None
        return component

    def get_background_component(self) -> Background | None:
        """Get background component.

        Returns:
            Background | None: Background instance or None if not found.
        """
        component = self.get_component("Background")
        if not isinstance(component, Background):
            return None
        return component

    def get_texture_layer(self, by_usage: str | None = None) -> Layer | None:
        """Get texture layer by usage.

        Arguments:
            by_usage (str, optional): Texture usage.

        Returns:
            Layer | None: Texture layer instance or None if not found.
        """
        texture_component = self.get_texture_component()
        if not texture_component:
            return None
        if by_usage:
            return texture_component.get_layer_by_usage(by_usage)
        return None

    def get_texture_layers(
        self,
        by_usage: str | None = None,
    ) -> None | list[Layer]:
        """Get texture layers by usage.

        Arguments:
            by_usage (str, optional): Texture usage.

        Returns:
            None | list[Layer]: List of texture layers.
        """
        texture_component = self.get_texture_component()
        if not texture_component:
            return None
        if by_usage:
            return texture_component.get_layers_by_usage(by_usage)
        return None

    def previews(self) -> list[str]:
        """Get list of preview images.

        Returns:
            list[str]: List of preview images.
        """
        previews = []
        for component in self.components:
            try:
                previews.extend(component.previews())
            except Exception as e:
                self.logger.error(
                    "Error getting previews for component %s: %s",
                    component.__class__.__name__,
                    e,
                )
        return previews

    def pack(self, archive_path: str, remove_source: bool = True) -> str:
        """Pack map directory to zip archive.

        Arguments:
            archive_path (str): Path to the archive.
            remove_source (bool, optional): Remove source directory after packing.

        Returns:
            str: Path to the archive.
        """
        archive_path = shutil.make_archive(archive_path, "zip", self.map_directory)
        self.logger.debug("Map packed to %s.zip", archive_path)
        if remove_source:
            try:
                shutil.rmtree(self.map_directory)
                self.logger.debug("Map directory removed: %s", self.map_directory)
            except Exception as e:
                self.logger.debug("Error removing map directory %s: %s", self.map_directory, e)
        return archive_path

    def get_country_by_coordinates(self) -> str:
        """Get country name by coordinates.

        Returns:
            str: Country name.
        """
        try:
            geolocator = Nominatim(user_agent="maps4fs")
            location = geolocator.reverse(self.coordinates, language="en")
            if location and "country" in location.raw["address"]:
                return location.raw["address"]["country"]
        except Exception as e:
            self.logger.error("Error getting country name by coordinates: %s", e)
            return "Unknown"
        return "Unknown"
