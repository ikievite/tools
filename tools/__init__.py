import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "{asctime} - {levelname} - {name} - {message}",
    datefmt="%H:%M:%S",
    style="{",
)
console.setFormatter(formatter)
logger.addHandler(console)
