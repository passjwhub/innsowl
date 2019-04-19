# -*-coding:utf-8 -*-
import sys
import traceback
import getopt
import re
import json
import random
import socket
import time
import os

sys.path.append('.')
mswindows = (sys.platform == "win32")

def check_ip(str):
    Rst = 'True'
    cheIP = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    if not re.findall(cheIP, str):
        Rst = 'False'
    else:
        IPs = list(str.split('.'))
        # g_logger.info( 'IPs is ', IPs, len(IPs)
        for i in range(len(IPs)):
            try:
                if int(IPs[i]) > 255:
                    g_logger.info('bigger than 255 %s' % IPs[i])
                    Rst = 'False'
                else:
                    pass
            except ValueError as Emsg:
                g_logger.info(Emsg)
    return Rst, str
