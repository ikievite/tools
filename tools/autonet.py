"""Automate network operations."""

import logging
import os
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
    if response.result:
        return True
    return False


def add_vlan_trunk_intf(vlan_id: str, intf: str) -> list[str, ...]:
    """Add vlan to trunk interface.

    Args:
        vlan_id: vlan_id
        intf: interface name
    """
    return [f"interface {intf}", f"switchport trunk allowed vlan add {vlan_id}", "exit"]


def send_show(device: dict[str, Any], show_command: str) -> str:
    with Scrapli(**device) as conn:
        response = conn.send_command(show_command)
        return response.result


def create_vlan_modify_intf(
    device: dict[str, Any],
    intf: str,
    vlan_id: str,
    vlan_name: Optional[str] = None,
):
    commands = []
    with Scrapli(**device) as conn:
        if is_vlan_exist(conn, vlan_id=vlan_id):
            logger.debug(f"VLAN {vlan_id} already exists on device.")
        else:
            commands.extend(create_vlan(vlan_id=vlan_id, vlan_name=vlan_name))
        if intf:
            commands.extend(add_vlan_trunk_intf(intf=intf, vlan_id=vlan_id))
        if commands:
            commands.append("write")
            response = conn.send_configs(commands)
            response.raise_for_status()


if __name__ == "__main__":

    my_device = {
        "host": "192.168.22.100 ",
        "auth_username": AUTH_USERNAME,
        "auth_password": AUTH_PASSWORD,
        "auth_strict_key": False,
        "platform": "raisecom_ros",
    }

    create_vlan_modify_intf(my_device, vlan_id="127", intf="gigaethernet 1/1/37")
