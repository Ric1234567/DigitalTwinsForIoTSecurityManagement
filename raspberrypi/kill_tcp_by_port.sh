#!/bin/sh

i=2020
while [ $i -le 2024 ]
do
        sudo fuser -k $i/tcp &
        i=$(( $i + 1 ))
done
