import logging

LOGGER = logging.getLogger("pyrep")
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s :: %(levelname)-8s :: %(message)s",
)


def deactivate_logger():
    """
    Deactivate the logger.
    """
    LOGGER.setLevel(logging.CRITICAL)


def debug_logger():
    """
    Set the logger to debug level.
    """
    LOGGER.setLevel(logging.DEBUG)

def info_logger():
    LOGGER.setLevel(logging.INFO)
