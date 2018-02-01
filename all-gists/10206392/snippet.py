import hexchat
import re

__module_name__ = "Temp Ban"
__module_version__ = "1.0"
__module_description__ = "Easy command to tempban someone and kick them, requires InspIRCd and the m_timedbans module"


def formatTime(timestamp):
	multipliers = {"y": "year", "w": "week", "h": "hour", "d": "day", "m": "minute", "s": "second"}
	parts = re.findall(r'\d+\D', timestamp)
	finalFormat = ""
	for part in parts:
		split = re.split(r'(\D)', part)
		time = split[0]
		multiplier = split[1]
		finalFormat += time + " "
		finalFormat += multipliers[multiplier] + " " if int(time) == 1 else multipliers[multiplier] + "s "
	return finalFormat.strip()

def tempban(word, word_eol, userdata):
	if len(word) < 3:
		print(userdata)
		return hexchat.EAT_ALL

	nick = word[1]
	time = word[2]
	channel = hexchat.get_info("channel")
	users = hexchat.get_list("users")
	for user in users:
		if user.nick.lower() == nick.lower() and user.host is not None:
			host = user.host.split("@")[1]
			tbanCommand = "tban {} {} *!*@{}".format(channel, time, host)
			hexchat.command(tbanCommand)
			reason = word_eol[3] if len(word) > 3 else "Temp banned"
			hexchat.command("kick {} TEMPBAN: {} ({})".format(nick, reason, formatTime(time)))
			return hexchat.EAT_ALL
	hexchat.command("tban {} {} {}".format(channel, time, nick))

hexchat.hook_command("tempban", tempban, "Command is /tempban <nick> <time> [reason]")