"""Get API data."""

import logging

import requests
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


def get_data(url):
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
    print(get_data("https://randomuser.me/api/").json())  # noqa:  WPS421
