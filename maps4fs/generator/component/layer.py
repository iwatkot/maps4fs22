"""This module contains the class representing a layer with textures and tags."""

from __future__ import annotations

import os
import re


class Layer:
    """Class which represents a layer with textures and tags.
    It's using to obtain data from OSM using tags and make changes into corresponding textures.

    Arguments:
        name (str): Name of the layer.
        tags (dict[str, str | list[str]]): Dictionary of tags to search for.
        width (int | None): Width of the polygon in meters (only for LineString).
        color (tuple[int, int, int]): Color of the layer in BGR format.
        exclude_weight (bool): Flag to exclude weight from the texture.
        priority (int | None): Priority of the layer.
        info_layer (str | None): Name of the corresnponding info layer.
        usage (str | None): Usage of the layer.
        background (bool): Flag to determine if the layer is a background.
        invisible (bool): Flag to determine if the layer is invisible.

    Attributes:
        name (str): Name of the layer.
        tags (dict[str, str | list[str]]): Dictionary of tags to search for.
        width (int | None): Width of the polygon in meters (only for LineString).
    """

    # pylint: disable=R0913
    def __init__(  # pylint: disable=R0917
        self,
        name: str,
        count: int,
        tags: dict[str, str | list[str] | bool] | None = None,
        width: int | None = None,
        color: tuple[int, int, int] | list[int] | None = None,
        exclude_weight: bool = False,
        priority: int | None = None,
        info_layer: str | None = None,
        usage: str | None = None,
        background: bool = False,
        invisible: bool = False,
        procedural: list[str] | None = None,
        border: int | None = None,
        precise_tags: dict[str, str | list[str] | bool] | None = None,
        precise_usage: str | None = None,
    ):
        self.name = name
        self.count = count
        self.tags = tags
        self.width = width
        self.color = color if color else (255, 255, 255)
        self.exclude_weight = exclude_weight
        self.priority = priority
        self.info_layer = info_layer
        self.usage = usage
        self.background = background
        self.invisible = invisible
        self.procedural = procedural
        self.border = border
        self.precise_tags = precise_tags
        self.precise_usage = precise_usage

    def to_json(self) -> dict[str, str | list[str] | bool]:  # type: ignore
        """Returns dictionary with layer data.

        Returns:
            dict: Dictionary with layer data."""
        data = {
            "name": self.name,
            "count": self.count,
            "tags": self.tags,
            "width": self.width,
            "color": list(self.color),
            "exclude_weight": self.exclude_weight,
            "priority": self.priority,
            "info_layer": self.info_layer,
            "usage": self.usage,
            "background": self.background,
            "invisible": self.invisible,
            "procedural": self.procedural,
            "border": self.border,
            "precise_tags": self.precise_tags,
            "precise_usage": self.precise_usage,
        }

        data = {k: v for k, v in data.items() if v is not None}
        return data  # type: ignore

    @classmethod
    def from_json(cls, data: dict[str, str | list[str] | bool]) -> Layer:
        """Creates a new instance of the class from dictionary.

        Arguments:
            data (dict[str, str | list[str] | bool]): Dictionary with layer data.

        Returns:
            Layer: New instance of the class.
        """
        return cls(**data)  # type: ignore

    def path(self, weights_directory: str) -> str:
        """Returns path to the first texture of the layer.

        Arguments:
            weights_directory (str): Path to the directory with weights.

        Returns:
            str: Path to the texture.
        """
        idx = "01" if self.count > 0 else ""
        weight_postfix = "_weight" if not self.exclude_weight else ""
        return os.path.join(weights_directory, f"{self.name}{idx}{weight_postfix}.png")

    def path_preview(self, weights_directory: str) -> str:
        """Returns path to the preview of the first texture of the layer.

        Arguments:
            weights_directory (str): Path to the directory with weights.

        Returns:
            str: Path to the preview.
        """
        return self.path(weights_directory).replace(".png", "_preview.png")

    def get_preview_or_path(self, weights_directory: str) -> str:
        """Returns path to the preview of the first texture of the layer if it exists,
        otherwise returns path to the texture.

        Arguments:
            weights_directory (str): Path to the directory with weights.

        Returns:
            str: Path to the preview or texture.
        """
        preview_path = self.path_preview(weights_directory)
        return preview_path if os.path.isfile(preview_path) else self.path(weights_directory)

    def paths(self, weights_directory: str) -> list[str]:
        """Returns a list of paths to the textures of the layer.
        NOTE: Works only after the textures are generated, since it just lists the directory.

        Arguments:
            weights_directory (str): Path to the directory with weights.

        Returns:
            list[str]: List of paths to the textures.
        """
        weight_files = os.listdir(weights_directory)

        # Inconsistent names are the name of textures that are not following the pattern
        # of texture_name{idx}_weight.png.
        inconsistent_names = ["forestRockRoot", "waterPuddle"]

        if self.name in inconsistent_names:
            return [
                os.path.join(weights_directory, weight_file)
                for weight_file in weight_files
                if weight_file.startswith(self.name)
            ]

        return [
            os.path.join(weights_directory, weight_file)
            for weight_file in weight_files
            if re.match(rf"{self.name}\d{{2}}_weight.png", weight_file)
        ]
