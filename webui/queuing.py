import json
import os
import threading
from time import sleep, time
from typing import Generator

from config import QUEUE_FILE, QUEUE_INTERVAL, QUEUE_TIMEOUT

from maps4fs import Logger

logger = Logger(level="INFO", to_file=False)


def get_queue(force: bool = False) -> dict[int, str]:
    """Get the queue from the queue file.
    If the queue file does not exist, create a new one with an empty queue.

    Arguments:
        force (bool): Whether to force the creation of a new queue file.

    Returns:
        dict[int, str]: The queue, where the key is an epoch time and the value is a session.
    """
    if not os.path.isfile(QUEUE_FILE) or force:
        logger.debug("Queue will be reset.")
        save_queue({})
        return {}
    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)

    for epoch, session in queue.items():
        if int(epoch) + int(QUEUE_TIMEOUT * 1.5) < int(time()):
            remove_from_queue(session, queue)

    return queue


def get_queue_length() -> int:
    """Get the length of the queue.

    Returns:
        int: The length of the queue.
    """
    return len(get_queue())


def save_queue(queue: dict[int, str]) -> None:
    """Save the queue to the queue file.

    Arguments:
        queue (dict[int, str]): The queue to save.
    """
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f)
    logger.debug("Queue set to %s.", queue)


def add_to_queue(session: str) -> None:
    """Add a session to the queue.

    Arguments:
        session (str): The session to add to the queue.
    """
    queue = get_queue()

    epoch = int(time())

    queue[epoch] = session
    save_queue(queue)
    logger.debug("Session %s added to the queue.", session)


def get_first_item() -> str | None:
    """Get the session of the first item in the queue.

    Returns:
        str: The session of the first item in the queue.
    """
    queue = get_queue()
    if not queue:
        return None

    return queue[min(queue.keys())]


def remove_from_queue(session: str, queue: dict[int, str] = None) -> None:
    """Remove a session from the queue.

    Arguments:
        session (str): The session to remove from the queue.
    """
    queue = queue or get_queue()
    if session in queue.values():
        queue = {epoch: s for epoch, s in queue.items() if s != session}
        save_queue(queue)
        logger.debug("Session %s removed from the queue.", session)
    else:
        logger.debug("Session %s not found in the queue.", session)


def get_position(session: str) -> int | None:
    """Get the position of a session in the queue.

    Arguments:
        session (str): The session to get the position of.

    Returns:
        int: The position of the session in the queue.
    """
    queue = get_queue()
    if session not in queue.values():
        return None
    return list(queue.values()).index(session)


def wait_in_queue(session: str) -> Generator[int, None, None]:
    """Wait in the queue until the session is the first item.

    Arguments:
        session (str): The session to wait for.
    """
    retries = QUEUE_TIMEOUT // QUEUE_INTERVAL
    logger.debug(
        "Starting to wait in the queue for session %s with maximum retries %s.", session, retries
    )

    termiation_thread = threading.Thread(target=start_termination, args=(session,))
    termiation_thread.start()

    for _ in range(retries):
        position = get_position(session)
        if position == 0 or position is None:
            logger.debug("Session %s is the first item in the queue.", session)
            return
        logger.debug("Session %s is in position %s in the queue.", session, position)
        yield position
        sleep(QUEUE_INTERVAL)


def start_termination(session: str) -> None:
    """Start the termination of a session.
    No matter if it was awaited, in queue or not, after a timeout it will be removed
    from the queue.

    Arguments:
        session (str): The session to terminate.
    """
    logger.debug("Session %s will be terminated after %s seconds.", session, QUEUE_TIMEOUT)
    sleep(QUEUE_TIMEOUT)
    remove_from_queue(session)
