#! /usr/bin/bash

echo "Starting daemon..."

osqueryd --config_path=/home/pi/osquery/daemon/daemon_config.conf
