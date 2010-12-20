#!/bin/bash

for i in 1 2 3 4
do
	python3.2 dmut/client/slave.py localhost:8001 localhost:8000 &
done
