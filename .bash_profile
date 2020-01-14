alias fgt1='telnet 10.105.50.1 2066'
alias fgt2='telnet 10.105.50.2 2074'
alias dut548_1='telnet 10.105.50.3 2057'
alias dut548_2='telnet 10.105.50.3 2056'
alias dut548_3='telnet 10.105.50.1 2075'
alias dut548_4='telnet 10.105.50.1 2078'
alias bgp1='telnet 10.105.241.144 2071'
alias bgp2='telnet 10.105.241.44 2066'
alias bgp3='telnet 10.105.240.44 2090'
alias bgp4='telnet 10.105.240.44 2007'
alias bgp5='telnet 10.105.240.144 2068'

# added by Anaconda3 5.2.0 installer
export PATH="/anaconda3/bin:$PATH"
export IXIA_HOME="/Ixia/ixos_8.50ea_ixnetwork_8.50ea_ixload_8.50ea/ixia"
export IXOS_API_HOME=${IXIA_HOME}/ixos-api/8.50.0.32/lib
export IXNETWORK_HOME=${IXIA_HOME}/ixnetwork/8.50.1501.9/lib
export HLT_HOME=${IXIA_HOME}/hlapi/8.50.1.13
export HLT_LIBRARY=${HLT_HOME}/library
export ixTclNetwork=${IXNETWORK_HOME}/TclApi
export ixTclNetwork=${IXNETWORK_HOME}/TclApi/IxTclNetwork
export IXLOAD_HOME=${IXIA_HOME}/ixload/8.50.0.465
export IXL_libs=${IXLOAD_HOME}
export ixLoadComm=${IXLOAD_HOME}/lib/comm
export SystemLibTcl="/System/Library/Tcl"
 
# The followings are for using ixNet low level APIs to interact with the Linux API server
# You will need to know where your tcl tls and http packages are installed and state the paths here.
export linuxApiServer=${ixTclNetwork}/LinuxApiServer

#export tclTls=/opt/ActiveTcl-8.5/./lib/teapot/package/linux-glibc2.3-x86_64/lib/tls1.6.4
#export tclHttp=/opt/ActiveTcl-8.5/lib/tcl8.5/http1.0

export IXIA_VERSION=8.50
# Uncomment this if using HLAPI IxExplorer
# IxOS + HLTAPI = HLTSET224,  HLTAPI + IxNetwork = HLTSET225 
#export IXIA_VERSION=HLTSET225

#export TCLLIBPATH="$IXOS_API_HOME $HLT_HOME $HLT_LIBRARY ${IXLOAD_HOME}/lib $ixLoadComm $ixTclNetwork $linuxApiServer $tclTls $tclHttp"
export TCLLIBPATH="$IXOS_API_HOME $HLT_HOME $HLT_LIBRARY ${IXLOAD_HOME}/lib $ixLoadComm $ixTclNetwork $linuxApiServer, $SystemLibTcl"

export PYTHONPATH="${HLT_HOME}/library/common/ixiangpf/python:${IXNETWORK_HOME}/PythonApi:${IXLOAD_HOME}/lib"
# The bottom line is for mpexpr if you don't have it. HLAPI requires it.
#export LD_LIBRARY_PATH=/opt/ixia/tcl/8.5.17.0/lib 


