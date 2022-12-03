

"""Tests for int_vlan module."""

import pytest

from tools.intf_vlans import parse_rc_intf

trunk_intf = """
!
interface port-channel 1
description Po1
switchport trunk allowed vlan 7,14,16,19,33,35-38 confirm
switchport trunk allowed vlan add 1915,2019,2030
switchport mode trunk
switchport reject-frame untagged
!
"""
acceess_intf = """
!
interface gigaethernet 1/1/1
description subs-34161
switchport access vlan 2009
storm-control unknown-multicast pps 1024
storm-control dlf pps 1024
!
"""

testdata = [
    (
        trunk_intf,
        {
            "port-channel 1": {
                "mode": "trunk",
                "vlans": [7, 14, 16, 19, 33, 35, 36, 37, 38, 1915, 2019, 2030],
            },
        },
    ),
    (acceess_intf, {"gigaethernet 1/1/1": {"mode": "access", "vlans": [2009]}}),
]


@pytest.mark.parametrize("cfg_intf, expected", testdata)
def test_parse_rc_intf(cfg_intf, expected):
    assert parse_rc_intf(cfg_intf) == expected
