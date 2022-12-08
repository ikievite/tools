"""Parse cfg module."""


from collections import defaultdict
from operator import itemgetter

ACCESS_INTF = "untagged"
TRUNK_INTF = "tagged"
VLANS_AT_LINE = 32

TRUNK_INTF_TEMPLATE = """interface giga 1/1/{intf_num}
 switchport trunk allowed vlan {vlans} conf
 switchport mode trunk
 switchport reject-frame untagged
 storm-control unknown-multicast pps 1024
 storm-control dlf pps 1024"""

ACCESS_INTF_TEMPLATE = """interface giga 1/1/{intf_num}
 switchport access vlan {vlan}
 storm-control unknown-multicast pps 1024
 storm-control dlf pps 1024"""


def parse_rc_intf(cfg: str) -> dict[str, dict[str, list[int]]]:
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
        common_vlans = set(interfaces[target_intf]["vlans"]) & set(intf_values["vlans"])
        # common_vlans = set(interfaces[target_intf].get("tagged")) & set(
        #    intf_values.get("tagged", [intf_values.get("untagged")]),
        # )
        if common_vlans:
            print(interface, common_vlans)


def make_vlan_range(vlan_list: list[int, ...], step, vlan_range) -> list[str, ...]:
    """Make vlan range from vlan list.

    Args:
        vlan_list: list with vlans
        step: step
        vlan_range: vlan range

    Returns:
        list with vlan ranges"""
    step += 1
    first_vlan = vlan_list[0]
    if len(vlan_list) == 1:
        return vlan_range.append(str(first_vlan))
    next_vlan = vlan_list[step]
    if first_vlan + step == next_vlan:
        make_vlan_range(vlan_list, step, vlan_range)
    vlan_range.append(f"{first_vlan}-{first_vlan+step-1}")
    vlan_list = vlan_list[step:]
    step = 0
    make_vlan_range(vlan_list, step, vlan_range)


def gen_rc_intf_cfg(dev_vars: dict) -> str:
    """Generate interface configuration for Raisecom switches.

    Args:
        dev_vars: dict with intf_vars

    Returns:
        interface cfg
    """
    config = []
    all_vlans = []
    for intf_num, intf_values in sorted(dev_vars.items(), key=itemgetter(0)):
        tagged_vlans = intf_values.get(TRUNK_INTF)
        untagged_vlan = intf_values.get(ACCESS_INTF)
        if tagged_vlans:
            all_vlans.extend(tagged_vlans)
            if len(tagged_vlans) >= VLANS_AT_LINE:
                vlan_chunks = [
                    tagged_vlans[vid : vid + VLANS_AT_LINE]
                    for vid in range(0, len(tagged_vlans), VLANS_AT_LINE)
                ]
                vlan_confirmed = vlan_chunks[0]
                vlan_added = vlan_chunks[1:]
                vlans = ",".join([str(vid) for vid in vlan_confirmed])
                intf_cfg = TRUNK_INTF_TEMPLATE.format(intf_num=intf_num, vlans=vlans)

                for vlan_chunk in vlan_added:
                    vlans = ",".join([str(vid) for vid in vlan_chunk])
                    insert_position = intf_cfg.find(" switchport mode trunk")
                    intf_cfg = (
                        intf_cfg[:insert_position]
                        + " switchport trunk allowed vlan add {vlans}\n".format(vlans=vlans)
                        + intf_cfg[insert_position:]
                    )
                config.append(intf_cfg)
            else:
                vlans = ",".join([str(vid) for vid in tagged_vlans])
                config.append(
                    TRUNK_INTF_TEMPLATE.format(intf_num=intf_num, vlans=vlans),
                )
        elif untagged_vlan:
            all_vlans.append(untagged_vlan)
            config.append(
                ACCESS_INTF_TEMPLATE.format(intf_num=intf_num, vlan=untagged_vlan),
            )
    all_vlans = list(set(all_vlans))
    if len(all_vlans) >= VLANS_AT_LINE:
        all_vlans = [
            all_vlans[vid : vid + VLANS_AT_LINE] for vid in range(0, len(all_vlans), VLANS_AT_LINE)
        ]
    for vlan_chunk in all_vlans:
        vlans = ",".join([str(vid) for vid in vlan_chunk])
        config.insert(0, f"create vlan {vlans} active")
    return "\n".join(config)


if __name__ == "__main__":
    vendor = "rc"
    filename = "cfg_dlink.txt"
    with open(filename) as fn:
        dev_cfg = fn.read()
    dev_vars = parse_dlink_intf(dev_cfg)
    print(gen_rc_intf_cfg(dev_vars))
    # v = [10, 11, 12, 20, 22]
    # print(make_vlan_range(v, 0, []))
