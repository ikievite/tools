from tools.autonet import find_ipaddresses

intf_cfg = """{
    "configuration" : {
        "@" : {
            "junos:commit-seconds" : "1673011064",
            "junos:commit-localtime" : "2023-01-06 15:17:44 EET",
            "junos:commit-user" : "user_x"
        },
        "interfaces" : {
            "interface" : [
            {
                "name" : "et-0/0/1",
                "description" : "sw1 port2",
                "gigether-options" : {
                    "ieee-802.3ad" : {
                        "bundle" : "ae4"
                    }
                }
            },
            {
                "name" : "et-0/0/2",
                "description" : "a1",
                "flexible-vlan-tagging" : [null],
                "mtu" : 13312,
                "encapsulation" : "flexible-ethernet-services",
                "unit" : [
                {
                    "name" : 100,
                    "encapsulation" : "vlan-bridge",
                    "vlan-id" : 100
                },
                {
                    "name" : 200,
                    "vlan-id" : 200,
                    "family" : {
                        "inet" : {
                            "address" : [
                            {
                                "name" : "10.12.12.2/24"
                            }
                            ]
                        }
                    }
                }
                ]
            },
            {
                "name" : "ae123",
                "flexible-vlan-tagging" : [null],
                "mtu" : 13312,
                "encapsulation" : "flexible-ethernet-services",
                "unit" : [
                {
                    "name" : 10,
                    "description" : "unit10",
                    "proxy-arp" : [null],
                    "vlan-id" : 10,
                    "family" : {
                        "inet" : {
                            "unnumbered-address" : {
                                "source" : "lo0.0",
                                "preferred-source-address" : "10.24.1.254"
                            }
                        }
                    }
                },
                {
                    "name" : 12,
                    "description" : "unit12",
                    "vlan-id" : 12,
                    "family" : {
                        "inet" : {
                            "address" : [
                            {
                                "name" : "192.168.12.1/24"
                            }
                            ]
                        }
                    }
                },
                {
                    "name" : 15,
                    "description" : "unit15",
                    "vlan-id" : 15,
                    "family" : {
                        "inet" : {
                            "address" : [
                            {
                                "name" : "10.87.17.1/24",
                                "preferred" : [null]
                            },
                            {
                                "name" : "10.87.19.1/24"
                            }
                            ]
                        }
                    }
                }
                ]
            },
            {
                "name" : "lo0",
                "unit" : [
                {
                    "name" : 0,
                    "family" : {
                        "inet" : {
                            "address" : [
                            {
                                "name" : "10.24.1.250/32"
                            },
                            {
                                "name" : "10.24.1.254/32",
                                "primary" : [null]
                            }
                            ]
                        }
                    }
                }
                ]
            }
            ]
        }
    }
}"""


def test_find_ipaddresses():
    expected = [
        "10.12.12.2/24",
        "192.168.12.1/24",
        "10.87.17.1/24",
        "10.24.1.250/32",
        "10.24.1.254/32",
    ]
    assert find_ipaddresses(intf_cfg) == expected
