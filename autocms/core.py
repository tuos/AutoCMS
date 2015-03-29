"""Common functions for AutoCMS components"""

import re 
import os
import time
import math
import datetime
import subprocess


def load_configuration(filename):
    """Return configuration dict from filename."""
    config = dict()
    with open(filename,'r') as file:
        config_raw = file.read().splitlines()
    for line in config_raw:
        if( re.match(r'export',line) ):
            key = line.split('=')[0]
            key = key.replace("export","")
            key = key.strip()
            val = line.split('=')[1]
            val = val.strip()
            val = val.strip('"')
            config[key] = val
    return config


def get_completed_jobs(config):
    """Query the slurm scheduler for completed job ids and return list."""
    cmd = ('/usr/scheduler/slurm/bin/sacct --state=CA,CD,F,NF,TO'
           ' -S $(date +%%Y-%%m-%%d -d @$(( $(date +%%s) - 172800 )) )'
           ' --accounts=%s --user=%s -n -o "jobid" | grep -e "^[0-9]* "' 
           % ( config['AUTOCMS_GNAME'], config['AUTOCMS_UNAME'] ))
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    lines = result.stdout.readlines()
    lines = map(str.strip,lines)
    return lines


