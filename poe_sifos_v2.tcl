psa 10.105.241.47
psa_4pair 5,1 single

Model                           SN                        APC                                                  Rack            Mgmt IP
Sifos PSL 3424L     3424006      10.105.241.146 port 12     9/07          10.105.241.49
Sifos PSL 3424L     3424005      10.105.241.146 port 11     9/04          10.105.241.48
Sifos PSA 3000     30002050A   10.105.241.97   port 17     6/03          10.105.241.47
 
 
Windows VMs with Sifos tools installed.
 
IP                         Crednetials
10.105.252.14   Adminstrator/Fortinet123!
10.105.252.23   Adminstrator/Fortinet123!
10.105.252.25   Adminstrator/Fortinet123!





proc psl_power_up {} {
	set port_list {"1,2","2,2","3,2","4,2","5,2","6,2","7,2","8,2" "9,2","10,2","11,2","12,2","13,2","14,2","15,2","16,2"}
	set power_list {13.7 3.9 6.7 13.7 28.7} 
    set class_list {0 1 2 3 4}
    set zipped [lmap a $class_list b $power_list {list $a $b}]
    puts $zipped

	regsub -all {(,")|(",)|"} $port_list " " port_list;
	puts $port_list
	puts $power_list
	for {set i 0} {$i < 1} {incr i} {
		foreach z $zipped {
            set class [lindex $z 0]
            puts $class
            set power [lindex $z 1]
            puts $power
			foreach port $port_list {
				# puts $port 
				# puts $power
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

proc at_power_up {} {
	set port_list {"1,1","6,1","7,1","8,1","9,1","10,1","11,1","12,1"}
	set power_list {60} 
	regsub -all {(,")|(",)|"} $port_list " " port_list;
	puts $port_list
	puts $power_list
	for {set i 0} {$i < 2} {incr i} {
		foreach power $power_list {
			foreach port $port_list {
				puts $port 
				puts $power
				puts "power_port $port c 6 p $power"
        		power_port $port c 6 p $power
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
	#set port_list {"5,1","6,1","7,1"}
    set power_list {13.7 3.9 6.7 13.7 28.7 43.7 57.3} 
    set class_list {0 1 2 3 4 5 6}
    set zipped [lmap a $class_list b $power_list {list $a $b}]
    puts $zipped
 	regsub -all {(,")|(",)|"} $port_list " " port_list;
	puts $port_list
	puts $power_list
	for {set i 0} {$i < 1} {incr i} {
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
  psa_4pair 5,1 single
  # Establish proper polarities & detection signatures for pairsets
  polarity 5,1 mdi+mdix
  passive 5,1 r 25 c 0
  # Establish Class Signture
  # Multi-Event signatures are not applied until Class Event #1
  # Class 6 will by default set 2mA mark load
  class 5,1 6
  # Configure the Current Trace to 2 second high resolution aperture
  # Arm the meter for an event trigger
  idctrace 5,1 trig ext period 2sx stat
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

 
proc lldp_t {} {	 
set port_list {"6,1" "7,1"}
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
	psa_lldp_trace $port period 10 duration 1
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
