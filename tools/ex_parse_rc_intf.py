from intf_vlans import parse_rc_intf

interfaces = """
!
interface gigaethernet 1/1/1
description subs-34161
switchport access vlan 2009
storm-control unknown-multicast pps 1024
storm-control dlf pps 1024
!
interface gigaethernet 1/1/2
description 116.63
switchport trunk allowed vlan 16,116 confirm
switchport trunk allowed vlan add 1515,1618,1705
switchport mode trunk
switchport reject-frame untagged
storm-control unknown-multicast pps 1024
storm-control dlf pps 1024
!
"""


def main():
    for block in interfaces.split("!"):
        if "interface" and "switchport" in block:
            print(parse_rc_intf(block))


if __name__ == "__main__":
    main()
