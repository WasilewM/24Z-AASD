import logging

LOG_LEVEL = "info"


logger = logging.getLogger()
formatter = logging.Formatter("%(asctime)s,%(levelname)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(LOG_LEVEL.upper())
