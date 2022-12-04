"""Tests for int_vlan module."""


from tools.intf_vlans import parse_rc_intf, parse_dlink_intf


def test_parse_rc_intf():
    rc_cfg = """
    !
interface gigaethernet 1/1/1
description subs-34161
switchport access vlan 2009
storm-control unknown-multicast pps 1024
storm-control dlf pps 1024
!
interface port-channel 1
description Po1
switchport trunk allowed vlan 7,14,16,19,33,35-38 confirm
switchport trunk allowed vlan add 1915,2019,2030
switchport mode trunk
switchport reject-frame untagged
!
"""
    expected = {
        "port-channel 1": {
            "mode": "trunk",
            "vlans": [7, 14, 16, 19, 33, 35, 36, 37, 38, 1915, 2019, 2030],
        },
        "gigaethernet 1/1/1": {"mode": "access", "vlans": [2009]},
    }
    assert parse_rc_intf(rc_cfg) == expected


def test_parse_dlink_intf():
    dlink_cfg = """
create vlan 11 tag 11
config vlan 11 add tagged 26-28 advertisement disable
create vlan vlan-52 tag 52
config vlan vlan-52 add tagged 14,26-28 advertisement disable
create vlan 114 tag 114
config vlan 114 add tagged 1,25-26
config vlan 114 add untagged 24 advertisement disable
"""
    expected = {
        1: {"tagged": [114]},
        14: {"tagged": [52]},
        24: {"untagged": 114},
        25: {"tagged": [114]},
        26: {"tagged": [11, 52, 114]},
        27: {"tagged": [11, 52]},
        28: {"tagged": [11, 52]},
    }
    assert parse_dlink_intf(dlink_cfg) == expected
