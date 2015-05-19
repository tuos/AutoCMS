#!/bin/bash

#
# Trivial mockup of a scientific application,
# runs for some random interval, spits out garbage,
# and sometimes fails
#

KEEP_GOING=true

while [ "$KEEP_GOING" = true ]; do
    sleep $(( $RANDOM % 5 + 1 ))
    if [ $(( $RANDOM % 100 )) -eq 0 ]; then
        echo "Segmentation fault"
        exit 139
    fi
    FOO_VAL1=$(( $RANDOM % 2  ))
    FOO_VAL2=$(( $RANDOM % 10 + 9  ))
    FOO_VAL3=$(( $RANDOM % 6 + 1 ))
    echo "DLIST VALS: 0 $FOO_VAL1 $FOO_VAL1 A 0 0 $FOO_VAL2 1 $FOO_VAL3"
    if [ $(( $RANDOM % 50 )) -eq 0 ]; then
        echo "Unable to conserve momentum after 931 steps, giving up..."
        exit 1
    fi
    if [ $(( $RANDOM % 10 )) -eq 0 ]; then
        echo "Process converged after N iterations. Exiting."
        KEEP_GOING=false
    fi
done

exit 0
