from tools.intf_vlans import parse_rc_intf


def test_parse_rc_intf():
    data = """
!
interface gigaethernet 1/1/1
description subs-34161
switchport access vlan 2009
storm-control unknown-multicast pps 1024
storm-control dlf pps 1024
!
"""
    expected = {'gigaethernet 1/1/1': {'mode': 'access', 'vlans': [2009]}}
    assert parse_rc_intf(data) == expected