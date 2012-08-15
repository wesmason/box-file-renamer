#!/bin/bash

fileName=ipod:^ipad!.txt
match='[\:|\!|\^|\>|\<]'
replacement=\-
echo ${fileName//$match/$replacement}
