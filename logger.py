import logging

logging.basicConfig(level=logging.INFO, format="%(name)s :: [%(asctime)s] :: %(levelname)s :: %(message)s")
self_logger = logging.getLogger(__name__)
