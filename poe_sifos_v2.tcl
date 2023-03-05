******************* How to connect to a PSA chasssis? ***************************
psa <ip_addr>

************ PSA: How to define a slot as 4-pair port? ***************
psa_4pair 9,1 single -- single signature
psa_4pair 9,1 dual  -- dual signature
psa_4pair 9,1 disable  -- 2 pair mode 


************ PSA: How to test load for 803.3AT ********
psa_test_load 1,2 fast c 3 -force t 20

Class Min Load 		Max Load
0 		0.5 Watts		15.3 Watts 
1 		0.5 Watts		3.9 Watts
2 		0.5 Watts		6.9 Watts
3 		7.1 Watts		15.3 Watts
4 		15.5 Watts	29.8 Watts
5     40 Watts    51 Watts
6     51 Watts    60 Watts

psa_4pair 5,1 single
psa_test_load 3,2 fast c 0 -force t 20
psa_test_load 3,2 fast c 1 -force t 20
psa_test_load 3,2 fast c 2 -force t 20
psa_test_load 3,2 fast c 3 -force t 20
psa_test_load 3,2 fast c 4 -force t 20


************ PSA: How to power up a 4-pair port ********************
psa_4pair 5,1 single

************ PSA: How to source power from PSE port with 802.3bt standard?************
proc psa_bt {} {	 
set port_list {"5,1" "6,1" "7,1" "8,1" "9,1" "10,1" "11,1" "12,1"}
#set port_list {"7,1"}
foreach port $port_list {
	puts "psa_disconnect $port"
	psa_disconnect $port
	puts "psa_4pair $port single"
	psa_4pair $port single
	puts "psa_auto_port $port BT"
	psa_auto_port $port BT
	puts "power_bt $port c 4 p 30  "
 	power_bt $port c 4 p 30
}
}


**************PSA: How to basically power up 3AT ? ************************
proc psa_at {} {
set port_list {"1,2" "2,1" "2,2" "3,1" "3,2" "4,1" "4,2"}
foreach port $port_list {
	puts "psa_disconnect $port"
	psa_disconnect $port
	puts "psa_4pair $port disable"
	psa_4pair $port disable
	puts "psa_auto_port $port AT"
	psa_auto_port $port AT
	puts "alt $port A"
	alt $port A
	puts "power_port $port c 4 p 30"
	power_port $port c 4 p 30
	paverage $port period 500m stat
	# psa_disconnect 1,1
	# psa_check_lan_state 1,1
}
}

************ PSA: How to emulate 3AT PD quickly **********************
proc psa_at_emulate {} {
set port_list {"1,2" "2,1" "2,2" "3,1" "3,2" "4,1" "4,2"}
foreach port $port_list {
puts "psa_disconnect $port"
psa_disconnect $port
puts "psa_emulate_pd $port start c 4 p 25.5 o 5"
psa_emulate_pd $port start c 4 p 25.5 o 5
}
}


**************PSA: How to power up 3AT with LLDP ? ************************
proc psa_at_lldp {} {
set port_list {"1,2" "2,1" "2,2" "3,1" "3,2" "4,1" "4,2"}
foreach port $port_list {
	psa_disconnect $port
	puts "power_port $port c 4 p 37 lldp force 30 timeout 20"
	power_port $port c 4 p 37 lldp force 30 timeout 20
	paverage $port period 500m stat
	# psa_disconnect 1,1
	# psa_check_lan_state 1,1
}
}
*************** PSA: How to configure the PSA attributes? **************************

psa_pse -spec bt -grant phy+lldp 

psa_pse -grant phy+lldp
psa_pse -grant phy 

#Use psa_saveConfig to permanently save PSE Attribute settings: BT.
psa_saveConfig

******** PSA: How to emulate PD LLDP for 802.3BT? ******************

# Program Default LLDP Packet Parameters to ALL Test Ports 
pd_default_lldp 99,99

# Program Unique MAC Addresses to ALL Test Ports with specified 9-digit ROOT # Store these in non-volatile memory in each test port
pd_mac_init 99,99 root 00.4a.30.00.0 store Slot,Port 1,1 004A30000011

