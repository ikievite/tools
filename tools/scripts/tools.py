from .intf_vlans import parse_rc_intf

interfaces = """
!
interface gigaethernet 1/1/2
description 116.63
switchport trunk allowed vlan 16,116 confirm
switchport mode trunk
switchport reject-frame untagged
storm-control unknown-multicast pps 1024
storm-control dlf pps 1024
!
"""


def main():
    for block in interfaces.split("!"):
        print(parse_rc_intf(block))


if __name__ == "__main__":
    main()
