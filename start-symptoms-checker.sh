#!/bin/bash

mkdir -p /datadrive/deepcare/symptoms-checker/log
touch /datadrive/deepcare/symptoms-checker/log/symptoms-checker-systemd.log
cd /datadrive/deepcare/symptoms-checker/
/usr/bin/python /datadrive/deepcare/symptoms-checker/app.py > /datadrive/deepcare/symptoms-checker/log/symptoms-checker-systemd.log 2>&1 > /dev/null
