import sys, socket, shlex
from random import choice, randint

class linebuf:
    def __init__(self):
        self.s = ['']
    def data(self, data):
        self.s[-1:] = (self.s[-1] + data).split('\r\n')
        lines, self.s = self.s[:-1], self.s[-1:]
        return lines

def out(line):
    sock.send((line+'\r\n').encode())
    print('<- '+line)
def reply(line):
    out(reply_fmt.format(line))

my = { 'nick':'ajibot' }

def cmd_hi(args):
    reply(choice(['ohai','hi','hai','lolsup','c:',':D','hello',
            'herro','hullo','heyyyy','hiiii','lol']))
def cmd_who(args):
    reply('i am '+my['nick'])
def cmd_coin(args):
    reply(choice(['heads','tails']))
cmd_flip = cmd_coin
def cmd_poni(args):
    reply('https://derpiboo.ru/'+str(randint(0,290000)))
def cmd_roll(args):
    s = [int(x) for x in args[0].split('d')]
    if s[0] > 0 and s[0] < 20 and s[1] > 1 and s[1] < 100:
        rolls = [randint(1,s[1]) for x in range(s[0])]
        reply('{} = {}'.format(' '.join([str(x) for x in rolls]), sum(rolls)))
cmd_dice = cmd_roll
def cmd_dicks(args):
    reply('8'+('='*randint(3,10))+'D')
cmd_dick = cmd_dicks
def cmd_help(args):
    s = []
    for k in globals().keys():
        if k.startswith('cmd_'):
            s.append(k[4:])
    reply(' '.join(s))

def irc_433(source, args, text, raw):
    my['nick'] += '_'
    out('NICK ' + my['nick'])
def irc_001(source, args, text, raw):
    my['nick'] = args[1]
    out('JOIN ' + my['chan'])
def irc_join(source, args, text, raw):
    chan = text if text != '' else args[-1]
    if source[0] == my['nick']:
        out('PRIVMSG {} :joined {}'.format(my['chan'], chan))
def irc_ping(source, args, text, raw):
    out('PONG '+raw[5:])
def irc_privmsg(source, args, text, raw):
    global reply_fmt
    command = []
    if args[1][0] == '#':
        if text[0] == '.':
            command = shlex.split(text[1:])
        if text.startswith(my['nick']):
            s = text.split(None,1)
            if len(s) > 1:
                command = shlex.split(s[1])
        if len(command) > 0:
            reply_fmt = 'PRIVMSG {} :{}: {}'.format(args[1], source[0], '{}')
    else:
        command = shlex.split(text)
        reply_fmt = 'NOTICE {} :{}'.format(source[0], '{}')
    if len(command) == 0:
        return  
    name, args = 'cmd_'+command[0].lower(), command[1:]
    if name in globals():
        globals()[name](args)

def process(line):
    s, _, text = line.partition(' :')
    args = s.split(' ')
    if len(args) == 0:
        return
    source = ''
    if args[0][0] == ':':
        source, args = args[0][1:], args[1:]
    name = 'irc_' + args[0].lower()
    if name in globals():
        globals()[name](source.partition('!'), args, text, line)

if len(sys.argv) != 3:
    print('usage: ajibot <server> <chan>')
    print('no hash on chan (i.e., start with \'foo\' if you want to join #foo')
    sys.exit(1)
lb = linebuf()
sock = socket.socket()
running = True
sock.connect((sys.argv[1],6667))
my['chan'] = '#'+sys.argv[2]
out('NICK ' + my['nick'])
out('USER a * * :ajibot')
while running:
    data = sock.recv(512).decode()
    if len(data) == 0:
        break
    for line in lb.data(data):
        print('-> '+line)
        try:
            process(line)
        except Exception:
            sys.excepthook(*sys.exc_info())
