#!/bin/bash
# This will scp a scpecified junos file in to /var/tmp of a list of Juniper devices and do a "request system software add reboot"
# kundolyr@
echo "This script is to be run to upgrade JUnos in Catzilla devices as part of initial deployment , SHOULD NOT BE USED ON PRODUCTION DEVICES "
echo "THIS WILL REBOOT THE SWITCHES AGAINST WHICH THESE ARE RUN"
set +x
syntax() {
    echo
    echo "Usage: $0 [-h <hostnames_file>] [-f <firmware_file>]"
    echo
    echo "This script will copy an OS image to a specified list of devices"
    echo "within a Catzilla fabric and execute an OS upgrade command."
    echo "Works via ssh."
    echo "See comments in the source for more details."
    echo 
    echo "Mandatory Arguments"
    echo "  -h filename containing IPs/hostnames"
    echo "  -f filename of firmware"
    echo
    echo "Example: $0 -f junos_image.tgz -h hosts.txt"
    echo
    echo
}

# bail if we have no args
NUMARGS=$#
if test "$NUMARGS" < "2"; then
    syntax
    exit 1
fi

while getopts :h::f:h FLAG; do
    case $FLAG in
        h)  
            HOSTNAMES=$OPTARG
            ;;
        f)
            FIRMWARE=$OPTARG
            ;;
        h)
            syntax
            exit
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            syntax
            exit 1
            ;;
     esac
done

# credential-related stuff
SSHUSER="$(whoami)".sudo
COMMAND="request system software add /var/tmp/$FIRMWARE force-host reboot"
echo 'type your device (ec2/prod) password'
read -s password
SSHPASS="$password"

# do we really have a password?
if test "$SSHPASS" = ''; then
    echo "error."
    echo "We didn't get a password?  Aborting."
    exit 1
else
    echo "Got your password."
fi


while read host
do
[ -z $host ] && continue
# copy file to host
/usr/bin/expect << EOD
set timeout -1
spawn scp $FIRMWARE $host:/var/tmp/
sleep 1
expect {
    "(yes/no)?" {
        send "yes\r";
        exp_continue
    }
    "assword: " {
        send {$SSHPASS};
        send "\r";
        exp_continue
    }
    sleep 1
    expect eof
}
EOD


# update os on host
/usr/bin/expect << EOD
spawn ssh $SSHUSER@$host
sleep 1
expect {
    "(yes/no)?" {
        send "yes\r";
        exp_continue
    }
    "assword: " {
        send {$SSHPASS}; 
        send "\r";
        exp_continue
    }
}
set MULTIPROMPT {[>#$] }
sleep 1
expect {
    "$MULTIPROMPT" {
        send {$COMMAND};
        send "\r"
    }
}
sleep 1
expect eof
EOD
done < $HOSTNAMES
