def parse_rc_intf(cfg: str) -> dict[str, list[int]]:
    vlans = ""
    for line in cfg.split("\n"):
        if "interface" in line:
            intf = line.strip("interface ").strip()
        if "confirm" in line:
            vlans += line.split()[-2]
        if "add" in line:
            vlans += ","
            vlans += line.split()[-1]

    vlan_list = []

    for vlan in vlans.split(","):
        if "-" in vlan:
            start_vlan, end_vlan = vlan.split("-")
            start_vlan = int(start_vlan)
            end_vlan = int(end_vlan) + 1
            vlan_list.extend([vid for vid in range(start_vlan, end_vlan)])
        else:
            vlan_list.append(int(vlan))
    return {intf: sorted(vlan_list)}
