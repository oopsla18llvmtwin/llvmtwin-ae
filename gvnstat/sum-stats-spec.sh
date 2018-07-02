#!/bin/bash

if  [ "$#" -ne 1 ]; then
  echo "sum-stat.sh <SPEC CPU2017 results dir(absolute)>"
  exit 1
fi

LABELS[0]="Number_of_equalities_propagated" # NumGVNEqProp" # # of replacement according to comparison result
LABELS[1]="Number_of_pointer_equalities_propagated" #"NumGVNPtrEqProp"
LABELS[2]="Number_of_logical_deref_pointer_equalities_propagated"
LABELS[3]="Number_of_same_base_logical_pointer_equalities_propagated"
LABELS[4]="Number_of_null_pointer_equalities_propagated"
COUNTS[0]=0
COUNTS[1]=0
COUNTS[2]=0
COUNTS[3]=0
COUNTS[4]=0

for i in `find $1 -name 'CPU2017*.log'` ; do 
  echo $i
  for idx in {0..4} ; do
    #echo "[${LABELS[idx]}]"
    grep "${LABELS[idx]}" $i > _tmp.txt
    while read -r line ; do
      echo $line
      NUM=`echo $line | cut -d" " -f1`
      #echo $NUM
      ADDED=$((COUNTS[idx] + NUM))
      #echo $ADDED
      COUNTS[$idx]=${ADDED}
    done < _tmp.txt
  done
  for idx in {0..4} ; do
    echo ${LABELS[idx]}: ${COUNTS[idx]}
  done
done

