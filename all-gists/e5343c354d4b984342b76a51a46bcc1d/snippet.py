import discord

paired = {
    'channel that will trigger the bot': 'channel the bot will copy messages to',
    'you know the drill': 'i can do this all day'
}

keyword_data = {
    'channel that will trigger the bot': ['keyword', 'copybot', ['both of these', 'must be in the same message']]
}

bot = discord.Client()

def escape_name(name):
    return name \
        .replace('\\', '\\\\') \
        .replace('*', '\\*') \
        .replace('_', '\\_') \
        .replace('`', '\\`')

@bot.event
async def on_message(msg):
    cid = msg.channel.id
    if cid in keyword_data:
        keywords = keyword_data[cid]
        send = False
        for i in keywords:
            if not send:
                if type(i) == str:
                    if i in msg.content.lower():
                        send = True
                elif type(i) == list:
                    send = True
                    for kw in i:
                        if not kw in msg.content:
                            send = False
        if send == True:
            if cid in paired:
                toSend = '[**' + escape_name(msg.author.display_name) + '**]: ' + msg.content
                if len(toSend) <= 2000:
                    try:
                        await bot.send_message(discord.Object(paired[cid]), toSend)
                    except:
                        pass

bot.run('token here')
