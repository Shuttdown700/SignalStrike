# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 22:41:42 2024

@author: shuttdown
"""

import subprocess as sp
import re
import time

wt = 5 # Wait time -- I purposefully make it wait before the shell command
accuracy = 3 #Starting desired accuracy is fine and builds at x1.5 per loop

while True:
    time.sleep(wt)
    pshellcomm = ['powershell']
    pshellcomm.append('add-type -assemblyname system.device; '\
                      '$loc = new-object system.device.location.geocoordinatewatcher;'\
                      '$loc.start(); '\
                      'while(($loc.status -ne "Ready") -and ($loc.permission -ne "Denied")) '\
                      '{start-sleep -milliseconds 100}; '\
                      '$acc = %d; '\
                      'while($loc.position.location.horizontalaccuracy -gt $acc) '\
                      '{start-sleep -milliseconds 100; $acc = [math]::Round($acc*1.5)}; '\
                      '$loc.position.location.latitude; '\
                      '$loc.position.location.longitude; '\
                      '$loc.position.location.horizontalaccuracy; '\
                      '$loc.stop()' %(accuracy))

    #Remove >>> $acc = [math]::Round($acc*1.5) <<< to remove accuracy builder
    #Once removed, try setting accuracy = 10, 20, 50, 100, 1000 to see if that affects the results
    #Note: This code will hang if your desired accuracy is too fine for your device
    #Note: This code will hang if you interact with the Command Prompt AT ALL 
    #Try pressing ESC or CTRL-C once if you interacted with the CMD,
    #this might allow the process to continue

    p = sp.Popen(pshellcomm, stdin = sp.PIPE, stdout = sp.PIPE, stderr = sp.STDOUT, text=True)
    (out, err) = p.communicate()
    out = re.split('\n', out)
    print(out)