#! /bin/bash


if [ $# -ne 5 ]; then
    echo
    echo -e "\tThis script generates the config files needed to update the DNS entries for the Catzilla MGMT rotuers."
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
CHECK_DNS='check_dns_mgmt.sh'
echo "###############################################"
echo The Site is: $SITE
echo The Output files will be exist in ~/$FOLDER-DNS
echo Thanks
echo "###############################################"
mkdir -p ~/$FOLDER
cd ~/$FOLDER

# Add bin bash in $CHECK_DNS outside of for loop
echo "#!/bin/bash" >> $CHECK_DNS

# Management Brick Top Of Rack switches 
for ((c=$FirstBrickRouter; c<=$LastBrickRouter; c++))
do
  for ((d=1; d<=2; d++))
  do
    echo "The router we are on: $SITE-br-ctz-f1mgmt-b$c-r$d"
    if mgaddr=$(grep '^PRIMARYIP' $CURRDIR/../../../../targetspec/border/catzilla/$SITE-br-ctz-f1mgmt-b$c-r$d/routerspecific.attr | tr -d 'PRIMARYIP '); then
      IFS='.' read -ra ADDRESS <<< "$mgaddr"
      #for i in "${ADDRESS[@]}"
      #do
      #echo $i
      #done
      declare -i tlen
      tlen=${#ADDRESS[@]}
      #echo $tlen
      #echo ${ADDRESS[$tlen-1]}
      #echo $consol0000
      reverseaddr=${ADDRESS[$tlen-1]}.${ADDRESS[$tlen-2]}.${ADDRESS[$tlen-3]}.${ADDRESS[$tlen-4]}
  
      echo delete, $reverseaddr.in-addr.arpa, 900, PTR, freeip.amazon.com >> mgmtreversednsdelete
  
      echo add, $SITE-br-ctz-f1mgmt-b$c-r$d.$REGION.amazon.com, 900, A, $mgaddr >> mgmtforwarddnsadd
      echo add, $reverseaddr.in-addr.arpa, , PTR, $SITE-br-ctz-f1mgmt-b$c-r$d.$REGION.amazon.com >> mgmtreversednsadd

      echo printf \"Checking $SITE-br-ctz-f1mgmt-b$c-r$d.$REGION.amazon.com \" >> $CHECK_DNS
      echo "host $SITE-br-ctz-f1mgmt-b$c-r$d.$REGION.amazon.com > $CHECK_DNS.out" >> $CHECK_DNS
      echo "if egrep -q $mgaddr $CHECK_DNS.out;then" >> $CHECK_DNS
      echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
      echo else >> $CHECK_DNS
      echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
      echo fi >> $CHECK_DNS

      echo printf \"Checking $mgaddr \" >> $CHECK_DNS
      echo "host $mgaddr > $CHECK_DNS.out" >> $CHECK_DNS
      echo "if egrep -q $SITE-br-ctz-f1mgmt-b$c-r$d.$REGION.amazon.com. $CHECK_DNS.out;then" >> $CHECK_DNS
      echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
      echo else >> $CHECK_DNS
      echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
      echo fi >> $CHECK_DNS
    fi
   done
 done

# Management Spine Top Of Rack switches (if spine is '0' then this is micro).
if [ $FirstSpineRouter -ne 0 ] &&[  $LastSpineRouter -ne 0 ]; then
    for ((c=$FirstSpineRouter; c<=$LastSpineRouter; c++))
    do
        echo "The router we are on: $SITE-br-ctz-f1mgmt-s$c-r1"
        mgaddr=$(grep '^PRIMARYIP' $CURRDIR/../../../../targetspec/border/catzilla/$SITE-br-ctz-f1mgmt-s$c-r1/routerspecific.attr | tr -d 'PRIMARYIP ')
        if [[ ! -z "$mgaddr" ]]; then
          IFS='.' read -ra ADDRESS <<< "$mgaddr"
          #for i in "${ADDRESS[@]}"
          #do
          #echo $i
          #done
         declare -i tlen
          tlen=${#ADDRESS[@]}
          #echo $tlen
          #echo ${ADDRESS[$tlen-1]}
          #echo $consol0000
          reverseaddr=${ADDRESS[$tlen-1]}.${ADDRESS[$tlen-2]}.${ADDRESS[$tlen-3]}.${ADDRESS[$tlen-4]}

          echo delete, $reverseaddr.in-addr.arpa, 900, PTR, freeip.amazon.com >> mgmtreversednsdelete

          echo add, $SITE-br-ctz-f1mgmt-s$c-r1.$REGION.amazon.com, 900, A, $mgaddr >> mgmtforwarddnsadd
          echo add, $reverseaddr.in-addr.arpa, , PTR, $SITE-br-ctz-f1mgmt-s$c-r1.$REGION.amazon.com >> mgmtreversednsadd

          echo printf \"Checking $SITE-br-ctz-f1mgmt-s$c-r1.$REGION.amazon.com \" >> $CHECK_DNS
          echo "host $SITE-br-ctz-f1mgmt-s$c-r1.$REGION.amazon.com > $CHECK_DNS.out" >> $CHECK_DNS
          echo "if egrep -q $mgaddr $CHECK_DNS.out;then" >> $CHECK_DNS
          echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
          echo else >> $CHECK_DNS
          echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
          echo fi >> $CHECK_DNS

          echo printf \"Checking $mgaddr \" >> $CHECK_DNS
          echo "host $mgaddr > $CHECK_DNS.out" >> $CHECK_DNS
          echo "if egrep -q $SITE-br-ctz-f1mgmt-s$c-r1.$REGION.amazon.com. $CHECK_DNS.out;then" >> $CHECK_DNS
          echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
          echo else >> $CHECK_DNS
          echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
          echo fi >> $CHECK_DNS
        fi
    done
fi

# Management AGG's switches
for ((d=1; d<=2; d++))
do
  echo "The router we are on: $SITE-br-ctz-f1mgmt-agg-r$d"
  if mgaddr=$(grep '^PRIMARYIP' $CURRDIR/../../../../targetspec/border/catzilla/$SITE-br-ctz-f1mgmt-agg-r$d/routerspecific.attr | tr -d 'PRIMARYIP '); then
    IFS='.' read -ra ADDRESS <<< "$mgaddr"
    #for i in "${ADDRESS[@]}"
    #do
    #echo $i
    #done
    declare -i tlen
    tlen=${#ADDRESS[@]}
    #echo $tlen
    #echo ${ADDRESS[$tlen-1]}
    #echo $consol0000
    reverseaddr=${ADDRESS[$tlen-1]}.${ADDRESS[$tlen-2]}.${ADDRESS[$tlen-3]}.${ADDRESS[$tlen-4]}
    echo delete, $reverseaddr.in-addr.arpa, 900, PTR, freeip.amazon.com >> mgmtreversednsdelete
    echo add, $SITE-br-ctz-f1mgmt-agg-r$d.$REGION.amazon.com, 900, A, $mgaddr >> mgmtforwarddnsadd
    echo add, $reverseaddr.in-addr.arpa, , PTR, $SITE-br-ctz-f1mgmt-agg-r$d.$REGION.amazon.com >> mgmtreversednsadd
    echo printf \"Checking $SITE-br-ctz-f1mgmt-agg-r$d.$REGION.amazon.com \" >> $CHECK_DNS
    echo "host $SITE-br-ctz-f1mgmt-agg-r$d.$REGION.amazon.com > $CHECK_DNS.out" >> $CHECK_DNS
    echo "if egrep -q $mgaddr $CHECK_DNS.out;then" >> $CHECK_DNS
    echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
    echo else >> $CHECK_DNS
    echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
    echo fi >> $CHECK_DNS
    echo printf \"Checking $mgaddr \" >> $CHECK_DNS
    echo "host $mgaddr > $CHECK_DNS.out" >> $CHECK_DNS
    echo "if egrep -q $SITE-br-ctz-f1mgmt-agg-r$d.$REGION.amazon.com. $CHECK_DNS.out;then" >> $CHECK_DNS
    echo '    printf " - \e[32mPass\e[0m\n"' >> $CHECK_DNS
    echo else >> $CHECK_DNS
    echo '    printf " - \e[31mFail\e[0m\n"' >> $CHECK_DNS
    echo fi >> $CHECK_DNS
  fi
done
fi

#append $CHECK_DNS.out removal
echo rm -fr $CHECK_DNS.out >> $CHECK_DNS
