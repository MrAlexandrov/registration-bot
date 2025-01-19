import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    # level=logging.DEBUG
)
logger = logging.getLogger(__name__)
