#!/usr/bin/python2.7
import subprocess

def touchpad_currently_off():
    all_states = subprocess.check_output(['synclient']).split('\n')
    off_state = next((s for s in all_states if 'touchpadoff' in s.lower()), None)
    return '1' in off_state

def main():
    if touchpad_currently_off():
        subprocess.check_call(['synclient', 'touchpadoff=0'])
    else:
        subprocess.check_call(['synclient', 'touchpadoff=1'])

if __name__ == '__main__':
    main()