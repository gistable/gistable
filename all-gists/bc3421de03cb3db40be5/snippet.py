# coding: utf-8
import os

def is_device_jailbroken():
    try:
        os.listdir('/private')
    except OSError:
        return False
    return True

print 'Is my device jailbroken:', is_device_jailbroken()