"""Get API data."""

import logging
import os

import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()

logger = logging.getLogger(__name__)

API_MODELS_URLS = os.getenv("API_MODELS_UPL")


def get_data(url: str) -> requests.Response:
    """Get API data.

    Args:
        url: url

    Returns:
        response
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except HTTPError as http_err:
        logger.critical(f"HTTP error occurred: {http_err}")
    except Exception as exc:
        logger.critical(f"Other error occurred: {exc}")


if __name__ == "__main__":
    print(get_data(API_MODELS_URLS).json())  # noqa:  WPS421
