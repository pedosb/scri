#!/bin/bash

if [ $# != 1 ]; then
	echo "Usage $0: <file_name>"
	echo "<file_name> é o caminho para um arquivo com os valores dos sensores."
	exit -1
fi

./Main.py -v < $1 > p
java Main < $1 > j

./Voter.py -v -j j -p p
