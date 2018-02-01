import re

history_snippet = '''Start-Date: 2014-08-25  12:52:37
Commandline: apt-get install -y openjdk-6-jdk openjdk-7-jdk icedtea-7-plugin
Install: openjdk-6-jre-lib:amd64 (6b32-1.13.4-4ubuntu0.14.04.1, automatic), icedtea-netx-common:amd64 (1.5-1ubuntu1, automatic), openjdk-6-jdk:amd64 (6b32-1.13.4-4ubuntu0.14.04.1), libxcb1-dev:amd64 (1.10-2ubuntu1, automatic), ttf-dejavu-extra:amd64 (2.34-1ubuntu1, automatic), icedtea-6-jre-cacao:amd64 (6b32-1.13.4-4ubuntu0.14.04.1, automatic), icedtea-7-plugin:amd64 (1.5-1ubuntu1), libxau-dev:amd64 (1.0.8-1, automatic), openjdk-6-jre-headless:amd64 (6b32-1.13.4-4ubuntu0.14.04.1, automatic), x11proto-core-dev:amd64 (7.0.24-1, automatic), libxt-dev:amd64 (1.1.4-1, automatic), openjdk-7-jdk:amd64 (7u65-2.5.1-4ubuntu1~0.14.04.1), libx11-dev:amd64 (1.6.2-1ubuntu2, automatic), x11proto-kb-dev:amd64 (1.0.6-2, automatic), openjdk-6-jre:amd64 (6b32-1.13.4-4ubuntu0.14.04.1, automatic), xtrans-dev:amd64 (1.3.2-1, automatic), libxdmcp-dev:amd64 (1.1.1-1, automatic), icedtea-netx:amd64 (1.5-1ubuntu1, automatic), libx11-doc:amd64 (1.6.2-1ubuntu2, automatic), xorg-sgml-doctools:amd64 (1.11-1, automatic), libsm-dev:amd64 (1.2.1-2, automatic), x11proto-input-dev:amd64 (2.3-1, automatic), libpthread-stubs0-dev:amd64 (0.3-4, automatic), libice-dev:amd64 (1.0.8-2, automatic), icedtea-6-jre-jamvm:amd64 (6b32-1.13.4-4ubuntu0.14.04.1, automatic)
End-Date: 2014-08-25  12:53:31'''

INSTALL_STRING = 'Install: '
REMOVE_STRING = 'Remove: '
#COMMANDLINE_STRING = 'Commandline: '

pattern = re.compile('(.+?) \(.+?\), ')

installed_packages = []
removed_packages = []

for line in history_snippet.split('\n'):
    '''
    if line.startswith(COMMANDLINE_STRING):
        if line.find('install') != -1:
            line = line[line.find('install') + len('install'):]
            for package in line.split():
                if package.startswith('-'):
                    continue
                installed_packages.append(package)
    '''
    
    if line.startswith(INSTALL_STRING):
        line = line[len(INSTALL_STRING):]
        
        installed_packages.extend(pattern.findall(line))
    elif line.startswith(REMOVE_STRING):
        line = line[len(REMOVE_STRING):]
        
        removed_packages.extend(pattern.findall(line))

installed_packages.sort()
removed_packages.sort()

print(' '.join(installed_packages))
print(' '.join(removed_packages))
