import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
    # level=logging.DEBUG
)
logger = logging.getLogger(__name__)