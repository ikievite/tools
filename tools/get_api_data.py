"""Get API data."""

import itertools
import json
import logging
import os
from pprint import pprint
from typing import Iterator, Optional

import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()

logger = logging.getLogger(__name__)

API_MODELS_URL = os.getenv("API_MODELS_URL")
API_SWITCHES_URL = os.getenv("API_SWITCHES_URL")


def get_data(url: str, payload: Optional[dict[str, int]] = None):
    """Get API data.

    Args:
        url: url
        payload: payload

    Returns:
        request response
    """
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        return response.json()
    except HTTPError as http_err:
        logger.critical(f"HTTP error occurred: {http_err}")
    except Exception as exc:
        logger.critical(f"Other error occurred: {exc}")


def get_all_data(
    url: str,
    payload: str = None,
    meta_field: str = "meta",
    data_field: str = "data",
) -> Iterator[dict[str, str]]:
    """Get data with API pagination.

    Args:
        url: url
        payload: payload
        meta_field: meta field name
        data_field: data field name

    Yields:
        list with items
    """
    response = get_data(url, payload)
    yield response[data_field]
    last_page = response.get(meta_field).get("pages")
    for page in range(2, last_page + 1):
        if payload:
            payload.update({"page": page})
        else:
            payload = {"page": page}
        yield get_data(url, payload)[data_field]


if __name__ == "__main__":
    switches = get_all_data(API_SWITCHES_URL)
    pprint(len(list(itertools.chain(*switches))))  # noqa: WPS421

    dlink_des3526 = "62e1b01d4668a56741394d03"
    query = json.dumps({"model": dlink_des3526})
    dlink_des3526_switches = get_all_data(API_SWITCHES_URL, {"query": query})
    pprint(len(list(itertools.chain(*dlink_des3526_switches))))    # noqa: WPS421
