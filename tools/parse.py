"""parse"""


from ttp import ttp

ttp_template = """
{{ ip_addr }} {{ proto }} {{ port }} {{ timeout }} {{ retransmit }} {{ key }}
"""

cfg = """DGS-3200-10:4#show authen server_host      
Command: show authen server_host

IP Address       Protocol  Port   Timeout  Retransmit  Key
---------------  --------  -----  -------  ----------  -------------------------
94.232.215.29    RADIUS    1812   2        2           1qazZAQ!                 

Total Entries : 1"""


def find_auth_servers(config: str) -> list[str, ...]:
    parser = ttp(data=config, template=ttp_template)
    parser.parse()
    return parser.result(format="json")[0]


if __name__ == "__main__":
    print(find_auth_servers(cfg))
