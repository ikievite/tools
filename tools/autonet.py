"""Automate network operations."""

import os
from typing import Any, Optional

from dotenv import load_dotenv
from scrapli import Scrapli

load_dotenv()

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")


def create_vlan(connection, vlan_id: str, vlan_name: Optional[str] = None) -> None:
    """Create vlan on device.

    Args:
        connection: connection to device
        vlan_id: vlan_id
        vlan_name: vlan name

    Raises:
        Exception: if vlan already exists on device
    """
    if is_vlan_exist(connection, vlan_id):
        raise Exception(f"VLAN {vlan_id} already exists on device {connection}")
    commands = [f"vlan {vlan_id}"]
    if vlan_name:
        commands.append(f"name {vlan_name}")
    response = connection.send_configs(commands)
    response.raise_for_status()


def delete_vlan(connection, vlan_id: str) -> None:
    """Delete vlan on device.

    Args:
        connection: connection to device
        vlan_id: vlan_id

    Raises:
        Exception: if vlan already exists on device
    """
    if not is_vlan_exist(connection, vlan_id):
        raise Exception(f"VLAN {vlan_id} does not exist on device {connection.host}")
    response = connection.send_config(f"no vlan {vlan_id}")
    response.raise_for_status()


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


def add_vlan_trunk_intf(connection, vlan_id: str, intf: str) -> None:
    """Add vlan to trunk interface.

    Args:
        connection: connection to device
        vlan_id: vlan_id
        intf: interface name
    """
    conf_intf = [f"interface {intf}", f"switchport trunk allowed vlan add {vlan_id}"]
    response = connection.send_configs(conf_intf)
    response.raise_for_status()


def send_show(device: dict[str, Any], show_command: str) -> str:
    with Scrapli(**device) as conn:
        response = conn.send_command(show_command)
        return response.result


if __name__ == "__main__":

    my_device = {
        "host": "192.168.22.100 ",
        "auth_username": AUTH_USERNAME,
        "auth_password": AUTH_PASSWORD,
        "auth_strict_key": False,
        "platform": "raisecom_ros",
    }
    with Scrapli(**my_device) as conn:
        add_vlan_trunk_intf(conn, intf="giga 1/1/37", vlan_id="126")
