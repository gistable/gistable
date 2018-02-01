import phosphorus
from phosphorus.irc import IRC

import sys
_, host, port, nick = sys.argv

def main():
    irc = IRC(host, port, nick)
    yield phosphorus.fork(irc.run())
    yield phosphorus.until_elapsed(2)
    yield from irc.send_command("join", "#overviewer")
    
    while 1:
        cmd = (yield from irc.get_next_command('privmsg'))
        if not cmd:
            break
        
        source, message = cmd[1]
        if source == "#overviewer":
            if "fnord" in message.lower():
                yield from irc.send_command("privmsg", "#overviewer", message.lower().replace("fnord", ""))

phosphorus.run(main())
