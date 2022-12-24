"""Automate network operations."""

import logging
import os
from time import perf_counter
from typing import Any, Optional

from dotenv import load_dotenv
from scrapli import Scrapli

logger = logging.getLogger(__name__)

load_dotenv()

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")


def create_vlan(vlan_id: str, vlan_name: Optional[str] = None) -> list[str, ...]:
    """Create vlan on device.

    Args:
        vlan_id: vlan_id
        vlan_name: vlan name

    Returns:
        list with commands
    """
    commands = [f"vlan {vlan_id}"]
    if vlan_name:
        commands.append(f"name {vlan_name}")
    commands.append("exit")
    return commands


def delete_vlan(vlan_id: str) -> list[str]:
    """Delete vlan on device.

    Args:
        vlan_id: vlan_id

    Returns:
        list with commands
    """
    return [f"no vlan {vlan_id}"]


def is_vlan_exist(conn, vlan_id: str) -> bool:
    """Check if vlan exists.

    Args:
        conn: Scrapli connection
        vlan_id: vlan_id

    Returns:
        bool
    """
    response = conn.send_command(f"show vlan {vlan_id} detail")
    if response.result:  # noqa: WPS531
        return True
    return False


def add_vlan_trunk_intf(vlan_id: str, intf: str) -> list[str, ...]:
    """Add vlan to trunk interface.

    Args:
        vlan_id: vlan_id
        intf: interface name

    Returns:
        list with commands
    """
    return [f"interface {intf}", f"switchport trunk allowed vlan add {vlan_id}", "exit"]


def del_vlan_trunk_intf(vlan_id: str, intf: str) -> list[str, ...]:
    """Delete vlan from trunk interface.

    Args:
        vlan_id: vlan_id
        intf: interface name

    Returns:
        list with commands
    """
    return [f"interface {intf}", f"switchport trunk allowed vlan remove {vlan_id}", "exit"]


def send_show(device: dict[str, Any], show_command: str) -> str:  # noqa: D103
    with Scrapli(**device) as conn:
        response = conn.send_command(show_command)
        return response.result


def modify_vlan_intf(
    device: dict[str, Any],
    action: str,
    intf: str,
    vlan_id: str,
    vlan_name: Optional[str] = None,
) -> None:
    """
    Create/delete vlan on device, add/remove vlan from interface.

    Args:
        device: dict with device params
        action: `add` or `del` action
        vlan_id: vlan id
        vlan_name: vlan name
        intf: interface name
    """
    commands = []
    with Scrapli(**device) as conn:
        if action == "add":
            if is_vlan_exist(conn, vlan_id=vlan_id):
                logger.debug(f"VLAN {vlan_id} already exists on device.")
            else:
                commands.extend(create_vlan(vlan_id=vlan_id, vlan_name=vlan_name))
        elif action == "del":
            if is_vlan_exist(conn, vlan_id=vlan_id):
                commands.extend(delete_vlan(vlan_id=vlan_id))
            else:
                logger.debug(f"VLAN {vlan_id} has already been removed on device.")
        if intf:
            if action == "add":
                commands.extend(add_vlan_trunk_intf(intf=intf, vlan_id=vlan_id))
            if action == "del":
                commands.extend(del_vlan_trunk_intf(intf=intf, vlan_id=vlan_id))
        if commands:
            commands.extend(["end", "write"])
            response = conn.send_configs(commands)
            response.raise_for_status()


if __name__ == "__main__":

    sw1 = {
        "host": "192.168.22.100 ",
        "auth_username": AUTH_USERNAME,
        "auth_password": AUTH_PASSWORD,
        "auth_strict_key": False,
        "platform": "raisecom_ros",
    }

    sw2 = {
        "host": "192.168.20.152",
        "auth_username": AUTH_USERNAME,
        "auth_password": AUTH_PASSWORD,
        "auth_strict_key": False,
        "platform": "raisecom_ros",
    }

    start = perf_counter()

    modify_vlan_intf(sw1, action="add", vlan_id="127", intf="gigaethernet 1/1/37")
    modify_vlan_intf(sw2, action="add", vlan_id="127", intf="gigaethernet 1/1/27")

    end = perf_counter()
    execution_time = end - start
    print(f">>> Execution_time: {execution_time}")  # noqa: WPS421
