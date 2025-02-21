from typing import NamedTuple

from config import video_tutorials_json


class Messages:
    TITLE = "maps4FS"
    MAIN_PAGE_DESCRIPTION = (
        "Generate map templates for Farming Simulator from real places.  \n\n"
        "If some objects (buidings, fields, etc.) are missing or misplaced,  \nyou can edit them "
        "by yourself on the 🌎 [OpenStreetMap](https://www.openstreetmap.org/) website. \n\n"
        "💬 Join our [Discord server](https://discord.gg/Sj5QKKyE42) to get help, share your "
        "maps, or just chat.  \n"
        "🤗 If you like the project, consider supporting it on [Buy Me a Coffee](https://www.buymeacoffee.com/iwatkot) or "
        "[Patreon](https://www.patreon.com/iwatkot).  \n"
        "🐙 Visit the [GitHub repository](https://github.com/iwatkot/maps4fs) for more information.  \n"
        "📹 A complete step-by-step video tutorial is on [YouTube](https://www.youtube.com/watch?v=Nl_aqXJ5nAk&)!  \n"
        "📹 WIP: Check out the complete playlist of video turorials on [YouTube]"
        "(https://www.youtube.com/watch?v=hPbJZ0HoiDE&list=PLug0g7UYHX8D1Jik6NkJjQhdxqS-NOtB9). 🆕"
    )

    LOCAL_VERSION = (
        "Right now you're using a public version of the app, which has some limitations.  \n"
        "You can also run the app locally, it will work faster, has no limitations, and "
        "have some additional features.  \n"
        "If you have Docker installed it's just one command:  \n"
        "```bash  \ndocker run -p 8501:8501 iwatkot/maps4fs  \n```  \n"
        "Detailed instuctions are available in the [README](https://github.com/iwatkot/maps4fs"
        "?tab=readme-ov-file#option-2-docker-version)."
    )

    FS22_NOTES = (
        "Support for the Farming Simulator 22 is discontinued.  \nSome of the features are not "
        "available for this game."
    )

    COVERAGE_INFO = (
        "In this section you can generate a global preview of all the generated maps.  \n"
    )

    PUBLIC_MAP_SIZE = "If you run the app locally, you can generate maps of any size."

    MOVED = "The app has moved to ➡️➡️➡️ [maps4fs.xyz](https://maps4fs.xyz)"
    MAIN_PAGE_COMMUNITY_WARNING = (
        "🚜 Hey, farmer!  \n"
        "Do you know what **Docker** is? If yes, please consider running the application "
        "locally.  \n"
        "StreamLit community hosting has some limitations, such as:  \n"
        "🔸 Maximum map size is 2048x2048 meters.  \n"
        "🔸 Background terrain will not be generated.  \n"
        "🔸 Water planes will not be generated.  \n"
        "🔸 Map rotation is disabled.  \n"
        "🔸 Texture dissolving is disabled (they will look worse).  \n  \n"
        "If you run the application locally, you won't have any of these limitations "
        "and will be able to generate maps of any size with any settings you want and nice looking textures.  \n"
        "Learn more about the Docker version in the repo's "
        "[README](https://github.com/iwatkot/maps4fs?tab=readme-ov-file#option-2-docker-version).  \n"
        "Also, if you are familiar with Python, you can use the "
        "[maps4fs](https://pypi.org/project/maps4fs/) package to generate maps locally."
    )
    TOOL_LOCAL = "💡 This tool is available in the local version of the tool."
    SETTING_LOCAL = "💡 This setting is available in the local version of the tool."
    SETTING_DISABLED_ON_PUBLIC = (
        "🔒 The {setting} setting is disabled on the public version of the app."
    )

    TOOLBOX_INFO = (
        "This section contains different tools that can be helpful for modders, grouped by "
        "the component of the map they are related to.  \n"
    )
    KNOWLEDGE_INFO = (
        "Here you can find some useful information about the different aspects of map modding."
    )
    FAQ_INFO = "Here you can find answers to the most frequently asked questions."
    ONLY_FULL_TILES_INFO = (
        "If checked only full tiles will be generated. If unchecked, the background terrain will "
        "be also generated as splitted tiles, e.g. N, NE, E, SE, S, SW, W, NW.  \n"
        "In most cases you don't need splitted tiles, so it's recommended to keep this option "
        "checked."
    )

    TEXTURE_SCHEMA_INFO = (
        "This section contains the schema which is used to generate the textures. "
        "Any changes here can lead to errors or completely broken map. "
    )
    TREE_SCHEMA_INFO = (
        "This section contains the schema which is used to generate the trees. "
        "Any changes here can lead to errors or completely broken map. "
    )
    CUSTOM_OSM_INFO = (
        "To prepare the custom OSM file, please refer to the [documentation]("
        "https://github.com/iwatkot/maps4fs/blob/main/docs/custom_osm.md).  \n"
        "Note, that incorrect file can lead to errors or completely broken map."
    )
    CUSTOM_BACKGROUND_INFO = (
        "The uploaded file should be:  \n"
        "- Single-channel (grayscale) unsigned 16-bit PNG image.  \n"
        "- The size of the image should be map size + 4096 in each dimension, where the map in "
        "the center.  \n"
        "- If rotation needed, the image should be rotated already.  \n  \n"
        "If any of above conditions are not met, generation will fail."
    )
    EXPERT_MODE_INFO = (
        "In this mode you can edit confuguration of the generation in a raw format. "
        "Be careful, any incorrect value can lead to errors or completely broken map."
    )
    EXPERT_SETTINGS_INFO = (
        "Before changing anything here, read the [documentation]"
        "(https://github.com/iwatkot/maps4fs/tree/main/docs)"
        ", otherwise, you probably will get "
        "a completely broken map."
    )
    OVERLOADED = (
        "Right now the server is overloaded. Please try again later.  \n"
        "Or use the [Docker version]("
        "https://github.com/iwatkot/maps4fs?tab=readme-ov-file#option-2-docker-version)  of the tool."
    )

    COMMUNITY_PROVIDER = (
        "This DTM provider was developed by the community, if you have any issues with it "
        "please contact the author."
    )
    CUSTOM_TEMPLATE_INFO = (
        "This option allows you to upload your own map template.  \n"
        "The template should match the structure of the default template, otherwise it will "
        "not work. Prepare the template carefully, any mistake can lead to errors or completely "
        "broken map. No support will be provided for custom templates."
    )
    CACHE_INFO = (
        "Cache contains the data from DTM Providers, map previews, satellite images, etc. "
        "If you clean the cache, it will be removed but the generator will download the data "
        "again so it may take longer to generate the map. Do not clean the cache unless you "
        "have any issues with it."
    )


