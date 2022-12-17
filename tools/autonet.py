"""Automate network operations."""

import os

from dotenv import load_dotenv

load_dotenv()

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")

my_device = {
    "host": "192.168.22.100 ",
    "auth_username": AUTH_USERNAME,
    "auth_password": AUTH_PASSWORD,
    "auth_strict_key": False,
    "platform": "raisecom_ros",
}
