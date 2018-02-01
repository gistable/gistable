import hexchat

__module_name__ = 'Twitch'
__module_author__ = 'TingPing, frumpy4, StepS'
__module_version__ = '6.8'
__module_description__ = 'Better integration with Twitch.tv'

# Commands from http://help.twitch.tv/customer/portal/articles/659095-chat-moderation-commands
# Enable the "commands" and "membership" caps for the best effect
# See https://github.com/justintv/Twitch-API/blob/master/chat/capabilities.md for an up-to-date list.
# /ban may conflict with other scripts nothing we can do about that
# /clear is an existing command, just override it
commands = ('timeout', 'slow', 'slowoff', 'subscribers', 'subscribersoff',
			'mod', 'unmod', 'mods', 'clear', 'ban', 'unban', 'commercial',
			'r9kbeta', 'r9kbetaoff', 'color', 'host', 'unhost', 'disconnect', 'w')

aliases = {'op':'mod', 'deop':'unmod'}

ymsgEdited = False
yactEdited = False

# Clean out some control chars from messages because Twitch servers eat them on delivery.
# So the local representation will be consistent with what the receiving end will see.
def strip_cchars(str):
	for list in [range(2, 9), range(11, 13), range(14, 32)]:
		for cnum in list:
			str = str.replace(chr(cnum), '')
	return str

def chantype(context):
	for chan in hexchat.get_list('channels'):
		if chan.context == context:
			return chan.type
	return 0

# From https://github.com/TingPing/plugins/blob/master/HexChat/mymsg.py and modified
def self_msg(msg, context=hexchat):
	mynick = context.get_info('nick')
	if '\001ACTION' in msg:
		for repl in ('\001ACTION', '\001'):
			msg = msg.replace(repl, '', 1)
		return context.emit_print('Your Action', mynick, msg.strip())
	else:
		return context.emit_print('Your Message', mynick, msg)

# For functions that must only take effect on Twitch
def twitchOnly(func):
	def if_twitch(*args, **kwargs):
		for host in (hexchat.get_info('host'), hexchat.get_info('server')):
			if host and 'twitch.tv' in host:
				return func(*args, **kwargs)
		else:
			return hexchat.EAT_NONE
	return if_twitch

# Handle chat clean-ups and timeouts.
@twitchOnly
def clearchat_cb(word, word_eol, userdata):
	if len(word) == 4:
		hexchat.emit_print('Server Text','User \00318'+word[3].replace(':','',1)+'\017 has been timed out.')
	elif len(word) == 3:
		hexchat.emit_print('Server Text','Chat has been cleared by a moderator.')
	else:
		return hexchat.EAT_NONE
	return hexchat.EAT_ALL

# Handle whispers and display them as private messages in the current context.
@twitchOnly
def whisper_cb(word, word_eol, userdata):
	whisper = word_eol[3].replace(':','',1)
	nick = word[0][1:].split('!')[0]
	context = hexchat.find_context(channel=nick)
	if context:
		context.command('recv {} PRIVMSG {}'.format(word[0], word_eol[2]))
	else:
		# hexchat.command('recv {} NOTICE {}'.format(word[0], word_eol[2]))
		# 'Private Message' produces a beep so is preferable
		hexchat.emit_print('Private Message', nick, whisper)
	return hexchat.EAT_ALL

# Twitch returns a lot of 'unknown command' errors, ignore them.
@twitchOnly
def servererr_cb(word, word_eol, userdata):
	if word[3] in ('WHO', 'WHOIS'):
		return hexchat.EAT_ALL

@twitchOnly
def eatall(word, word_eol, data):
	return hexchat.EAT_ALL

# Called if a RECONNECT message is received from the server.
@twitchOnly
def reconnect_cb(word, word_eol, userdata):
	hexchat.emit_print('Server Error', 'The server has requested you to reconnect. \
If you don\'t do this, you will likely be disconnected after 30 seconds.')
	return hexchat.EAT_ALL

# Called if a Twitch channel is hosting somebody while offline (switches to the target stream in the webbrowser)
# Treat it as an invite in HexChat.
@twitchOnly
def hosttarget_cb(word, word_eol, userdata):
	source = word[2].replace('#','',1)
	targchan = word[3].replace(':','#',1)
	if targchan != '#-':
		hexchat.emit_print('Invited', targchan, source, hexchat.get_info('server'))
	return hexchat.EAT_ALL

