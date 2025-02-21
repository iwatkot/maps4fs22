"""This module contains the Config class for map settings and configuration."""

from __future__ import annotations

import json
import os
from random import choice, randint, uniform
from typing import Generator
from xml.etree import ElementTree as ET

import cv2
import numpy as np
from tqdm import tqdm

from maps4fs.generator.component.base.component_xml import XMLComponent
from maps4fs.generator.settings import Parameters

NODE_ID_STARTING_VALUE = 2000
SPLINES_NODE_ID_STARTING_VALUE = 5000
TREE_NODE_ID_STARTING_VALUE = 10000

FIELDS_ATTRIBUTES = [
    ("angle", "integer", "0"),
    ("missionAllowed", "boolean", "true"),
    ("missionOnlyGrass", "boolean", "false"),
    ("nameIndicatorIndex", "string", "1"),
    ("polygonIndex", "string", "0"),
    ("teleportIndicatorIndex", "string", "2"),
]


class I3d(XMLComponent):
    """Component for map i3d file settings and configuration.

    Arguments:
        game (Game): The game instance for which the map is generated.
        coordinates (tuple[float, float]): The latitude and longitude of the center of the map.
        map_size (int): The size of the map in pixels.
        map_rotated_size (int): The size of the map in pixels after rotation.
        rotation (int): The rotation angle of the map.
        map_directory (str): The directory where the map files are stored.
        logger (Any, optional): The logger to use. Must have at least three basic methods: debug,
            info, warning. If not provided, default logging will be used.
    """

    def preprocess(self) -> None:
        """Gets the path to the map I3D file from the game instance and saves it to the instance
        attribute. If the game does not support I3D files, the attribute is set to None."""
        self.xml_path = self.game.i3d_file_path(self.map_directory)

    def process(self) -> None:
        """Updates the map I3D file and creates splines in a separate I3D file."""
        self.update_height_scale()

        self._update_parameters()

        if self.game.i3d_processing:
            self._add_fields()

            if self.map.i3d_settings.add_trees:
                self._add_forests()
            self._add_splines()

    def update_height_scale(self, value: int | None = None) -> None:
        """Updates the height scale value in the map I3D file.
        If the value is not provided, the method checks if the shared settings are set to change
        the height scale and if the height scale value is set. If not, the method returns without
        updating the height scale.

        Arguments:
            value (int, optional): The height scale value.
        """
        if not value:
            if (
                self.map.shared_settings.change_height_scale
                and self.map.shared_settings.height_scale_value
            ):
                value = int(self.map.shared_settings.height_scale_value)
            else:
                return

        tree = self.get_tree()
        root = tree.getroot()
        path = ".//Scene/TerrainTransformGroup"

        data = {"heightScale": str(value)}

        self.get_and_update_element(root, path, data)
        self.save_tree(tree)

    def _update_parameters(self) -> None:
        """Updates the map I3D file with the  sun bounding box and displacement layer size."""

        tree = self.get_tree()
        root = tree.getroot()

        sun_element_path = ".//Scene/Light[@name='sun']"
        distance = self.map_size // 2
        data = {
            "lastShadowMapSplitBboxMin": f"-{distance},-128,-{distance}",
            "lastShadowMapSplitBboxMax": f"{distance},148,{distance}",
        }

        self.get_and_update_element(root, sun_element_path, data)

        displacement_layer_path = ".//Scene/TerrainTransformGroup/Layers/DisplacementLayer"
        data = {"size": str(int(self.map_size * 8))}
        self.get_and_update_element(root, displacement_layer_path, data)

        self.save_tree(tree)

    def _add_splines(self) -> None:
        """Adds splines to the map I3D file."""
        splines_i3d_path = self.game.splines_file_path(self.map_directory)
        if not os.path.isfile(splines_i3d_path):
            self.logger.warning("Splines I3D file not found: %s.", splines_i3d_path)
            return

        tree = self.get_tree(splines_i3d_path)

        roads_polylines = self.get_infolayer_data(Parameters.TEXTURES, Parameters.ROADS_POLYLINES)
        if not roads_polylines:
            self.logger.warning("Roads polylines data not found in textures info layer.")
            return

        root = tree.getroot()
        # Find <Shapes> element in the I3D file.
        shapes_node = root.find(".//Shapes")
        # Find <Scene> element in the I3D file.
        scene_node = root.find(".//Scene")

        if shapes_node is None or scene_node is None:
            self.logger.warning("Shapes or Scene node not found in I3D file.")
            return

        not_resized_dem = self.get_not_resized_dem()
        if not_resized_dem is None:
            self.logger.warning("Not resized DEM not found.")
            return

        user_attributes_node = root.find(".//UserAttributes")
        if user_attributes_node is None:
            self.logger.warning("UserAttributes node not found in I3D file.")
            return

        node_id = SPLINES_NODE_ID_STARTING_VALUE
        for road_id, road_info in enumerate(roads_polylines, start=1):
            points = road_info.get("points")
            tags = road_info.get("tags")

            try:
                fitted_road = self.fit_object_into_bounds(
                    linestring_points=points, angle=self.rotation
                )
            except ValueError as e:
                self.logger.debug(
                    "Road %s could not be fitted into the map bounds with error: %s",
                    road_id,
                    e,
                )
                continue

            fitted_road = self.interpolate_points(
                fitted_road, num_points=self.map.spline_settings.spline_density
            )
            fitted_roads = [(fitted_road, "original")]

            if self.map.spline_settings.add_reversed_splines:
                reversed_fitted_road = fitted_road[::-1]
                fitted_roads.append((reversed_fitted_road, "reversed"))

            for fitted_road, direction in fitted_roads:
                spline_name = f"spline_{road_id}_{direction}_{tags}"

                data = {
                    "name": spline_name,
                    "translation": "0 0 0",
                    "nodeId": str(node_id),
                    "shapeId": str(node_id),
                }

                scene_node.append(self.create_element("Shape", data))

                road_ccs = [self.top_left_coordinates_to_center(point) for point in fitted_road]

                data = {
                    "name": spline_name,
                    "shapeId": str(node_id),
                    "degree": "3",
                    "form": "open",
                }
                nurbs_curve_node = self.create_element("NurbsCurve", data)

                for point_ccs, point in zip(road_ccs, fitted_road):
                    cx, cy = point_ccs
                    x, y = point

                    z = self.get_z_coordinate_from_dem(not_resized_dem, x, y)

                    nurbs_curve_node.append(self.create_element("cv", {"c": f"{cx}, {z}, {cy}"}))

                shapes_node.append(nurbs_curve_node)

                user_attribute_node = self.get_user_attribute_node(
                    node_id,
                    attributes=[
                        ("maxSpeedScale", "integer", "1"),
                        ("speedLimit", "integer", "100"),
                    ],
                )

                user_attributes_node.append(user_attribute_node)
                node_id += 1

        tree.write(splines_i3d_path)  # type: ignore
        self.logger.debug("Splines I3D file saved to: %s.", splines_i3d_path)

    def _add_fields(self) -> None:
        """Adds fields to the map I3D file."""
        tree = self.get_tree()

        border = 0
        fields_layer = self.map.get_texture_layer(by_usage=Parameters.FIELD)
        if fields_layer and fields_layer.border:
            border = fields_layer.border

        fields = self.get_infolayer_data(Parameters.TEXTURES, Parameters.FIELDS)
        if not fields:
            self.logger.warning("Fields data not found in textures info layer.")
            return

        self.logger.debug("Found %s fields in textures info layer.", len(fields))
        self.logger.debug("Starging to add fields to the I3D file.")

        root = tree.getroot()
        gameplay_node = root.find(".//TransformGroup[@name='gameplay']")

        if gameplay_node is None:
            return
        fields_node = gameplay_node.find(".//TransformGroup[@name='fields']")
        user_attributes_node = root.find(".//UserAttributes")

        if fields_node is None or user_attributes_node is None:
            return

        node_id = NODE_ID_STARTING_VALUE
        field_id = 1

        for field in tqdm(fields, desc="Adding fields", unit="field"):
            try:
                fitted_field = self.fit_object_into_bounds(
                    polygon_points=field, angle=self.rotation, border=border
                )
            except ValueError as e:
                self.logger.debug(
                    "Field %s could not be fitted into the map bounds with error: %s",
                    field_id,
                    e,
                )
                continue

            field_ccs = [self.top_left_coordinates_to_center(point) for point in fitted_field]

            field_node, updated_node_id = self._get_field_xml_entry(field_id, field_ccs, node_id)
            if field_node is None:
                continue
            user_attributes_node.append(
                self.get_user_attribute_node(node_id, attributes=FIELDS_ATTRIBUTES)
            )
            node_id = updated_node_id

            # Adding the field node to the fields node.
            fields_node.append(field_node)
            self.logger.debug("Field %s added to the I3D file.", field_id)

            node_id += 1
            field_id += 1

        self.save_tree(tree)

    def _get_field_xml_entry(
        self, field_id: int, field_ccs: list[tuple[int, int]], node_id: int
    ) -> tuple[ET.Element, int] | tuple[None, int]:
        """Creates an XML entry for the field with given field ID and field coordinates.

        Arguments:
            field_id (int): The ID of the field.
            field_ccs (list[tuple[int, int]]): The coordinates of the field polygon points
                in the center coordinate system.
            node_id (int): The node ID of the field node.

        Returns:
            tuple[ET.Element, int] | tuple[None, int]: The field node and the updated node ID or
                None and the node ID.
        """
        try:
            cx, cy = self.get_polygon_center(field_ccs)
        except Exception as e:
            self.logger.debug("Field %s could not be fitted into the map bounds.", field_id)
            self.logger.debug("Error: %s", e)
            return None, node_id

        # Creating the main field node.
        data = {
            "name": f"field{field_id}",
            "translation": f"{cx} 0 {cy}",
            "nodeId": str(node_id),
        }
        field_node = self.create_element("TransformGroup", data)
        node_id += 1

        # Creating the polygon points node, which contains the points of the field.
        polygon_points_node = self.create_element(
            "TransformGroup", {"name": "polygonPoints", "nodeId": str(node_id)}
        )
        node_id += 1

        for point_id, point in enumerate(field_ccs, start=1):
            rx, ry = self.absolute_to_relative(point, (cx, cy))

            node_id += 1
            point_node = self.create_element(
                "TransformGroup",
                {
                    "name": f"point{point_id}",
                    "translation": f"{rx} 0 {ry}",
                    "nodeId": str(node_id),
                },
            )

            polygon_points_node.append(point_node)

        field_node.append(polygon_points_node)

        # Adding the name indicator node to the field node.
        name_indicator_node, node_id = self._get_name_indicator_node(node_id, field_id)
        field_node.append(name_indicator_node)

        node_id += 1
        field_node.append(
            self.create_element(
                "TransformGroup", {"name": "teleportIndicator", "nodeId": str(node_id)}
            )
        )

        return field_node, node_id

    def _get_name_indicator_node(self, node_id: int, field_id: int) -> tuple[ET.Element, int]:
        """Creates a name indicator node with given node ID and field ID.

        Arguments:
            node_id (int): The node ID of the name indicator node.
            field_id (int): The ID of the field.

        Returns:
            tuple[ET.Element, int]: The name indicator node and the updated node ID.
        """
        node_id += 1
        name_indicator_node = self.create_element(
            "TransformGroup", {"name": "nameIndicator", "nodeId": str(node_id)}
        )

        node_id += 1
        data = {
            "name": "Note",
            "nodeId": str(node_id),
            "text": f"field{field_id}&#xA;0.00 ha",
            "color": "4278190080",
            "fixedSize": "true",
        }
        note_node = self.create_element("Note", data)
        name_indicator_node.append(note_node)

        return name_indicator_node, node_id

    def get_user_attribute_node(
        self, node_id: int, attributes: list[tuple[str, str, str]]
    ) -> ET.Element:
        """Creates an XML user attribute node with given node ID.

        Arguments:
            node_id (int): The node ID of the user attribute node.
            attributes (list[tuple[str, str, str]]): The list of attributes to add to the node.

        Returns:
            ET.Element: The created user attribute node.
        """
        user_attribute_node = ET.Element("UserAttribute")
        user_attribute_node.set("nodeId", str(node_id))

        for name, attr_type, value in attributes:
            data = {
                "name": name,
                "type": attr_type,
                "value": value,
            }
            user_attribute_node.append(self.create_element("Attribute", data))

        return user_attribute_node

    def _read_tree_schema(self) -> list[dict[str, str]] | None:
        """Reads the tree schema from the game instance or from the custom schema.

        Returns:
            list[dict[str, int | str]] | None: The tree schema or None if the schema could not be
                read.
        """
        custom_schema = self.kwargs.get("tree_custom_schema")
        if custom_schema:
            tree_schema = custom_schema
        else:
            try:
                tree_schema_path = self.game.tree_schema
            except ValueError:
                self.logger.warning("Tree schema path not set for the Game %s.", self.game.code)
                return None

            if not os.path.isfile(tree_schema_path):
                self.logger.warning("Tree schema file was not found: %s.", tree_schema_path)
                return None

            try:
                with open(tree_schema_path, "r", encoding="utf-8") as tree_schema_file:
                    tree_schema = json.load(tree_schema_file)  # type: ignore
            except json.JSONDecodeError as e:
                self.logger.warning(
                    "Could not load tree schema from %s with error: %s", tree_schema_path, e
                )
                return None

        return tree_schema  # type: ignore

    def _get_random_tree(
        self, tree_schema: list[dict[str, str]], leaf_type: str | None = None
    ) -> dict[str, str]:
        """Gets a random tree from the tree schema.
        If the leaf type is provided, the method tries to get a tree with the same leaf type.

        Arguments:
            tree_schema (list[dict[str, str]]): The tree schema.
            leaf_type (str, optional): The leaf type of the tree. Defaults to None.

        Returns:
            dict[str, str]: The random tree from the schema
        """
        if not leaf_type:
            return choice(tree_schema)

        try:
            leaf_type = leaf_type.split("_")[0]
        except IndexError:
            return choice(tree_schema)

        if leaf_type == "mixed":
            trees_with_leaf_type = [tree for tree in tree_schema if tree.get("leaf_type")]
            return choice(trees_with_leaf_type)

        trees_by_leaf_type = [tree for tree in tree_schema if tree.get("leaf_type") == leaf_type]
        if not trees_by_leaf_type:
            return choice(tree_schema)

        return choice(trees_by_leaf_type)

    def _add_forests(self) -> None:
        """Adds forests to the map I3D file."""
        tree_schema = self._read_tree_schema()
        if not tree_schema:
            return

        if self.map.texture_settings.use_precise_tags:
            forest_layers = self.map.get_texture_layers(by_usage=Parameters.FOREST)
        else:
            layer = self.map.get_texture_layer(by_usage=Parameters.FOREST)
            forest_layers = [layer] if layer else []
        if not forest_layers:
            self.logger.warning("Forest layer not found.")
            return

        node_id = TREE_NODE_ID_STARTING_VALUE

        for forest_layer in forest_layers:
            weights_directory = self.game.weights_dir_path(self.map_directory)
            forest_image_path = forest_layer.get_preview_or_path(weights_directory)

            if not forest_image_path or not os.path.isfile(forest_image_path):
                self.logger.warning("Forest image not found.")
                continue

            tree = self.get_tree()
            root = tree.getroot()
            scene_node = root.find(".//Scene")
            if scene_node is None:
                self.logger.warning("Scene element not found in I3D file.")
                return

            trees_node = self.create_element(
                "TransformGroup",
                {
                    "name": "trees",
                    "translation": "0 0 0",
                    "nodeId": str(node_id),
                },
            )
            node_id += 1

            not_resized_dem = self.get_not_resized_dem()
            if not_resized_dem is None:
                self.logger.warning("Not resized DEM not found.")
                return

            forest_image = cv2.imread(forest_image_path, cv2.IMREAD_UNCHANGED)
            for x, y in self.non_empty_pixels(
                forest_image, step=self.map.i3d_settings.forest_density
            ):
                shifted_x, shifted_y = self.randomize_coordinates(
                    (x, y),
                    self.map.i3d_settings.forest_density,
                    self.map.i3d_settings.trees_relative_shift,
                )

                shifted_x, shifted_y = int(shifted_x), int(shifted_y)

                z = self.get_z_coordinate_from_dem(not_resized_dem, shifted_x, shifted_y)

                xcs, ycs = self.top_left_coordinates_to_center((shifted_x, shifted_y))
                node_id += 1

                rotation = randint(-180, 180)

                random_tree = self._get_random_tree(tree_schema, forest_layer.precise_usage)
                tree_name = random_tree["name"]
                tree_id = random_tree["reference_id"]

                data = {
                    "name": tree_name,
                    "translation": f"{xcs} {z} {ycs}",
                    "rotation": f"0 {rotation} 0",
                    "referenceId": str(tree_id),
                    "nodeId": str(node_id),
                }
                trees_node.append(self.create_element("ReferenceNode", data))

            scene_node.append(trees_node)
            self.save_tree(tree)

    @staticmethod
    def randomize_coordinates(
        coordinates: tuple[int, int], density: int, shift_percent: int
    ) -> tuple[float, float]:
        """Randomizes the coordinates of the point with the given density.

        Arguments:
            coordinates (tuple[int, int]): The coordinates of the point.
            density (int): The density of the randomization.
            shift_percent (int): Maximum relative shift in percent.

        Returns:
            tuple[float, float]: The randomized coordinates of the point.
        """
        shift_range = density * shift_percent / 100

        x_shift = uniform(-shift_range, shift_range)
        y_shift = uniform(-shift_range, shift_range)

        x, y = coordinates

        return x + x_shift, y + y_shift

    @staticmethod
    def non_empty_pixels(
        image: np.ndarray, step: int = 1
    ) -> Generator[tuple[int, int], None, None]:
        """Receives numpy array, which represents single-channeled image of uint8 type.
        Yield coordinates of non-empty pixels (pixels with value greater than 0).

        Arguments:
            image (np.ndarray): The image to get non-empty pixels from.
            step (int, optional): The step to iterate through the image. Defaults to 1.

        Yields:
            tuple[int, int]: The coordinates of non-empty pixels.
        """
        for y, row in enumerate(image[::step]):
            for x, value in enumerate(row[::step]):
                if value > 0:
                    yield x * step, y * step

    def get_not_resized_dem(self) -> np.ndarray | None:
        """Reads the not resized DEM image from the background component.

        Returns:
            np.ndarray | None: The not resized DEM image or None if the image could not be read.
        """
        background_component = self.map.get_background_component()
        if not background_component:
            self.logger.warning("Background component not found.")
            return None

        if not background_component.not_resized_path:
            self.logger.warning("Not resized DEM path not found.")
            return None

        not_resized_dem = cv2.imread(background_component.not_resized_path, cv2.IMREAD_UNCHANGED)

        return not_resized_dem

    def get_z_coordinate_from_dem(self, not_resized_dem: np.ndarray, x: int, y: int) -> float:
        """Gets the Z coordinate from the DEM image for the given coordinates.

        Arguments:
            not_resized_dem (np.ndarray): The not resized DEM image.
            x (int): The x coordinate.
            y (int): The y coordinate.

        Returns:
            float: The Z coordinate.
        """
        dem_x_size, dem_y_size = not_resized_dem.shape

        x = int(max(0, min(x, dem_x_size - 1)))
        y = int(max(0, min(y, dem_y_size - 1)))

        z = not_resized_dem[y, x]
        z *= self.get_z_scaling_factor(ignore_height_scale_multiplier=True)

        return z