# Connect the LLDP Subsystem on all ports
psa_lan 99,99 connect


# Give the PSE Some Time to Link with PSA Test Ports
after 2000

# Program 802.3bt PD Power Request & Message Transmission Parameters to ALL Ports 

pd_req 99,99 sspwr 36.2 class 4 period 12 count 0 trig off init
pd_req 1,1 sspwr 36.2 class 4 period 12 count 0 trig off init


# Query the PD request configuration on port 2
pd_req 1,1 stat 
pd_req 1,2 stat 
pd_req 2,1 stat 
pd_req 2,2 stat 
pd_req 3,1 stat 
pd_req 3,2 stat 


**************** How to edumlate LLDP protocol for 802.3AT POE PD? *************
# Connect the LLDP Subsystem
psa_lan 1,1 connect
 
# Program LLDP Packet Parameters – Mostly Power-Up Defaults 
pd_lldp 1,1 lldpaddr 01.80.C2.00.00.0E ch_id 4 004a30000011 port_id 3 004a30000011
pd_lldp 1,1 ttl 120 vlan disable
# Query LLDP Packet 
pd_lldp 1,1 ?  

# Program PD MAC and PoE TLV Parameters
pd_frame 1,1 mac 00.4a.30.00.00.11
pd_frame 1,1 type 2 source pse priority high pwr_alloc echo 
# Query LLDP PoE Configuration
pd_frame 1,1 ?

# Program 802.3at PD Power Request and Message Transmission Parameters 
pd_req 1,1 pwr 22.2 class 4 period 15 count 0 trig off init

# Query PD LLDP Transmission Parameters
pd_req 1,1 ?
 
# Start PD LLDP Transmission 
pd_req 1,1 stat
 
 
 ************ PSA/PSL: How to trace a 3AT LLDP POE transaction *******************
proc lldp_trace {} {	 
set port_list {"1,1"}
puts $port_list
#regsub -all {(,")|(",)|"} $port_list " " port_list;
foreach port $port_list {
	#c: Capacitance Must be 0,5,7,11 uF
	puts $port
	passive $port r 25 c 0
	class $port 4
	port $port connect
	psa_lan $port connect
	pse_link_wait $port timeout 30
	pd_req $port class 4 pwr 24.3
	psa_lldp_trace $port period 10 duration 2
}
}



===================================== PSA Informaiton ======================================
psa 10.105.241.47
psa 10.105.241.49


Model                           SN                        APC                                                  Rack            Mgmt IP
Sifos PSL 3424L     3424006      10.105.241.146 port 12     9/07          10.105.241.49
Sifos PSL 3424L     3424005      10.105.241.146 port 11     9/04          10.105.241.48
Sifos PSA 3000     30002050A   10.105.241.97   port 17     6/03          10.105.241.47
 
 
Windows VMs with Sifos tools installed.
 
IP                         Crednetials
10.105.252.14   Adminstrator/Fortinet123!
10.105.252.23   Adminstrator/Fortinet123!
10.105.252.25   Adminstrator/Fortinet123!

proc capture_peak {} {
# Configure test port for valid signature 
passive 1,1 r 26 c 0
# Configure Vpeak Measurement
vdcpeak 1,1 trig on max period 200m timeout 10
# Sync to trailing edge of pre-detection pulse (uses Trigger 1 !)
psa_det_sync 1,1 falling level 2.5
# Setup trigger for Vvalid(Max) measurement
trig1 1,1 rising
# Connect the detection resistance by connecting the port switch
port 1,1 connect
# Recover the peak voltage of the detection pulse
set status [psa_wait 1,1 vdcpeak]
set VvalidMax [lindex $status 3]
# Force a power-down by opening port switch, setting load to zero
psa_disconnect 1,1 
# Configure the Time Interval Measurement
# Trigger level and polarity of falling at level 2 also used for sync
timint 1,1 start falling level 2 stop rising level 40 msec noisy
# Synchronize to the end of pre-detection pulse
psa_det_sync 1,1 falling level 2 noisy
# Connect the detection resistance by connecting the port switch
port 1,1 connect
# Recover the time from end of detection until power-up
set status [psa_wait 1,1 timint]
set Tpon [lindex $status 4]
puts "Vvalid_Max = $VvalidMax volts, Tpon = $Tpon msec"
}

