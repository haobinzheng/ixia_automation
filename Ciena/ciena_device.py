class ciena_device():
    def __init__(*args,**kwargs):


def config_mgmt(self,*args,**kwargs):
    sample = f"""
    oc-if:interfaces interface 'mgmtbr0' config name "mgmtbr0" mtu 1500 description "bridge interface for out of band management port/local management interface" role cn-if:management type system
oc-if:interfaces interface 'mgmtbr0' ipv4 addresses address '10.132.10.113' config ip "10.132.10.113" prefix-length 24
dhcp-client client 'mgmtbr0' admin-enable false requested-lease-time 3600
dhcp-client client 'mgmtbr0' option-enable time-offset true router true domain-name-server true log-server true host-name true domain-name true ntp-servers true lease-time false tftp-server-name true bootfile-name true vivsi true
dhcpv6-client client 'mgmtbr0' admin-enable false
dhcpv6-client client 'mgmtbr0' option-enable
rib vrf 'default' ipv4 '0.0.0.0/0' next-hop '10.132.10.1' outgoing-interface-name "mgmtbr0"
""" 
