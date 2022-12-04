"""Parse cfg module."""


from collections import defaultdict

ACCESS_INTF = "untagged"
TRUNK_INTF = "tagged"


def parse_rc_intf(cfg: str) -> dict[str, list[int]]:
    """
    Find vlans and interfaces on Raisecom cfg.

    Args:
        cfg: part of cfg file with vlans

    Returns:
        dict with interfaces and vlans
    """
    interfaces = {}
    for block in cfg.split("!"):
        if "interface" and "switchport" in block:
            vlans = ""
            for line in block.split("\n"):
                if "interface" in line:
                    intf = line.strip("interface ")
                elif "confirm" in line:
                    vlans += line.split()[-2]
                    mode = "trunk"
                elif "add" in line:
                    vlans += ","  # noqa: WPS336
                    vlans += line.split()[-1]
                elif "switchport access vlan" in line:
                    vlans += line.split()[-1]
                    mode = "access"
            vlan_list = []
            for vlan in vlans.split(","):
                if "-" in vlan:
                    start_vlan = int(vlan.split("-")[0])
                    end_vlan = int(vlan.split("-")[-1]) + 1
                    vlan_list.extend([vlan_id for vlan_id in range(start_vlan, end_vlan)])
                else:
                    vlan_list.append(int(vlan))

            interfaces.update({intf: {"mode": mode, "vlans": sorted(vlan_list)}})
    return interfaces


def parse_dlink_intf(cfg: str) -> dict[int, dict[str, list[int]]]:
    """
    Find vlans and interfaces on D-Link cfg.

    Args:
        cfg: part of cfg file with vlans

    Returns:
        dict with interfaces and vlans
    """
    interfaces: dict = defaultdict(dict)
    vlan_name_tag: dict[str, int] = {}
    for line in cfg.split("\n"):
        if "create vlan" in line:
            vlan_name = line.split()[2]
            vlan_id = int(line.split()[-1])
            vlan_name_tag.update({vlan_name: int(vlan_id)})
        elif "add tagged" in line:
            vlan_name = line.split()[2]
            ports = line.split()[5]
            vlan_id = vlan_name_tag[vlan_name]
            for intf in ports.split(","):
                if "-" in intf:
                    start_intf = int(intf.split("-")[0])
                    end_intf = int(intf.split("-")[-1]) + 1
                    for interface in range(start_intf, end_intf):
                        if interfaces[interface].get(TRUNK_INTF):
                            interfaces[interface][TRUNK_INTF].append(vlan_id)
                        else:
                            interfaces[interface][TRUNK_INTF] = []
                            interfaces[interface][TRUNK_INTF].append(vlan_id)
                else:
                    interface = int(intf)
                    if interfaces[interface].get(TRUNK_INTF):
                        interfaces[interface][TRUNK_INTF].append(vlan_id)
                    else:
                        interfaces[interface][TRUNK_INTF] = []
                        interfaces[interface][TRUNK_INTF].append(vlan_id)
        elif "add untagged" in line:
            vlan_name = line.split()[2]
            ports = line.split()[5]
            vlan_id = vlan_name_tag[vlan_name]
            interfaces[int(ports)] = {ACCESS_INTF: vlan_id}
    return interfaces


def find_common_vlans(
    vendor: str,
    cfg: str,
    target_intf: str,
) -> None:
    """Find common vlans between target interface and others.

    Args:
        vendor: vendor
        cfg: part of device`s config
        target_intf: target interface
    """
    if vendor == "rc":
        interfaces = parse_rc_intf(cfg)
    elif vendor == "dlink":
        interfaces = parse_dlink_intf(cfg)
    for interface, intf_values in interfaces.items():
        if interface == target_intf:
            continue
        common_vlans = set(interfaces[target_intf].get("tagged")) & set(
            intf_values.get("tagged", [intf_values.get("untagged")]),
        )
        if common_vlans:
            print(interface, common_vlans)


if __name__ == "__main__":
    vendor = "dlink"
    with open("cfg_dlink.txt") as fn:
        dev_cfg = fn.read()
    target_intf = 27
    find_common_vlans(vendor, dev_cfg, target_intf)
