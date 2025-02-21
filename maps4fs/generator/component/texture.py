"""Module with Texture class for generating textures for the map using OSM data."""

from __future__ import annotations

import json
import os
import shutil
import warnings
from collections import defaultdict
from typing import Any, Callable, Generator, Optional

import cv2
import numpy as np
import osmnx as ox
import pandas as pd
from osmnx import settings as ox_settings
from shapely import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from tqdm import tqdm

from maps4fs.generator.component.base.component_image import ImageComponent
from maps4fs.generator.component.layer import Layer

PREVIEW_MAXIMUM_SIZE = 2048


class Texture(ImageComponent):
    """Class which generates textures for the map using OSM data.

    Attributes:
        weights_dir (str): Path to the directory with weights.
        name (str): Name of the texture.
        tags (dict[str, str | list[str] | bool]): Dictionary of tags to search for.
        width (int | None): Width of the polygon in meters (only for LineString).
        color (tuple[int, int, int]): Color of the layer in BGR format.
    """

    def preprocess(self) -> None:
        """Preprocesses the data before the generation."""
        self.read_layers(self.get_schema())

        self._weights_dir = self.game.weights_dir_path(self.map_directory)
        self.procedural_dir = os.path.join(self._weights_dir, "masks")
        os.makedirs(self.procedural_dir, exist_ok=True)

        self.info_save_path = os.path.join(self.map_directory, "generation_info.json")
        self.info_layer_path = os.path.join(self.info_layers_directory, "textures.json")

    def read_layers(self, layers_schema: list[dict[str, Any]]) -> None:
        """Reads layers from the schema.

        Arguments:
            layers_schema (list[dict[str, Any]]): Schema with layers for textures.
        """
        try:
            self.layers = [Layer.from_json(layer) for layer in layers_schema]
            self.logger.debug("Loaded %s layers.", len(self.layers))
        except Exception as e:
            raise ValueError(f"Error loading texture layers: {e}") from e

    def get_schema(self) -> list[dict[str, Any]]:
        """Returns schema with layers for textures.

        Raises:
            FileNotFoundError: If the schema file is not found.
            ValueError: If there is an error loading the schema.
            ValueError: If the schema is not a list of dictionaries.

        Returns:
            dict[str, Any]: Schema with layers for textures.
        """
        custom_schema = self.kwargs.get("texture_custom_schema")
        if custom_schema:
            layers_schema = custom_schema
            self.logger.debug("Custom schema loaded with %s layers.", len(layers_schema))
        else:
            if not os.path.isfile(self.game.texture_schema):
                raise FileNotFoundError(
                    f"Texture layers schema not found: {self.game.texture_schema}"
                )

            try:
                with open(self.game.texture_schema, "r", encoding="utf-8") as f:
                    layers_schema = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error loading texture layers schema: {e}") from e

        if not isinstance(layers_schema, list):
            raise ValueError("Texture layers schema must be a list of dictionaries.")

        return layers_schema

    def get_base_layer(self) -> Layer | None:
        """Returns base layer.

        Returns:
            Layer | None: Base layer.
        """
        for layer in self.layers:
            if layer.priority == 0:
                return layer
        return None

    def get_background_layers(self) -> list[Layer]:
        """Returns list of background layers.

        Returns:
            list[Layer]: List of background layers.
        """
        return [layer for layer in self.layers if layer.background]

    def get_layer_by_usage(self, usage: str) -> Layer | None:
        """Returns layer by usage.

        Arguments:
            usage (str): Usage of the layer.

        Returns:
            Layer | None: Layer.
        """
        for layer in self.layers:
            if layer.usage == usage:
                return layer
        return None

    def get_layers_by_usage(self, usage: str) -> list[Layer]:
        """Returns layer by usage.

        Arguments:
            usage (str): Usage of the layer.

        Returns:
            list[Layer]: List of layers.
        """
        return [layer for layer in self.layers if layer.usage == usage]

    def process(self) -> None:
        """Processes the data to generate textures."""
        self._prepare_weights()
        self._read_parameters()
        self.draw()
        self.rotate_textures()
        self.add_borders()
        if self.map.texture_settings.dissolve and self.game.dissolve:
            self.dissolve()
        self.copy_procedural()

    def add_borders(self) -> None:
        """Iterates over all the layers and picks the one which have the border propety defined.
        Borders are distance from the edge of the map on each side (top, right, bottom, left).
        On the layers those pixels will be removed (value set to 0). If the base layer exist in
        the schema, those pixel values (not 0) will be added as 255 to the base layer."""
        base_layer = self.get_base_layer()
        base_layer_image = None
        if base_layer:
            base_layer_image = cv2.imread(base_layer.path(self._weights_dir), cv2.IMREAD_UNCHANGED)

        layers_with_borders = [layer for layer in self.layers if layer.border is not None]

        for layer in layers_with_borders:
            # Read the image.
            # Read pixels on borders with specified width (border property).
            # Where the pixel value is 255 - set it to 255 in base layer image.
            # And set it to 0 in the current layer image.
            layer_image = cv2.imread(layer.path(self._weights_dir), cv2.IMREAD_UNCHANGED)
            border = layer.border
            if not border:
                continue

            self.transfer_border(layer_image, base_layer_image, border)

            cv2.imwrite(layer.path(self._weights_dir), layer_image)
            self.logger.debug("Borders added to layer %s.", layer.name)

        if base_layer_image is not None:
            cv2.imwrite(base_layer.path(self._weights_dir), base_layer_image)  # type: ignore

    def copy_procedural(self) -> None:
        """Copies some of the textures to use them as mask for procedural generation.
        Creates an empty blockmask if it does not exist."""
        blockmask_path = os.path.join(self.procedural_dir, "BLOCKMASK.png")
        if not os.path.isfile(blockmask_path):
            self.logger.debug("BLOCKMASK.png not found, creating an empty file.")
            img = np.zeros((self.map_size, self.map_size), dtype=np.uint8)
            cv2.imwrite(blockmask_path, img)

        pg_layers_by_type = defaultdict(list)
        for layer in self.layers:
            if layer.procedural:
                # Get path to the original file.
                texture_path = layer.get_preview_or_path(self._weights_dir)
                for procedural_layer_name in layer.procedural:
                    pg_layers_by_type[procedural_layer_name].append(texture_path)

        if not pg_layers_by_type:
            self.logger.debug("No procedural layers found.")
            return

        for procedural_layer_name, texture_paths in pg_layers_by_type.items():
            procedural_save_path = os.path.join(self.procedural_dir, f"{procedural_layer_name}.png")
            if len(texture_paths) > 1:
                # If there are more than one texture, merge them.
                merged_texture = np.zeros((self.map_size, self.map_size), dtype=np.uint8)
                for texture_path in texture_paths:
                    texture = cv2.imread(texture_path, cv2.IMREAD_UNCHANGED)
                    merged_texture[texture == 255] = 255
                cv2.imwrite(procedural_save_path, merged_texture)
                self.logger.debug(
                    "Procedural file %s merged from %s textures.",
                    procedural_save_path,
                    len(texture_paths),
                )
            elif len(texture_paths) == 1:
                # Otherwise, copy the texture.
                shutil.copyfile(texture_paths[0], procedural_save_path)
                self.logger.debug(
                    "Procedural file %s copied from %s.", procedural_save_path, texture_paths[0]
                )

    def rotate_textures(self) -> None:
        """Rotates textures of the layers which have tags."""
        if self.rotation:
            # Iterate over the layers which have tags and rotate them.
            for layer in tqdm(self.layers, desc="Rotating textures", unit="layer"):
                if layer.tags or layer.precise_tags:
                    self.logger.debug("Rotating layer %s.", layer.name)
                    layer_paths = layer.paths(self._weights_dir)
                    layer_paths += [layer.path_preview(self._weights_dir)]
                    for layer_path in layer_paths:
                        if os.path.isfile(layer_path):
                            self.rotate_image(
                                layer_path,
                                self.rotation,
                                output_height=self.map_size,
                                output_width=self.map_size,
                            )
                else:
                    self.logger.debug(
                        "Skipping rotation of layer %s because it has no tags.", layer.name
                    )

    def _read_parameters(self) -> None:
        """Reads map parameters from OSM data, such as:
        - minimum and maximum coordinates
        """
        bbox = ox.utils_geo.bbox_from_point(self.coordinates, dist=self.map_rotated_size / 2)
        self.minimum_x, self.minimum_y, self.maximum_x, self.maximum_y = bbox

    def info_sequence(self) -> dict[str, Any]:
        """Returns the JSON representation of the generation info for textures."""
        useful_attributes = [
            "coordinates",
            "bbox",
            "map_size",
            "rotation",
            "minimum_x",
            "minimum_y",
            "maximum_x",
            "maximum_y",
        ]
        return {attr: getattr(self, attr, None) for attr in useful_attributes}

    def _prepare_weights(self):
        self.logger.debug("Starting preparing weights from %s layers.", len(self.layers))

        for layer in tqdm(self.layers, desc="Preparing weights", unit="layer"):
            self._generate_weights(layer)
        self.logger.debug("Prepared weights for %s layers.", len(self.layers))

    def _generate_weights(self, layer: Layer) -> None:
        """Generates weight files for textures. Each file is a numpy array of zeros and
            dtype uint8 (0-255).

        Arguments:
            layer (Layer): Layer with textures and tags.
        """
        if layer.tags is None and layer.precise_tags is None:
            size = (self.map_size, self.map_size)
        else:
            size = (self.map_rotated_size, self.map_rotated_size)
        postfix = "_weight.png" if not layer.exclude_weight else ".png"
        if layer.count == 0:
            filepaths = [os.path.join(self._weights_dir, layer.name + postfix)]
        else:
            filepaths = [
                os.path.join(self._weights_dir, layer.name + str(i).zfill(2) + postfix)
                for i in range(1, layer.count + 1)
            ]

        for filepath in filepaths:
            img = np.zeros(size, dtype=np.uint8)
            cv2.imwrite(filepath, img)

    @property
    def layers(self) -> list[Layer]:
        """Returns list of layers with textures and tags from textures.json.

        Returns:
            list[Layer]: List of layers.
        """
        return self._layers

    @layers.setter
    def layers(self, layers: list[Layer]) -> None:
        """Sets list of layers with textures and tags.

        Arguments:
            layers (list[Layer]): List of layers.
        """
        self._layers = layers

    def layers_by_priority(self) -> list[Layer]:
        """Returns list of layers sorted by priority: None priority layers are first,
        then layers are sorted by priority (descending).

        Returns:
            list[Layer]: List of layers sorted by priority.
        """
        return sorted(
            self.layers,
            key=lambda _layer: (
                _layer.priority is not None,
                -_layer.priority if _layer.priority is not None else float("inf"),
            ),
        )

    def draw(self) -> None:
        """Iterates over layers and fills them with polygons from OSM data."""
        layers = self.layers_by_priority()
        layers = [
            layer for layer in layers if layer.tags is not None or layer.precise_tags is not None
        ]

        cumulative_image = None

        # Dictionary to store info layer data.
        # Key is a layer.info_layer, value is a list of polygon points as tuples (x, y).
        info_layer_data: dict[str, list[list[int]]] = defaultdict(list)

        for layer in tqdm(layers, desc="Drawing textures", unit="layer"):
            if self.map.texture_settings.skip_drains and layer.usage == "drain":
                self.logger.debug("Skipping layer %s because of the usage.", layer.name)
                continue
            if layer.priority == 0:
                self.logger.debug(
                    "Found base layer %s. Postponing that to be the last layer drawn.", layer.name
                )
                continue
            layer_path = layer.path(self._weights_dir)
            self.logger.debug("Drawing layer %s.", layer_path)
            layer_image = cv2.imread(layer_path, cv2.IMREAD_UNCHANGED)
            self.logger.info(
                "Layer %s loaded. Shape: %s, dtype: %s.",
                layer.name,
                layer_image.shape,
                layer_image.dtype,
            )

            if cumulative_image is None:
                self.logger.debug("First layer, creating new cumulative image.")
                cumulative_image = layer_image

            mask = cv2.bitwise_not(cumulative_image)
            self._draw_layer(layer, info_layer_data, layer_image)
            self._add_roads(layer, info_layer_data)
            self.logger.info(
                "Layer %s drawn. Shape of the mask: %s, dtype: %s.",
                layer.name,
                mask.shape,
                mask.dtype,
            )

            output_image = cv2.bitwise_and(layer_image, mask)
            cumulative_image = cv2.bitwise_or(cumulative_image, output_image)

            cv2.imwrite(layer_path, output_image)
            self.logger.debug("Texture %s saved.", layer_path)

        # Save info layer data.
        if os.path.isfile(self.info_layer_path):
            self.logger.debug(
                "File %s already exists, will update to avoid overwriting.", self.info_layer_path
            )
            with open(self.info_layer_path, "r", encoding="utf-8") as f:
                info_layer_data.update(json.load(f))

        with open(self.info_layer_path, "w", encoding="utf-8") as f:
            json.dump(info_layer_data, f, ensure_ascii=False, indent=4)
            self.logger.debug("Info layer data saved to %s.", self.info_layer_path)

        if cumulative_image is not None:
            self.draw_base_layer(cumulative_image)

    def _draw_layer(
        self, layer: Layer, info_layer_data: dict[str, list[list[int]]], layer_image: np.ndarray
    ) -> None:
        """Draws polygons from OSM data on the layer image and updates the info layer data.

        Arguments:
            layer (Layer): Layer with textures and tags.
            info_layer_data (dict[list[list[int]]]): Dictionary to store info layer data.
            layer_image (np.ndarray): Layer image.
        """
        tags = layer.tags
        if self.map.texture_settings.use_precise_tags:
            if layer.precise_tags:
                self.logger.debug(
                    "Using precise tags: %s for layer %s.", layer.precise_tags, layer.name
                )
                tags = layer.precise_tags

        if tags is None:
            return

        for polygon in self.objects_generator(tags, layer.width, layer.info_layer):
            if not len(polygon) > 2:
                self.logger.debug("Skipping polygon with less than 3 points.")
                continue
            if layer.info_layer:
                info_layer_data[layer.info_layer].append(
                    self.np_to_polygon_points(polygon)  # type: ignore
                )
            if not layer.invisible:
                try:
                    cv2.fillPoly(layer_image, [polygon], color=255)  # type: ignore
                except Exception as e:
                    self.logger.warning("Error drawing polygon: %s.", repr(e))
                    continue

    def _add_roads(self, layer: Layer, info_layer_data: dict[str, list[list[int]]]) -> None:
        """Adds roads to the info layer data.

        Arguments:
            layer (Layer): Layer with textures and tags.
            info_layer_data (dict[list[list[int]]]): Dictionary to store info layer data.
        """
        if layer.info_layer == "roads":
            for linestring in self.objects_generator(
                layer.tags, layer.width, layer.info_layer, yield_linestrings=True
            ):
                linestring_entry = {
                    "points": linestring,
                    "tags": str(layer.tags),
                }
                info_layer_data[f"{layer.info_layer}_polylines"].append(linestring_entry)  # type: ignore

    def dissolve(self) -> None:
        """Dissolves textures of the layers with tags into sublayers for them to look more
        natural in the game.
        Iterates over all layers with tags and reads the first texture, checks if the file
        contains any non-zero values (255), splits those non-values between different weight
        files of the corresponding layer and saves the changes to the files.
        """
        for layer in tqdm(self.layers, desc="Dissolving textures", unit="layer"):
            if not layer.tags:
                self.logger.debug("Layer %s has no tags, there's nothing to dissolve.", layer.name)
                continue
            layer_path = layer.path(self._weights_dir)
            layer_paths = layer.paths(self._weights_dir)

            if len(layer_paths) < 2:
                self.logger.debug("Layer %s has only one texture, skipping.", layer.name)
                continue

            self.logger.debug("Dissolving layer from %s to %s.", layer_path, layer_paths)

            # Check if the image contains any non-zero values, otherwise continue.
            layer_image = cv2.imread(layer_path, cv2.IMREAD_UNCHANGED)

            if not np.any(layer_image):
                self.logger.debug(
                    "Layer %s does not contain any non-zero values, skipping.", layer.name
                )
                continue

            # Save the original image to use it for preview later, without combining the sublayers.
            cv2.imwrite(layer.path_preview(self._weights_dir), layer_image.copy())

            # Get the coordinates of non-zero values.
            non_zero_coords = np.column_stack(np.where(layer_image > 0))

            # Prepare sublayers.
            sublayers = [np.zeros_like(layer_image) for _ in range(layer.count)]

            # Randomly assign non-zero values to sublayers.
            for coord in non_zero_coords:
                sublayers[np.random.randint(0, layer.count)][coord[0], coord[1]] = 255

            # Save the sublayers.
            for sublayer, sublayer_path in zip(sublayers, layer_paths):
                cv2.imwrite(sublayer_path, sublayer)
                self.logger.debug("Sublayer %s saved.", sublayer_path)

            self.logger.debug("Dissolved layer %s.", layer.name)

    def draw_base_layer(self, cumulative_image: np.ndarray) -> None:
        """Draws base layer and saves it into the png file.
        Base layer is the last layer to be drawn, it fills the remaining area of the map.

        Arguments:
            cumulative_image (np.ndarray): Cumulative image with all layers.
        """
        base_layer = self.get_base_layer()
        if base_layer is not None:
            layer_path = base_layer.path(self._weights_dir)
            self.logger.debug("Drawing base layer %s.", layer_path)
            img = cv2.bitwise_not(cumulative_image)
            cv2.imwrite(layer_path, img)
            self.logger.debug("Base texture %s saved.", layer_path)

    def latlon_to_pixel(self, lat: float, lon: float) -> tuple[int, int]:
        """Converts latitude and longitude to pixel coordinates.

        Arguments:
            lat (float): Latitude.
            lon (float): Longitude.

        Returns:
            tuple[int, int]: Pixel coordinates.
        """
        x = int((lon - self.minimum_x) / (self.maximum_x - self.minimum_x) * self.map_rotated_size)
        y = int((lat - self.maximum_y) / (self.minimum_y - self.maximum_y) * self.map_rotated_size)
        return x, y

    def np_to_polygon_points(self, np_array: np.ndarray) -> list[tuple[int, int]]:
        """Converts numpy array of polygon points to list of tuples.

        Arguments:
            np_array (np.ndarray): Numpy array of polygon points.

        Returns:
            list[tuple[int, int]]: List of tuples.
        """
        return [(int(x), int(y)) for x, y in np_array.reshape(-1, 2)]

    def _to_np(self, geometry: Polygon, *args) -> np.ndarray:
        """Converts Polygon geometry to numpy array of polygon points.

        Arguments:
            geometry (Polygon): Polygon geometry.
            *Arguments: Additional arguments:
                - width (int | None): Width of the polygon in meters.

        Returns:
            np.ndarray: Numpy array of polygon points.
        """
        coords = list(geometry.exterior.coords)
        pts = np.array(coords, np.int32)
        pts = pts.reshape((-1, 1, 2))
        return pts

    def _to_polygon(self, obj: pd.core.series.Series, width: int | None) -> Polygon:
        """Converts OSM object to numpy array of polygon points and converts coordinates to pixels.

        Arguments:
            obj (pd.core.series.Series): OSM object.
            width (int | None): Width of the polygon in meters.

        Returns:
            Polygon: Polygon geometry with pixel coordinates.
        """
        geometry = obj["geometry"]
        geometry_type = geometry.geom_type
        converter = self._converters(geometry_type)
        if not converter:
            self.logger.debug("Geometry type %s not supported.", geometry_type)
            return None
        return converter(geometry, width)

    def polygon_to_pixel_coordinates(self, polygon: Polygon) -> Polygon:
        """Converts polygon coordinates from lat lon to pixel coordinates.

        Arguments:
            polygon (Polygon): Polygon geometry.

        Returns:
            Polygon: Polygon geometry.
        """
        coords_pixel = [
            self.latlon_to_pixel(lat, lon) for lon, lat in list(polygon.exterior.coords)
        ]
        return Polygon(coords_pixel)

    def linestring_to_pixel_coordinates(self, linestring: LineString) -> LineString:
        """Converts LineString coordinates from lat lon to pixel coordinates.

        Arguments:
            linestring (LineString): LineString geometry.

        Returns:
            LineString: LineString geometry.
        """
        coords_pixel = [self.latlon_to_pixel(lat, lon) for lon, lat in list(linestring.coords)]
        return LineString(coords_pixel)

    def point_to_pixel_coordinates(self, point: Point) -> Point:
        """Converts Point coordinates from lat lon to pixel coordinates.

        Arguments:
            point (Point): Point geometry.

        Returns:
            Point: Point geometry.
        """
        x, y = self.latlon_to_pixel(point.y, point.x)
        return Point(x, y)

    def _to_pixel(self, geometry: Polygon, *args, **kwargs) -> Polygon:
        """Returns the same geometry with pixel coordinates.

        Arguments:
            geometry (Polygon): Polygon geometry.

        Returns:
            Polygon: Polygon geometry with pixel coordinates.
        """
        return self.polygon_to_pixel_coordinates(geometry)

    def _sequence_to_pixel(
        self,
        geometry: LineString | Point,
        width: int | None,
    ) -> Polygon:
        """Converts LineString or Point geometry to numpy array of polygon points.

        Arguments:
            geometry (LineString | Point): LineString or Point geometry.
            width (int | None): Width of the polygon in meters.

        Raises:
            ValueError: If the geometry type is not supported

        Returns:
            Polygon: Polygon geometry.
        """
        if isinstance(geometry, LineString):
            geometry = self.linestring_to_pixel_coordinates(geometry)
        elif isinstance(geometry, Point):
            geometry = self.point_to_pixel_coordinates(geometry)
        else:
            raise ValueError(f"Geometry type {type(geometry)} not supported.")

        return geometry.buffer(width if width else 0)

    def _converters(
        self, geom_type: str
    ) -> Optional[Callable[[BaseGeometry, Optional[int]], np.ndarray]]:
        """Returns a converter function for a given geometry type.

        Arguments:
            geom_type (str): Geometry type.

        Returns:
            Callable[[shapely.geometry, int | None], np.ndarray]: Converter function.
        """
        converters = {
            "Polygon": self._to_pixel,
            "LineString": self._sequence_to_pixel,
            "Point": self._sequence_to_pixel,
        }
        return converters.get(geom_type)  # type: ignore

    def objects_generator(
        self,
        tags: dict[str, str | list[str] | bool] | None,
        width: int | None,
        info_layer: str | None = None,
        yield_linestrings: bool = False,
    ) -> Generator[np.ndarray, None, None] | Generator[list[tuple[int, int]], None, None]:
        """Generator which yields numpy arrays of polygons from OSM data.

        Arguments:
            tags (dict[str, str | list[str]]): Dictionary of tags to search for.
            width (int | None): Width of the polygon in meters (only for LineString).
            info_layer (str | None): Name of the corresponding info layer.
            yield_linestrings (bool): Flag to determine if the LineStrings should be yielded.

        Yields:
            Generator[np.ndarray, None, None] | Generator[list[tuple[int, int]], None, None]:
                Numpy array of polygon points or list of point coordinates.
        """
        if tags is None:
            return
        is_fieds = info_layer == "fields"

        ox_settings.use_cache = self.map.texture_settings.use_cache
        ox_settings.requests_timeout = 30

        try:
            if self.map.custom_osm is not None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", FutureWarning)
                    objects = ox.features_from_xml(self.map.custom_osm, tags=tags)
            else:
                objects = ox.features_from_bbox(bbox=self.new_bbox, tags=tags)
        except Exception as e:
            self.logger.debug("Error fetching objects for tags: %s. Error: %s.", tags, e)
            return
        self.logger.debug("Fetched %s elements for tags: %s.", len(objects), tags)

        method = self.linestrings_generator if yield_linestrings else self.polygons_generator

        yield from method(objects, width, is_fieds)

    def linestrings_generator(
        self, objects: pd.core.frame.DataFrame, *args, **kwargs
    ) -> Generator[list[tuple[int, int]], None, None]:
        """Generator which yields lists of point coordinates which represent LineStrings from OSM.

        Arguments:
            objects (pd.core.frame.DataFrame): Dataframe with OSM objects.

        Yields:
            Generator[list[tuple[int, int]], None, None]: List of point coordinates.
        """
        for _, obj in objects.iterrows():
            geometry = obj["geometry"]
            if isinstance(geometry, LineString):
                points = [self.latlon_to_pixel(x, y) for y, x in geometry.coords]
                yield points

    def polygons_generator(
        self, objects: pd.core.frame.DataFrame, width: int | None, is_fieds: bool
    ) -> Generator[np.ndarray, None, None]:
        """Generator which yields numpy arrays of polygons from OSM data.

        Arguments:
            objects (pd.core.frame.DataFrame): Dataframe with OSM objects.
            width (int | None): Width of the polygon in meters (only for LineString).
            is_fieds (bool): Flag to determine if the fields should be padded.

        Yields:
            Generator[np.ndarray, None, None]: Numpy array of polygon points.
        """
        for _, obj in objects.iterrows():
            try:
                polygon = self._to_polygon(obj, width)
            except Exception as e:
                self.logger.warning("Error converting object to polygon: %s.", e)
                continue
            if polygon is None:
                continue

            if is_fieds and self.map.texture_settings.fields_padding > 0:
                padded_polygon = polygon.buffer(-self.map.texture_settings.fields_padding)

                if not isinstance(padded_polygon, Polygon) or not list(
                    padded_polygon.exterior.coords
                ):
                    self.logger.debug("The padding value is too high, field will not padded.")
                else:
                    polygon = padded_polygon

            polygon_np = self._to_np(polygon)
            yield polygon_np

    def previews(self) -> list[str]:
        """Invokes methods to generate previews. Returns list of paths to previews.

        Returns:
            list[str]: List of paths to previews.
        """
        preview_paths = []
        preview_paths.append(self._osm_preview())
        return preview_paths

    def _osm_preview(self) -> str:
        """Merges layers into one image and saves it into the png file.

        Returns:
            str: Path to the preview.
        """
        scaling_factor = PREVIEW_MAXIMUM_SIZE / self.map_size

        preview_size = (
            int(self.map_size * scaling_factor),
            int(self.map_size * scaling_factor),
        )
        self.logger.debug(
            "Scaling factor: %s. Preview size: %s.",
            scaling_factor,
            preview_size,
        )

        active_layers = [
            layer
            for layer in self.layers
            if layer.tags is not None or layer.precise_tags is not None
        ]
        self.logger.debug("Following layers have tag textures: %s.", len(active_layers))

        images = [
            cv2.resize(
                cv2.imread(layer.get_preview_or_path(self._weights_dir), cv2.IMREAD_UNCHANGED),
                preview_size,
            )
            for layer in active_layers
        ]
        colors = [layer.color for layer in active_layers]
        color_images = []
        for img, color in zip(images, colors):
            color_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
            color_img[img > 0] = color
            color_images.append(color_img)
        merged = np.sum(color_images, axis=0, dtype=np.uint8)
        self.logger.debug(
            "Merged layers into one image. Shape: %s, dtype: %s.",
            merged.shape,
            merged.dtype,
        )
        preview_path = os.path.join(self.previews_directory, "textures_osm.png")

        cv2.imwrite(preview_path, merged)  # type: ignore
        self.logger.debug("Preview saved to %s.", preview_path)
        return preview_path
