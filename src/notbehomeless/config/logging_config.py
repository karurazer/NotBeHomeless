import logging


def setup_logging(level: int = logging.INFO) -> None:
    """
        Configure application-wide logging.
        Call once from an entry point.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
