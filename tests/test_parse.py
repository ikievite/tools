"""Tests for parse module."""


from tools.parse import find_auth_servers

"""
DGS-3200-10:4#show authen server_host      
Command: show authen server_host

IP Address       Protocol  Port   Timeout  Retransmit  Key
---------------  --------  -----  -------  ----------  -------------------------
94.232.215.29    RADIUS    1812   2        2           1qazZAQ!                 

Total Entries : 1


DGS-3000-10TC:admin#show authen server_host      
Command: show authen server_host

IP Address           Protocol Port  Timeout Retransmit Key                    
-------------------- -------- ----- ------- ---------- -----------------------
94.232.215.29        RADIUS   1812  2       2          1qazZAQ!               
100.64.0.10          RADIUS   1812  2       2          1qazZAQ!               


Total Entries : 2

DES-3526:admin#show authen server_host     
Command: show authen server_host

IP Address       Protocol  Port   Timeout  Retransmit  Key
---------------  --------  -----  -------  ----------  -------------------------
94.232.215.29    RADIUS    1812   2        2           1qazZAQ!                 
192.168.254.10   RADIUS    1812   2        2           1qazZAQ!                 

Total Entries : 2

DES-3028:5#show authen server_host      
Command: show authen server_host

IP Address       Protocol  Port   Timeout  Retransmit  Key
---------------  --------  -----  -------  ----------  -------------------------
94.232.215.29    RADIUS    1812   2        2           1qazZAQ!                 

Total Entries : 1

DES-3200-26:admin#show authen server_host      
Command: show authen server_host

IP Address           Protocol Port  Timeout Retransmit Key                    
-------------------- -------- ----- ------- ---------- -----------------------
94.232.215.29        RADIUS   1812  2       2          1qazZAQ!               


Total Entries : 1
"""


def test_find_auth_servers():
    cfg = """DGS-3200-10:4#show authen server_host      
Command: show authen server_host

IP Address       Protocol  Port   Timeout  Retransmit  Key
---------------  --------  -----  -------  ----------  -------------------------
94.232.215.29    RADIUS    1812   2        2           1qazZAQ!                 

Total Entries : 1
"""
    expected = ["94.232.215.29"]
    assert find_auth_servers(cfg) == expected
