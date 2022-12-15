#!/bin/sh

i=2020
while [ $i -le 2024 ]
do
	nc -lvnp "$i" &
	i=$(( $i + 1 ))
done
