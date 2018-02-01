import discord
import logging
from dateutil.parser import parse
from dateutil.tz import gettz
from pytz import timezone

logging.basicConfig(level=logging.CRITICAL)
client = discord.Client()

tzinfos = {"CST": gettz("America/Chicago"), "CDT": gettz("America/Chicago"), "PST": gettz("America/Los Angeles"), "PDT": gettz("America/Los Angeles"), "EST": gettz("America/New York"), "EDT": gettz("America/New York")}

day_fmt = '%b %-d @ '
time_fmt = '%-I.%M%p'
# See https://github.com/dateutil/dateutil/issues/94#issuecomment-133733178
add_default_tz = lambda x, tzinfo: x.replace(tzinfo=x.tzinfo or tzinfo)
EST_tz = gettz("America/New York")

@client.event
async def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return

	if message.content.startswith('!tz'):
		try:
			msg = get_converted_times(message.content[3:])
		except Exception as e:
			print(e)
			msg = "Can't parse '" + message.content[3:] + "' sorry 🤖"
		await client.send_message(message.channel, msg)

def get_converted_times(msg):
	print(msg)
	msg = msg.strip().replace('.',':',1)
	dt = add_default_tz(parse(msg.upper(), fuzzy=True, tzinfos=tzinfos), EST_tz)
	print(dt)
	pDt = dt.astimezone(timezone('US/Pacific')).strftime(time_fmt).lower() + " pst"
	cDt = dt.astimezone(timezone('US/Central')).strftime(time_fmt).lower() + " cst"
	eDt = dt.astimezone(timezone('US/Eastern')).strftime(time_fmt).lower() + " est"
	day = dt.astimezone(timezone('US/Central')).strftime(day_fmt)
	return day + pDt + " -- " + cDt + " -- " + eDt

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

client.run('---TOKEN GOES HERE---')
