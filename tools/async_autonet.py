"""async_autonet."""


import asyncio
import os
from pprint import pprint
from typing import Any

from dotenv import load_dotenv
from scrapli import AsyncScrapli
from scrapli.exceptions import ScrapliException

MAX_ASYNC_CONNECTIONS = 50

load_dotenv()

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")


device_params = dict[str, Any]


async def with_semaphore(semaphore, func, *args, **kwargs):
    """Use asyncio.Semaphore when calling the func.

    Args:
        semaphore: asyncio semaphore
        func: func
        *args: args
        **kwargs: kwargs

    Returns:
        awaited func
    """
    async with semaphore:
        return await func(*args, **kwargs)


async def send_show(device: device_params, command: str) -> str:
    """Send show command to device.

    Args:
        device: dict with params
        command: command

    Returns:
        device`s output
    """
    host = device.get("host")
    try:
        async with AsyncScrapli(**device) as conn:
            reply = await conn.send_command(command)
        return reply.result
    except ScrapliException as error:
        print(f"{error} on {host}")


async def run_all(devices: list[device_params], command: str) -> dict[str, str]:
    """Run all coroutines.

    Args:
        devices: list with devices
        command: command

    Returns:
        dict with output
    """
    sem = asyncio.Semaphore(MAX_ASYNC_CONNECTIONS)
    result_dict = {}
    coro = [with_semaphore(sem, send_show, dev, command) for dev in devices]
    results = await asyncio.gather(*coro, return_exceptions=True)
    for dev, res in zip(devices, results):
        result_dict[dev["host"]] = res
    return result_dict


if __name__ == "__main__":
    common_params = {
        "auth_username": AUTH_USERNAME,
        "auth_password": AUTH_PASSWORD,
        "auth_strict_key": False,
    }
    sw1 = {
        "host": "192.168.22.100",
        "auth_username": AUTH_USERNAME,
        "auth_password": AUTH_PASSWORD,
        "auth_strict_key": False,
        "platform": "raisecom_ros",
        "transport": "asynctelnet",
        "port": 23,
    }

    sw2 = {
        "host": "192.168.174.24",
        "auth_username": AUTH_USERNAME,
        "auth_password": AUTH_PASSWORD,
        "auth_strict_key": False,
        "platform": "raisecom_ros",
        "transport": "asynctelnet",
        "port": 23,
    }
    devices = [sw1, sw2]
    output = asyncio.run(run_all(devices, "show sntp"))
    pprint(output)
