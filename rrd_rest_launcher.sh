#!/bin/bash

######################################################################
# rrd_rest_launcher.sh
# 
# uses the rrd_rest_launcher in the OSHI-REST-server project
# ####################################################################


printandexec () {
		echo "$@"
		eval "$@"
}

printandexec /home/user/workspace/OSHI-REST-server/rrd_rest_launcher.sh

