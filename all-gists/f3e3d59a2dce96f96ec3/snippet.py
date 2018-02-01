# frogor user check v1
# http://osx.michaellynn.org/freenode-osx-server/freenode-osx-server_2013-04-09.html
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
from objc import NULL
import sys

username = (SCDynamicStoreCopyConsoleUser(NULL, NULL, NULL) or [NULL])[0]
username = [username,''][username in [u"loginwindow", None]]
sys.stdout.write(username + "\n")

# v2
# http://osx.michaellynn.org/freenode-osx-server/freenode-osx-server_2013-04-09.html
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
from objc import NULL
import sys

username = (SCDynamicStoreCopyConsoleUser(NULL, NULL, NULL) or [NULL])[0]
username = [username,''][username in [u"loginwindow", u""]]
sys.stdout.write(username + "\n")

# v3
# http://osx.michaellynn.org/freenode-osx-server/freenode-osx-server_2014-10-28.html
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
from objc import NULL
import sys

username = (SCDynamicStoreCopyConsoleUser(NULL, NULL, NULL) or [None])[0]
username = [username,''][username in [u"loginwindow", None, u""]]
sys.stdout.write(username + "\n")

# v4
# http://osx.michaellynn.org/freenode-osx-server/freenode-osx-server_2014-10-28.html
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
import sys

username = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0]
username = [username,""][username in [u"loginwindow", None, u""]]
sys.stdout.write(username + "\n")

# embed in bash script like so
python -c 'from SystemConfiguration import SCDynamicStoreCopyConsoleUser; import sys; username = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0]; username = [username,""][username in [u"loginwindow", None, u""]]; sys.stdout.write(username + "\n");'