class Settings:
    """
    Settings class contains descriptions for configuration options
    for various aspects of the map generation process.
    """

    # DEM Settings

    ADJUST_TERRAIN_TO_GROUND_LEVEL = (
        "Enabling this setting will raise or lower the terrain "
        "so that it's lowest point is at ground level (taking into account the "
        "plateau and water depth values set below)."
    )
    MULTIPLIER = (
        "DEM multiplier can be used to make the terrain more pronounced. "
        "By default the DEM file will be exact copy of the real terrain. "
        "If you want to make it more steep, you can increase this value. "
        "The recommended value of the multiplier is 1.  \n"
        "But this will not work with every place, you need to perform "
        "experiments, play both with the multiplier and the height scale in GE.  \n"
        "ℹ️ **Units:** integer value."
    )
    BLUR_RADIUS = (
        "DEM blur radius is used to blur the elevation map. Without blurring the terrain "
        "may look too sharp and unrealistic. By default the blur radius is set to 3 "
        "which corresponds to a 3x3 pixel kernel. You can increase this value to make "
        "the terrain more smooth. Or make it smaller to make the terrain more sharp.  \n"
        "Follow the recommendations of the DTM provider you selected for the best result.  \n"
        "ℹ️ **Units:** integer value."
    )
    BLUR_RADIUS_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/78e18ceb-b5b1-4a9d-b51b-4834effdaf9b)  \n"
        "⚠️ **Note:** This image represents the difference when using low quality DEM data "
        "with resolution of 30 meters per pixel. If you're using high quality DEM data, "
        "do not use high blur radius values, because it will destroy the details of the terrain."
    )

    PLATEAU = (
        "DEM plateau value is used to make the whole map higher or lower. "
        "This value will be added to each pixel of the DEM image, making it higher. "
        "It can be useful if you're working on a plain area and need to add some "
        "negative height (to make rivers, for example).  \n"
        "ℹ️ **Units:** meters from the ground level."
    )
    CEILING = (
        "DEM ceiling value is used to add padding in the DEM above the "
        "highest elevation in your map area. It can be useful if you plan to manually "
        "add some height to the map by sculpting the terrain in GE.  \n"
        "ℹ️ **Units:** meters from the top of the highest elevation."
    )
    MINIMUM_HEIGHT_SCALE = (
        "This value is used as the heightScale in your map i3d. It will automatically "
        "be set higher if the elevation in your map (plus plateau, ceiling and water "
        "depth) is higher than this value.  \n"
        "ℹ️ **Units:** integer value."
    )

    WATER_DEPTH = (
        "Water depth value will be subtracted from the DEM image, making the water "
        "deeper. The pixel value used for this is calculated based on the heightScale value "
        "for your map.  \n"
        "ℹ️ **Units:** meters."
    )
    WATER_DEPTH_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/22b99071-3169-4c02-9425-1e9fec0e27ec)  \n"
        "⚠️ **Note:** This image represents the difference when using low quality DEM data "
        "where there's no data about the water depth. If you're using high quality DEM data, "
        "you don't need to use this setting, or it will break the terrain."
    )

    ADD_FOUNDATIONS = (
        "If add foundations is enabled, the terrain under the buildings will be flattened."
    )
    ADD_FOUNDATIONS_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/51cd6005-6971-49e5-a649-4ea31abac95d)"
    )

    # Background Settings

    GENERATE_BACKGROUND = (
        "The background terrain obj files will be generated to edit them in Blender if turned on. "
        "Turn it off if you already have them or don't need them."
    )
    GENERATE_WATER = (
        "The water planes obj files will be generated to edit them in Blender if turned on. "
        "Turn it off if you already have them or don't need them."
    )
    RESIZE_FACTOR = (
        "The background resize factor is used to resize the background terrain. The higher the value, "
        "the less detailed the background terrain will be. If set to 1, the background terrain "
        "will not be resized. Low values will result with a very long processing and "
        "meshes of enormous size. Do not change it unless you know what you are doing.  \n"
        "ℹ️ **Units:** integer value."
    )
    REMOVE_CENTER = (
        "If remove center is enabled, the region of playable map terrain will be removed "
        "from the background terrain 3D model."
    )
    REMOVE_CENTER_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/912864b7-c790-47a9-a001-dd1936d21c17)"
    )

    APPLY_DECIMATION = (
        "If apply decimation is enabled, the background terrain will be decimated to the "
        "specified value. It can be useful if you want to reduce the size of the 3D model. "
    )
    DECIMATION_PERCENT = (
        "Decimation percent value is used to set the decimation percent. The higher the value, "
        "the more decimated the model will be. Be careful with high values, because it may "
        "completely break the model.  \n"
        "ℹ️ **Units:** percents of the original image size."
    )
    DECIMATION_AGRESSION = (
        "Decimation aggression value is used to set the decimation aggression. The higher the "
        "the more faces will be removed. Note, that higher values will break the geometry of the "
        "3D model and it won't match with the playable terrain.  \n"
        "ℹ️ **Units:** integer value."
    )

    # GRLE Settings

    FARMLAND_MARGIN = (
        "Farmland margin value is used to add some margin around the farmland. "
        "It can be useful because without the margin, the farmland will end exact on the same "
        "position as the field ends. This can cause some issues with gameplay.  \n"
        "ℹ️ **Units:** meters."
    )
    FARMLAND_MARGIN_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/c160bf6d-9217-455b-9655-462dc09b943c)"
    )
    RANDOM_PLANTS = (
        "If random plants are enabled the different species of plants will be generated. "
        "If unchecked, only basic smallDenseMix will be applied."
    )
    RANDOM_PLANTS_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/e0dae979-21a8-4aa2-8281-ddcdcce3c582)"
    )

    ADD_FARMYARDS = (
        "If add farmyards is enabled and info_layer: farmyards is present in the texture schema, "
        "the regions with correspoding tas will be added as a farmland even without the "
        "corresponding field. It can be useful if you want to add some farmland in the "
        "regions without fields."
    )
    ADD_GRASS = (
        "If add grass is enabled, all the empty areas (without fields, roads, etc.) will "
        "be filled with grass."
    )
    ADD_GRASS_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/49c0376a-b83b-46f0-9e25-2f11e03e16c0)"
    )

    BASE_GRASS = "Select the plant that will be used as a base grass."
    PLANTS_ISLAND_MINIMUM_SIZE = (
        "Plants island minimum size value is used to set the minimum size of the plants islands "
        "when random size of the island will be selected, it will be the lowest possible size.  \n"
        "ℹ️ **Units:** meters."
    )
    PLANTS_ISLAND_MINIMUM_SIZE_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/1cac092f-62c7-4da3-82d1-a72cb64109cb)"
    )
    PLANTS_ISLAND_MAXIMUM_SIZE = (
        "Plants island maximum size value is used to set the maximum size of the plants islands "
        "when random size of the island will be selected, it will be the highest possible size.  \n"
        "ℹ️ **Units:** meters."
    )
    PLANTS_ISLAND_MAXIMUM_SIZE_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/1cac092f-62c7-4da3-82d1-a72cb64109cb)"
    )
    PLANTS_ISLAND_VERTEX_COUNT = (
        "Plants island vertex count value is used to set the number of vertices of the plants. "
        "The higher the value, the more complex shapes of the island will be.  \n"
        "ℹ️ **Units:** number of vertices."
    )
    PLANTS_ISLAND_VERTEX_COUNT_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/b8c7f1d5-9446-4d4c-9a51-5357f7984c60)"
    )
    PLANTS_ISLAND_ROUNDING_RADIUS = (
        "Plants island rounding radius value is used to set the rounding radius of the plants. "
        "The higher the value, the more rounded the vertices will be.  \n"
        "ℹ️ **Units:** meters."
    )
    PLANTS_ISLAND_ROUNDING_RADIUS_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/1b488107-9e85-479b-a59d-d3778404db8d)"
    )
    PLANTS_ISLAND_PERCENT = (
        "Plants island percent value is used to set the relation between the map size and the "
        "number of islands of plants. For example, if set to 100% for map size of 2048, the number"
        " of islands will be 2048.  \n"
        "ℹ️ **Units:** percents of the map size."
    )
    PLANTS_ISLAND_PERCENT_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/aa10bfbc-1cea-4002-b8ef-bfe0a902d1d5)"
    )
    BASE_PRICE = (
        "Base price value is used to set the base price of the farmland. It will be used to "
        "calculate the final price of the farmland.  \n"
        "ℹ️ **Units:** in-game currency (EUR or USD)."
    )
    PRICE_SCALE = (
        "Price scale value is a percentage value that will be applied to the price of the "
        "farmland based on the base price in farmlands.xml file. To make the farmland more "
        "expensive, make this value higher than 100. To make it cheaper, make it lower than 100.  \n"
        "ℹ️ **Units:** percents of the base price."
    )
    FILL_EMPTY_FARMLANDS = (
        "If fill empty farmlands is enabled, the empty (zero value) pixels of the farmlands "
        "info layer image will be filled with 255 value."
    )

    # I3D Settings

    ADD_TREES = (
        "If add trees is enabled, the trees will be added on the areas that defined as forests "
        "on the OSM data."
    )
    ADD_TREES_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/50dd8f82-f4f9-411e-a17a-ea10a0b95c20)"
    )

    FOREST_DENSITY = (
        "Forest density value represents the distance between trees in the forest. "
        "The higher the value, the more sparse the forest will be and less trees will be "
        "generated. Be careful with low values, because depending on the amount of forest areas "
        "and the map size, it may generate dozens of thousands of trees, which can cause "
        "performance issues.  \n"
        "ℹ️ **Units:** meters between trees."
    )
    FOREST_DENSITY_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/bf353ed6-f25c-4226-b0d6-105ada0f097b)"
    )

    TREES_RELATIVE_SHIFT = (
        "Represents the maximum possible shift of the tree from it's original position in percents"
        " of the density value. For example: if the density is set to 10 and the relative shift "
        "is set to 20%, the tree can be shifted by 2 meters in each direction.  \n"
        "ℹ️ **Units:** percents of the Forest Density value."
    )

    # Texture Settings

    DISSOLVE = (
        "If texture dissolving is enabled, the textures will be splitted between different files. "
        "It makes them look better in game, but it will require some time. "
        "It's recommended to keep this option enabled."
    )
    DISSOLVE_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/b7da059b-eb35-4a4e-a656-168c31257b15)"
    )

    FIELDS_PADDING = (
        "Field padding value is used to add some padding around the fields. "
        "It will make the fields smaller, can be useful if they are too close to each other.  \n"
        "ℹ️ **Units:** meters."
    )
    FIELDS_PADDING_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/b88ebfb3-7afb-4012-a845-42a04fefa7d2)"
    )

    SKIP_DRAINS = (
        "If skip drains is enabled, the drains and ditches will be ignored while generating "
        "the map."
    )
    USE_CACHE = (
        "If use cache is enabled, the data from OSM will be cached, that means that if you "
        "generated the map once and then made some changes in the OSM file, the generator will "
        "use the cached data instead of downloading it again. It can save some time, but if you "
        "want to get the most recent data, you should disable this option. This option has no "
        "effect when you're using the custom OSM file."
    )
    USE_PRECISE_TAGS = (
        "If enabled, the generator will use the **precise_tags** from texture schema instead "
        "of using the default **tags**. With the default schema it can be used to generate "
        "forests of specific leaf types, for example.  \n"
        "Note, that if there are no precise tags added on OSM data (for example, leaf type "
        "was not specified), the generator will not draw this texture at all, as well as will "
        "not add any trees."
    )
    USE_PRECISE_TAGS_EXAMPLE = (
        "By default the generator will use the `tags` from the texture schema.  \n"
        "```json  \n"
        '"tags": { "natural": ["wood", "tree_row"], "landuse": "forest" },  \n'
        "```  \n"
        "However, if this option is enabled, the generator will use the `precise_tags` instead.  \n"
        "```json  \n"
        '"precise_tags": { "leaf_type": "mixed" },  \n'
        "```  \n"
        "⚠️ **Note:** If an OSM object does not contain the precise tag (e.g. leaf_type), "
        "the generator will not draw the texture. Use this feature only if you ensure that "
        "the precise tags are present in the OSM data."
    )

    # Splines Settings

    SPLINE_DENSITY = (
        "Spline density value represents the number of additional points, which will be added between "
        "each pair of existing points of the spline. The higher value will make the spline "
        "more smooth. Be careful with high values, because it may make your spline too complex.  \n"
        "ℹ️ **Units:** number of additional points between each pair of existing points."
    )
    SPLINE_DENSITY_EXAMPLE = (
        "![](https://github.com/user-attachments/assets/8acd2910-4b86-42d1-a509-e8ccc7c8169d)"
    )
    ADD_REVERSED_SPLINES = (
        "If add reversed splines is enabled, the splines will be generated in both directions. "
        "Otherwise, only one direction will be generated (as in the OSM data)."
    )

    # Satellite Settings

    DOWNLOAD_IMAGES = (
        "If download images is enabled, the generator will download and merge the satellite images."
    )

    SATELLITE_MARGIN = (
        "Satellite margin value (in meters) is used to add some margin around the satellite images. "
        "It's not recommended to change this value in most cases, because as a result, the "
        "area of satellite images won't match the area of the map and it will lead to "
        "challenges when trying to align the images with the map.  \n"
        "ℹ️ **Units:** meters."
    )

    ZOOM_LEVEL = (
        "Satellite zoom level is used to set the zoom level of the satellite images. "
        "The higher the value, the more detailed the images will be. "
        "Be careful with high values, because it may result in very large images and super long "
        "download time.  \n"
        "ℹ️ **Units:** integer value, maximum recommended value is 18."
    )


class VideoTutorial(NamedTuple):
    """Represents a video tutorial object."""

    episode: int
    title: str
    description: str
    link: str
    image: str


video_tutorials: list[VideoTutorial] = [VideoTutorial(**video) for video in video_tutorials_json]
