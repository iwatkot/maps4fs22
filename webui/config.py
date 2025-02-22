import json
import os
import platform
import shutil
import threading
from time import sleep
from typing import Any, Literal

import requests
import schedule

WORKING_DIRECTORY = os.getcwd()
ARCHIVES_DIRECTORY = os.path.join(WORKING_DIRECTORY, "archives")
DATA_DIRECTORY = os.path.join(WORKING_DIRECTORY, "data")
MAPS_DIRECTORY = os.path.join(WORKING_DIRECTORY, "maps")
TEMP_DIRECTORY = os.path.join(WORKING_DIRECTORY, "temp")
INPUT_DIRECTORY = os.path.join(TEMP_DIRECTORY, "input")
TILES_DIRECTORY = os.path.join(TEMP_DIRECTORY, "tiles")

VIDEO_TUTORIALS_PATH = os.path.join(WORKING_DIRECTORY, "webui", "videos.json")

with open(VIDEO_TUTORIALS_PATH, "r", encoding="utf-8") as f:
    video_tutorials_json = json.load(f)

STREAMLIT_COMMUNITY_KEY = "HOSTNAME"
STREAMLIT_COMMUNITY_VALUE = "streamlit"
PUBLIC_HOSTNAME_KEY = "PUBLIC_HOSTNAME"
PUBLIC_HOSTNAME_VALUE = "maps4fs"

DOCS_DIRECTORY = os.path.join(WORKING_DIRECTORY, "docs")
MD_FILES = {
    "📁 Map structure": "map_structure.md",
    "⛰️ DEM": "dem.md",
    "🎨 Textures": "textures.md",
    "🌾 Farmlands": "farmlands.md",
    "🚜 Fields": "fields.md",
}
FAQ_MD = os.path.join(DOCS_DIRECTORY, "FAQ.md")

QUEUE_LIMIT = 5
DEFAULT_LAT = 45.28571409289627
DEFAULT_LON = 20.237433441210115

QUEUE_FILE = os.path.join(WORKING_DIRECTORY, "queue.json")
HISTORY_FILE = os.path.join(WORKING_DIRECTORY, "history.json")
QUEUE_TIMEOUT = 120  # 2 minutes
QUEUE_INTERVAL = 5

REMOVE_DELAY = 300  # 5 minutes


def get_schema(game_code: str, schema_type: Literal["texture", "tree"]) -> list[dict[str, Any]]:
    """Get the schema for the specified game and schema type.

    Args:
        game_code (str): The game code.
        schema_type (Literal["texture", "tree"]): The schema type.

    Returns:
        list[dict[str, Any]]: The schema for the specified game and schema type.
    """
    game_code = game_code.lower()
    schema_path = os.path.join(DATA_DIRECTORY, f"{game_code}-{schema_type}-schema.json")

    if not os.path.isfile(schema_path):
        raise FileNotFoundError(f"{schema_type} for {game_code} not found in {schema_path}.")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema


def get_mds() -> dict[str, str]:
    """Get the paths to the Markdown files in the docs directory.

    Returns:
        dict[str, str]: The paths to the Markdown files in the docs directory.
    """
    return {
        md_file: os.path.join(DOCS_DIRECTORY, filename) for md_file, filename in MD_FILES.items()
    }


def is_on_community_server() -> bool:
    """Check if the script is running on the Streamlit Community server.

    Returns:
        bool: True if the script is running on the Streamlit Community server, False otherwise.
    """
    return os.environ.get(STREAMLIT_COMMUNITY_KEY) == STREAMLIT_COMMUNITY_VALUE


def is_public() -> bool:
    """Check if the script is running on a public server.

    Returns:
        bool: True if the script is running on a public server, False otherwise.
    """
    return os.environ.get(PUBLIC_HOSTNAME_KEY) == PUBLIC_HOSTNAME_VALUE


def remove_with_delay_without_blocking(
    file_path: str,
    delay: int = REMOVE_DELAY,
) -> None:
    """Remove a file with a delay without blocking the main thread.

    Arguments:
        file_path (str): The path to the file to remove.
        logger (mfs.Logger): The logger instance.
        delay (int): The delay in seconds before removing the file.
    """

    def remove_file() -> None:
        sleep(delay)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    threading.Thread(target=remove_file).start()


def get_versions() -> tuple[str, str] | None:
    """Get the latest version and the current version of the package.

    Returns:
        tuple[str, str] | None: The latest version and the current version if the package is not
            the latest version, None otherwise
    """
    try:
        response = requests.get("https://pypi.org/pypi/maps4fs/json")
        response.raise_for_status()

        latest_version = response.json()["info"]["version"]

        current_version = get_package_version("maps4fs")

        return latest_version, current_version
    except Exception:
        return None


def get_package_version(package_name: str) -> str:
    """Get the package version.

    Returns:
        str: The package version.
    """
    current_os = platform.system().lower()
    if current_os == "windows":
        command = f"pip list 2>NUL | findstr {package_name}"
    else:
        command = f"pip list 2>/dev/null | grep {package_name}"

    response = os.popen(command).read()
    return response.replace(package_name, "").strip()


def get_directory_size(directory: str) -> int:
    """Calculate the total size of the specified directory.

    Args:
        directory (str): The path to the directory.

    Returns:
        int: The total size of the directory in bytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def get_temp_size() -> float:
    """Get the size of the temp directory (in MB).

    Returns:
        str: The size of the temp directory.
    """
    temp_size_bytes = get_directory_size(TEMP_DIRECTORY)
    return temp_size_bytes / (1024**2)


def create_dirs() -> None:
    """Create the directories if they do not exist."""
    directories = [
        ARCHIVES_DIRECTORY,
        DATA_DIRECTORY,
        MAPS_DIRECTORY,
        INPUT_DIRECTORY,
        TILES_DIRECTORY,
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def clean_temp() -> None:
    """Clean the temp directory."""
    shutil.rmtree(TEMP_DIRECTORY, ignore_errors=True)
    create_dirs()


def run_scheduler():
    """Run the scheduler."""
    while True:
        schedule.run_pending()
        sleep(1)


if is_public():
    schedule.every(6).hours.do(clean_temp)
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

create_dirs()
