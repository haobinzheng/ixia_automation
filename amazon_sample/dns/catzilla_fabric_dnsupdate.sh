#! /bin/bash
if [ $# -ne 5 ]; then
    echo
    echo -e "\tThis script generates the config files needed to update the DNS entries for the Catzilla Fabric rotuers."
    echo
    echo -e "\tThis script expects exactly 5 parameters, in this order:"
    echo -e '\t1. the site name, for example "iad7"'
    echo -e "\t2. The number of the first brick rack for which you want to use the script for "
    echo -e "\t3. The number of the last brick rack for which you want to use the script for"
    echo -e "\t4. The number of the first spine rack for which you want to use the script for"
    echo -e "\t5. The number of the last spine rack for which you want to use the script for"
    echo
    echo -e "\tFor example:"
    echo -e "\t$0 iad7 1 3 1 1"
    echo
else
SITE=$1
REGION=$(echo $SITE | cut -c1,2,3)
FirstBrickRouter=$2
LastBrickRouter=$3
FirstSpineRouter=$4
LastSpineRouter=$5
FOLDER=$(echo $SITE-dns | tr "[:upper:]" "[:lower:]")
CURRDIR=$( cd "$(dirname "$0")" ; pwd)
CHECK_DNS='check_dns_fab.sh'
echo "###############################################"
echo The Site is: $SITE
echo The Output files will be exist in ~/$FOLDER-DNS
echo Thanks
echo "###############################################"
mkdir -p ~/$FOLDER
cd ~/$FOLDER
rm *
# Add bin bash in $CHECK_DNS outside of for loop
echo "#!/bin/bash" >> $CHECK_DNS
# Fabric switches for Bricks
for ((c=$FirstBrickRouter; c<=$LastBrickRouter; c++))
do
  for ((e=1; e<=2; e++))
   do
    for ((d=1; d<=16; d++))
      do
         fabaddr=$(grep "TIER$e.*MANAGEMENTIP" $CURRDIR/../../../../targetspec/border/$SITE-br-ctz-f1b$c/$SITE-br-ctz-f1b$c-fabric.attr | awk '{ print $3,$4,$6 }' | sort  -t 'r' -nk2 | awk '{ print $3 }' | sed -n ''$d'p')
         echo "The routers we are on: $SITE-br-ctz-f1b$c-t$e-r$d""-->""$fabaddr"
         IFS='.' read -ra ADDRESS <<< "$fabaddr"
         declare -i tlen
         tlen=${#ADDRESS[@]}
         reverseaddr=${ADDRESS[$tlen-1]}.${ADDRESS[$tlen-2]}.${ADDRESS[$tlen-3]}.${ADDRESS[$tlen-4]}
         echo delete, $reverseaddr.in-addr.arpa, 900, PTR, freeip.amazon.com >> fabricreversednsdelete
         echo add, $SITE-br-ctz-f1b$c-t$e-r$d.$REGION.amazon.com, 900, A, $fabaddr >> fabricforwarddnsadd
         echo add, $reverseaddr.in-addr.arpa, , PTR, $SITE-br-ctz-f1b$c-t$e-r$d.$REGION.amazon.com >> fabricreversednsadd
         # check dns
         echo printf \"Checking $SITE-br-ctz-f1b$c-t$e-r$d.$REGION.amazon.com \" >> $CHECK_DNS
         echo "host $SITE-br-ctz-f1b$c-t$e-r$d.$REGION.amazon.com > $CHECK_DNS.out" >> $CHECK_DNS
         echo "if egrep -q $fabaddr $CHECK_DNS.out;then" >> $CHECK_DNS
         echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
         echo else >> $CHECK_DNS
         echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
         echo fi >> $CHECK_DNS
         # check reverse dns
         echo printf \"Checking $fabaddr \" >> $CHECK_DNS
         echo "host $fabaddr > $CHECK_DNS.out" >> $CHECK_DNS
         echo "if egrep -q $SITE-br-ctz-f1b$c-t$e-r$d.$REGION.amazon.com. $CHECK_DNS.out;then" >> $CHECK_DNS
         echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
         echo else >> $CHECK_DNS
         echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
         echo fi >> $CHECK_DNS
       done
    done
 done
# Fabric switches for Spines (if spine is '0' then this is a microCatzilla).
if [ $FirstSpineRouter -ne 0 ] &&[  $LastSpineRouter -ne 0 ]; then
 for ((c=$FirstSpineRouter; c<=$LastSpineRouter; c++))
  do
   for ((d=1; d<=16; d++))
    do
     fabaddr=$(grep 'TIER3.*MANAGEMENTIP' $CURRDIR/../../../../targetspec/border/$SITE-br-ctz-f1s$c/$SITE-br-ctz-f1s$c-fabric.attr | awk '{ print $3,$4,$6 }' | sort  -t 'r' -nk2 | awk '{ print $3 }' | sed -n ''$d'p')
     echo "The router we are on: $SITE-br-ctz-f1s$c-t3-r$d""-->""$fabaddr"
     if [[ ! -z "$fabaddr" ]]; then
       IFS='.' read -ra ADDRESS <<< "$fabaddr"
       declare -i tlen
       tlen=${#ADDRESS[@]}
       reverseaddr=${ADDRESS[$tlen-1]}.${ADDRESS[$tlen-2]}.${ADDRESS[$tlen-3]}.${ADDRESS[$tlen-4]}
       echo delete, $reverseaddr.in-addr.arpa, 900, PTR, freeip.amazon.com >> fabricreversednsdelete
       echo add, $SITE-br-ctz-f1s$c-t3-r$d.$REGION.amazon.com, 900, A, $fabaddr >> fabricforwarddnsadd
       echo add, $reverseaddr.in-addr.arpa, , PTR, $SITE-br-ctz-f1s$c-t3-r$d.$REGION.amazon.com >> fabricreversednsadd
       # check dns
       echo printf \"Checking $SITE-br-ctz-f1s$c-t3-r$d.$REGION.amazon.com \" >> $CHECK_DNS
       echo "host $SITE-br-ctz-f1s$c-t3-r$d.$REGION.amazon.com > $CHECK_DNS.out" >> $CHECK_DNS
       echo "if egrep -q $fabaddr $CHECK_DNS.out;then" >> $CHECK_DNS
       echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
       echo else >> $CHECK_DNS
       echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
       echo fi >> $CHECK_DNS
       # check reverse dns
       echo printf \"Checking $fabaddr \" >> $CHECK_DNS
       echo "host $fabaddr > $CHECK_DNS.out" >> $CHECK_DNS
       echo "if egrep -q $SITE-br-ctz-f1s$c-t3-r$d.$REGION.amazon.com. $CHECK_DNS.out;then" >> $CHECK_DNS
       echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
       echo else >> $CHECK_DNS
       echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
       echo fi >> $CHECK_DNS
     fi
    done
  done
 fi
fi
#append $CHECK_DNS.out removal
echo rm -fr $CHECK_DNS.out >> $CHECK_DNS
