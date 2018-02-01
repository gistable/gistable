#!/usr/bin/env python

import argparse, os, re, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--sdk', default='', help='OS X or iOS SDK directory')
parser.add_argument('--no-frameworks', action='store_true', default=False, help='do not print frameworks, only unprefixed classes')
args = parser.parse_args()

print_frameworks = not args.no_frameworks
frameworks = set()
for frameworkDir in ['Frameworks', 'PrivateFrameworks']:
    for root, dirs, files in os.walk(os.path.join(args.sdk + '/System/Library', frameworkDir)):
        base, extension = os.path.splitext(os.path.basename(root))
        if extension != '.framework':
            continue
        
        framework = root + '/' + base
        nm = subprocess.Popen(['nm', '-U', framework], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        while True:
            line = nm.stdout.readline()
            if len(line) == 0:
                break
            
            match = re.search(r' S _OBJC_CLASS_\$_(.*)', line)
            if match == None:
                continue
            
            className = match.group(1)
            if re.match(r'^[A-Z][a-z]', className) and not className.startswith(base):
                if print_frameworks and not framework in frameworks:
                    print framework
                
                frameworks.add(framework)
                print '%s%s' % ('    ' if print_frameworks else '', className)
