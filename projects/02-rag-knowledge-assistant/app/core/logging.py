from __future__ import annotations

import logging


def setup_logging(log_level: str) -> None:
    level_name = log_level.upper()
    level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        return

    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.setLevel(level)