# Print private jtv messages in server tab (if the commands cap is not in use).
# Print "channel" jtv/twitchnotify messages in the respective channel tab (with CAPs).
@twitchOnly
def privmsg_cb(word, word_eol, userdata):
	nick = word[0][1:].split('!')[0]
	if nick == 'jtv' or nick == 'twitchnotify':
		if word[2][0] != '#':
			for chan in hexchat.get_list('channels'):
				if chan.type == 1 and chan.id == hexchat.get_prefs('id'):
					chan.context.emit_print('Server Text', word_eol[3][1:])
			return hexchat.EAT_ALL
		else:
			hexchat.emit_print('Server Text', word_eol[3][1:])
			return hexchat.EAT_ALL
		# Obsolete, no longer sent by twitch/jtv in this form
		# elif word[3] in (':USERCOLOR', ':USERSTATE', ':HISTORYEND', ':EMOTESET', ':CLEARCHAT', ':SPECIALUSER'):
			# return hexchat.EAT_ALL

# Eat any message starting with '.' and '/', twitch eats all of them too.
# Except for the .w (whisper) messages when formed properly.
# Also clean out control chars (see "strip_cchars")
@twitchOnly
def yourmsg_cb(word, word_eol, userdata):
	global ymsgEdited
	if ymsgEdited:
		return

	if chantype(hexchat.get_context()) == 2:
		if word[1][0] in ['.', '/']:
			args = word[1].split(' ')
			if args[0][1:] == 'w':
				if len(args) >= 3:
					hexchat.emit_print('Notice Send', args[1], strip_cchars(' '.join(args[2:])))
				# Otherwise let the Twitch server demonstrate /w usage.
			return hexchat.EAT_ALL
		else:
			ymsgEdited = True
			hexchat.emit_print('Your Message', word[0], strip_cchars(word[1]), '' if len(word) < 3 else word[2])
			ymsgEdited = False
			return hexchat.EAT_ALL

# Clean out control chars from actions (see "strip_cchars")
@twitchOnly
def youract_cb(word, word_eol, userdata):
	global yactEdited
	if yactEdited:
		return

	yactEdited = True
	hexchat.emit_print('Your Action', word[0], strip_cchars(word[1]), '' if len(word) < 3 else word[2])
	yactEdited = False
	return hexchat.EAT_ALL

# PM support: PMs are redirected to whispers. It sends a /w to #jtv that gets eaten.
# A relay channel is needed for whispers to work, using #jtv as recommended on the official forums.
@twitchOnly
def my_saymsg_cb(word, word_eol, data):
	if chantype(hexchat.get_context()) == 3:
		targ = hexchat.get_info('channel')
		self_msg(word_eol[0])
		hexchat.command('PRIVMSG #jtv :/w {} {}'.format(targ, strip_cchars(word_eol[0])))
		return hexchat.EAT_ALL

# Redirect /msg and /notice to /w if the target is not a channel
@twitchOnly
def my_msg_cb(word, word_eol, data):
	if len(word) > 2 and word[1][0] != '#':
		hexchat.emit_print('Notice Send', word[1], strip_cchars(word_eol[2]))
		hexchat.command('PRIVMSG #jtv :/w {}'.format(word_eol[1]))
		return hexchat.EAT_ALL

# Just prefix with a '/' ('.' also works but '/' is preferred officially).
@twitchOnly
def command_cb(word, word_eol, alias):
	if chantype(hexchat.get_context()) != 2:
		hexchat.emit_print('Server Text','You must be on a channel to use the Twitch commands.')
		return hexchat.EAT_ALL
	elif alias:
		if len(word_eol) > 1:
			hexchat.command('say /{} {}'.format(alias, word_eol[1]))
		else:
			hexchat.command('say /{}'.format(alias))
	else:
		hexchat.command('say /{}'.format(word_eol[0]))
	return hexchat.EAT_ALL

for command in commands:
	hexchat.hook_command(command, command_cb)
for command, alias in aliases.items():
	hexchat.hook_command(command, command_cb, alias)
hexchat.hook_command('', my_saymsg_cb)
hexchat.hook_command('msg', my_msg_cb)
hexchat.hook_command('notice', my_msg_cb)
hexchat.hook_server('421', servererr_cb)
hexchat.hook_server('PRIVMSG', privmsg_cb)
hexchat.hook_server('CLEARCHAT', clearchat_cb)
hexchat.hook_server('WHISPER', whisper_cb)
hexchat.hook_server('RECONNECT', reconnect_cb)
hexchat.hook_server('HOSTTARGET', hosttarget_cb)
hexchat.hook_server('USERSTATE', eatall)
hexchat.hook_server('GLOBALUSERSTATE', eatall)
hexchat.hook_server('HISTORYEND', eatall)
hexchat.hook_server('SPECIALUSER', eatall)
hexchat.hook_server('ROOMSTATE', eatall)
hexchat.hook_print('Your Message', yourmsg_cb)
hexchat.hook_print('Your Action', youract_cb)
# Obsolete
# hexchat.hook_server('EMOTESET', eatall)
# hexchat.hook_server('USERCOLOR', eatall)