proc psl_power_up {} {
	#set port_list {"1,2","2,2","3,2","4,2","5,2","6,2","7,2","8,2" "9,2","10,2","11,2","12,2","13,2","14,2","15,2","16,2"}
	#set port_list {"1,1","2,1","3,1","4,1","5,1","6,1","7,1","8,1" "9,1","10,1","11,1","12,1","13,1","14,1","15,1","16,1","17,1","18,1","19,1","20,1","21,1","22,1","23,1","24,1"}
    set port_list {"1,2","2,2","3,2","4,2","5,2","6,2","7,2","8,2" "9,2","10,2","11,2","12,2","13,2","14,2","15,2","16,2","17,2","18,2","19,2","20,2","21,2","22,2","23,2","24,2"}
	  set power_list {13.7 3.9 6.7 13.7 28.7} 
    set class_list {0 1 2 3 4}
    set zipped [lmap a $class_list b $power_list {list $a $b}]
    puts $zipped

	regsub -all {(,")|(",)|"} $port_list " " port_list;
	puts $port_list
	puts $power_list
	for {set i 0} {$i < 1000} {incr i} {
		foreach z $zipped {
            set class [lindex $z 0]
            puts $class
            set power [lindex $z 1]
            puts $power
			foreach port $port_list {
				# puts $port 
				# puts $power
				puts "psl_setup $port 2pA"
				psl_setup $port 2pA
				puts "power_pse $port c $class p $power"
        		set status [power_pse $port c $class p $power]
                puts $status
				puts "pstatus $port"
				set status [lindex [pstatus $port stat] 3]
				after 10
				puts $status
				#psa_disconnect $port
				puts "vdcaverage $port stat"	
				#vdcaverage $port
				set VportMaxR [lindex [vdcaverage $port stat] 3]	
				after 10
				puts $VportMaxR
				st_wait 5
  			}
		}
	}
}

proc psl_power_onoff {} {
# Configure all ports to 2-Pair Alt-A and define ports to power
psl_setup p99 2pA
set addrList "p1 p2 p3 p4 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24"
# Power 8 Ports to Class 3, 11.5 watts
set poweredPorts ""
foreach addr $addrList {
 set status [power_pse $addr c 3 p 11.5]
 if { [lindex $status 0] != "POWERED" } {
 puts "Test Port $addr FAILED TO POWER !"
 } else {
 puts "Test Port $addr Succeeded TO POWER !"
 lappend poweredPorts $addr
 }
}
puts "Ports $poweredPorts are powering 11.5W"
# Configure and arm Load Transients
foreach addr $poweredPorts {
 ptrans p99 i 400 short arm
}
# Disconnect Signatures to prevent re-powering
# and Fire All Transients
port p99 isolate
trigout p0
# Recover Port Power Status
set unpoweredPorts ""
foreach addr $poweredPorts {
 set status [lindex [pstatus $addr stat] 3]
 if { $status == "OFF" } {
 lappend unpoweredPorts $addr
 puts "$addr has been Unpowered!"
 }
}
puts "Ports that removed power with transient: $unpoweredPorts"
# Disconnect and shut down all ports
psa_disconnect p99
}

proc psl_change_load_4p {} {
# Load the PSE Attributes from a PSE Attributes file myBtPse
# This will describe PSE to PSA software and configure ports to 4-Pair mode
#psa_pse myBtPSE
# Emulate Dual Class 4 power-up to 20 W
power_pse p1 c 4D p 20
# Adjust load on Pairset A to 22W
psl_set_load p1,A p 22
# Adjust load on Pairset B to 29.5W
psl_set_load p1,B p 29.5
# Wait 3 seconds, then assess power on each pairset
st_wait 3
paverage p1 period 1s
paverage p1,A stat
paverage p1,B stat
psa_disconnect p1
}

power_pse 1,1 c 4 p 24 lldp_at force 24.3 timeout 15

proc psl_lldp_basic {} {
	set addrList "p1 p2 p3 p4 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24"
	foreach p1 $addrList {
	puts "power_pse $p1 c 4 p 24 lldp_at force 24.3 timeout 15"
	set status [power_pse $p1 c 4 p 24 lldp_at force 24.3 timeout 15]
	puts $status
	puts "paverage $p1 period 1s stat"
	set status [paverage $p1 period 1s stat]
	puts $status
	puts "psa_check_lan_state $p1"
	set status [psa_check_lan_state $p1]
	puts $status
	# puts "psa_disconnect $p1"
	# psa_disconnect $p1
	# psa_check_lan_state $p1
	}
}


proc psl_lldp_frames {} {
	set mac [pd_mac_init p99 root 00.4a.30.00.0 store]
	puts "Allocated MAC addresses:"
	puts $mac
	puts "!!! executing: psa_lan p1 lldp" 
	psa_lan p1 lldp	
	puts "!!! executing: pd_frame p1 type 2 source pse priority high pwr_alloc echo"
	pd_frame p1 type 2 source pse priority high pwr_alloc echo
	set poe_config [pd_frame p1 ?]
	after 10
	puts "pd_frame p1 ? output = "
	puts $poe_config
 	pd_req p1 pwr 22.2 class 4 period 15 count 0  
	#power_pse p1 c 3
	puts "!!! exectuing: pd_req p1 ?"
	set parameter [pd_req p1 ?]
	puts $parameter

	pse_link_wait p1 timeout 5
	pse_frame p1 start
	pse_lldp_wait p1 timeout 30
	puts "!!! executing: pse_frame p1 stat"
	set stat [pse_frame p1 stat]
	puts $stat
	puts "!!! executing: pse_lldp p1 stat"
	set stat [pse_lldp p1 stat]
	puts $stat 
}

proc psl_lldp_frames_all {} {
	set mac [pd_mac_init p99 root 00.4a.30.00.0 store]
	puts "Allocated MAC addresses:"
	puts $mac
	set addrList "p1 p2 p3 p4 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24"
	foreach port $addrList {
		puts "!!! executing: psa_lan $port lldp" 
		psa_lan $port lldp	
		puts "!!! executing: pd_frame $port type 2 source pse priority high pwr_alloc echo"
		pd_frame $port type 2 source pse priority high pwr_alloc echo
		set poe_config [pd_frame $port ?]
		after 10
		puts "pd_frame $port ? output = "
		puts $poe_config
		pd_req $port pwr 22.2 class 4 period 15 count 0  
		#power_pse $port c 3
		puts "!!! exectuing: pd_req $port ?"
		set parameter [pd_req $port ?]
		puts $parameter

		pse_link_wait $port timeout 5
		pse_frame $port start
		pse_lldp_wait $port timeout 30
		puts "!!! executing: pse_frame $port stat"
		set stat [pse_frame $port stat]
		puts $stat
		puts "!!! executing: pse_lldp $port stat"
		set stat [pse_lldp $port stat]
		puts $stat 
	}
}

proc psl_lldp_trace {} {	
set addrList "p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24"
#set addrList "p2 p3"
foreach p $addrList {
passive $p r 24
class $p 4
iload $p i 50
port $p connect
psa_lan $p lldp
set status [pse_link_wait $p timeout 15]
puts $status
pd_req $p class 4 pwr 24.3
psa_lldp_trace $p period 8 duration 1
}
}

proc at_power_up {} {
	set port_list {"1,1","6,1","7,1","8,1","9,1","10,1","11,1","12,1"}
	set port_list {"1,1","1,2","2,1","2,2","3,1","3,2","4,1","4,2"}
	set power_list {48} 
	regsub -all {(,")|(",)|"} $port_list " " port_list;
	puts $port_list
	puts $power_list
	for {set i 0} {$i < 2} {incr i} {
		foreach power $power_list {
			foreach port $port_list {
				puts $port 
				puts $power
				puts "power_port $port c 6 p $power"
        		power_bt $port c 4 p $power
				puts "pstatus $port"
				set status [lindex [pstatus $port stat] 3]
				after 10
				puts $status
				#pstatus $port
 				puts "power_check $port"
				power_check $port
				set state [power_check $port]
				after 10
				puts $state
				st_wait 5
				#psa_disconnect $port
				puts "vdcaverage $port stat"	
				#vdcaverage $port
				set VportMaxR [lindex [vdcaverage $port stat] 3]	
				after 10
				puts $VportMaxR
				st_wait 5
  			}
		}
	}
}

proc bt_power_basic {} {
	set port_list {"5,1","6,1","7,1","8,1","9,1","10,1","11,1","12,1"}
	set port_list {"9,1","10,1","11,1","12,1"}
    set power_list {13.7 3.9 6.7 13.7 28.7 43.7 57.3} 
    set class_list {0 1 2 3 4 5 6}
    set zipped [lmap a $class_list b $power_list {list $a $b}]
    puts $zipped
 	regsub -all {(,")|(",)|"} $port_list " " port_list;
	puts $port_list
	puts $power_list
	for {set i 0} {$i < 1000} {incr i} {
			foreach z $zipped {
                set class [lindex $z 0]
                puts $class
                set power [lindex $z 1]
                puts $power
                foreach port $port_list {
                    puts "power_bt $port c $class p $power"
                    set status [power_bt $port c $class p $power]
                    puts $status
                    puts "pstatus $port"
                    set status [lindex [pstatus $port stat] 3]
                    after 10
                    puts $status
                    puts "power_check $port"
                    power_check $port
                    set state [power_check 1,1]
                    after 10
                    puts $state
                    st_wait 5
                    #psa_disconnect $port
                    puts "vdcaverage $port stat"	
                    #vdcaverage $port
                    set VportMaxR [lindex [vdcaverage $port stat] 3]	
                    after 10
                    puts $VportMaxR
                    st_wait 5
  			}
		}
	}
}

#Capturing a Power-Up Current (Extended) Trace on Connection of Class 6 (Single Signature) PD
proc bt_power_current {} {
  # Estatblish 4-Pair Single Signature Connection (PD emulation)
  psa_4pair 9,1 single
  # Establish proper polarities & detection signatures for pairsets
  polarity 9,1 mdi+mdix
  passive 9,1 r 25 c 0
  # Establish Class Signture
  # Multi-Event signatures are not applied until Class Event #1
  # Class 6 will by default set 2mA mark load
  class 9,1 6
  # Configure the Current Trace to 2 second high resolution aperture
  # Arm the meter for an event trigger
  idctrace 1,1 trig ext period 2sx stat
  # Configure a Load Transient to simulate Inrush load and Steady State load (850mA)
  # Trigger transient on 39V at power-up
  itrans 5,1 i1 400 t1 80m i2 850 t2 hold trig1
  trig1 5,1 rising level 39 arm
  # Connect the port, arm multi-event class, and trigger the meter
  psa_connect 5,1 mevent trigout
  # Collect the current trace when completed
  set status [psa_wait 5,1 idctrace]
  set trace_result [lindex $status 4]
}

 
proc lldp_trace {} {	 
set port_list {"2,1"}
puts $port_list
#regsub -all {(,")|(",)|"} $port_list " " port_list;
foreach port $port_list {
	#c: Capacitance Must be 0,5,7,11 uF
	puts $port
	passive $port r 25 c 0
	class $port 4
	port $port connect
	psa_lan $port connect
	pse_link_wait $port timeout 15
	pd_req $port class 4 pwr 25
	psa_lldp_trace $port period 10 duration 2
}
}

proc lldp_m {} {
set port_list {"5,1","6,1","7,1","8,1","9,1","10,1","11,1","12,1"}	 
set power_list {60} 
regsub -all {(,")|(",)|"} $port_list " " port_list
foreach port $port_list {
	puts "power_bt $port lldp ad 51 c 6 ada 49 adb 50 timeout 100"
	power_bt $port lldp ad 51 c 6 ada 49 adb 50 timeout 100
}
}
