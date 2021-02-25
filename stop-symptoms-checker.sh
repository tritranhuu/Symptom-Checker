#!/bin/bash

kill `ps -ef | grep symptoms-checker/app.py | grep -v grep | awk '{print $2}'`
