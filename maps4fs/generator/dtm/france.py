"""This module contains provider of France data."""

import os
import rasterio
from maps4fs.generator.dtm import utils
from maps4fs.generator.dtm.dtm import DTMProvider


class FranceProvider(DTMProvider):
    """Provider of France data."""

    _code = "france"
    _name = "France RGE Alti 2.0"
    _region = "FR"
    _icon = "🇫🇷"
    _resolution = 1
    _author = "[kbrandwijk](https://github.com/kbrandwijk)"
    _is_community = True

    _url = "https://data.cquest.org/ign/rgealti/repack/cog/RGEALTI_2-0_1M_COG_LAMB93-IGN69_FXX.vrt"
    _is_base = False

    _extents_identifier = "France"

    def download_tiles(self) -> list[str]:
        with rasterio.open(
            self.url,
            crs="EPSG:2154",
        ) as vrt_src:
            # Get bbox in EPSG:2154 in the right order
            bbox = self.get_bbox()
            bbox = utils.transform_bbox(bbox, "EPSG:2154")
            bbox = (bbox[0], bbox[3], bbox[1], bbox[2])

            # read the window of data from the vrt
            dst_window = vrt_src.window(*bbox)
            data = vrt_src.read(1, window=dst_window)
            width, height = data.shape[0], data.shape[1]

            # define the transform for the new raster telling where it is in the world
            transform = rasterio.transform.from_bounds(*bbox, width=width, height=height)

            # write it to a temporary file following the standard DTMProvider interface
            file_name = "_".join(map(str, bbox)) + ".tif"
            file_path = os.path.join(self._tile_directory, file_name)
            with rasterio.open(
                file_path,
                "w",
                driver="GTiff",
                crs="EPSG:2154",
                width=width,
                height=height,
                transform=transform,
                count=1,
                dtype=data.dtype,
            ) as dst:
                dst.write(data, indexes=1)

        return [file_path]
