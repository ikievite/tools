"""async_scan"""


import asyncio
import os

from dotenv import load_dotenv
from scrapli import AsyncScrapli
from scrapli.exceptions import ScrapliException

load_dotenv()

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")

telnet_params = {"transport": "asynctelnet", "port": 23}

ssh_prams = {"transport": "asyncssh"}

opts = {
    "asyncssh": {
        "kex_algs": [
            "diffie-hellman-group1-sha1",
        ],
        "encryption_algs": [
            "aes256-cbc",
            "aes192-cbc",
        ],
        "server_host_key_algs": ["ssh-dss", "ssh-rsa"],
    },
}


class CheckConnection:
    def __init__(self, device_list):
        self.device_list = device_list
        self._index = 0

    async def _scan(self, device):
        host = device["host"]
        try:
            async with AsyncScrapli(**device) as conn:
                prompt = await conn.get_prompt()
            return True, prompt
        except ScrapliException as error:
            return False, error

    async def __anext__(self):
        if self._index >= len(self.device_list):
            raise StopAsyncIteration
        device = self.device_list[self._index]
        result = await self._scan(device)
        self._index += 1
        return result

    def __aiter__(self):
        return self


async def check_connection(device):
    """Check device connection.

    Args:
        device: dict with params

    Returns:
        bool, prompt
    """
    try:
        async with AsyncScrapli(**device) as conn:
            prompt = await conn.get_prompt()
        return True, prompt
    except ScrapliException as error:
        return False, error


async def scanner(devices, protocol):
    """Scan devices.

    Args:
        devices: list with devices
        protocol: connection protocol
    """
    if protocol == "telnet":
        [device.update(telnet_params) for device in devices]
    elif protocol == "ssh":
        [device.update(ssh_prams) for device in devices]
    check = CheckConnection(devices)
    async for status, msg in check:
        print(f"{protocol} {status} {msg}")  # noqa: WPS421


async def main():  # noqa: D103
    ssh_devices = [
        {
            "host": "192.168.22.100",
            "auth_username": AUTH_USERNAME,
            "auth_password": AUTH_PASSWORD,
            "auth_strict_key": False,
            "platform": "raisecom_ros",
            "transport": "asyncssh",
            "transport_options": opts,
        },
        {
            "host": "192.168.174.24",
            "auth_username": AUTH_USERNAME,
            "auth_password": AUTH_PASSWORD,
            "auth_strict_key": False,
            "platform": "raisecom_ros",
            "transport": "asyncssh",
            "transport_options": opts,
        },
    ]
    telnet_devices = [
        {
            "host": "192.168.22.100",
            "auth_username": AUTH_USERNAME,
            "auth_password": AUTH_PASSWORD,
            "auth_strict_key": False,
            "platform": "raisecom_ros",
            "transport": "asynctelnet",
            "port": 23,
        },
        {
            "host": "192.168.174.24",
            "auth_username": AUTH_USERNAME,
            "auth_password": AUTH_PASSWORD,
            "auth_strict_key": False,
            "platform": "raisecom_ros",
            "transport": "asynctelnet",
            "port": 23,
        },
    ]
    scan_ssh = scanner(ssh_devices, "ssh")
    scan_telnet = scanner(telnet_devices, "telnet")
    await asyncio.gather(scan_ssh, scan_telnet)


if __name__ == "__main__":
    asyncio.run(main())
