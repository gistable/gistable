import discord
from discord.ext import commands
from asyncio import sleep


me = commands.Bot(command_prefix='.', self_bot=True)


@me.event
async def on_ready():
    print("----------")
    print("Logged in as:")
    print("    "+str(me.user.name))
    print("    "+str(me.user.id))
    print("----------")


def makeEmbed(*, name=None, icon=None, colour=0xDEADBF, values={}):
    '''Creates an embed messasge with specified inputs'''

    # Create an embed object with the specified colour
    embedObj = discord.Embed(colour=colour)

    # Set the author and URL
    embedObj.set_author(name=name, icon_url=icon)

    # Create all of the fields
    for i in values:
        if values[i] == '':
            values[i] = 'None'
        embedObj.add_field(name=i, value='{}'.format(values[i]))

    # Return to user
    return embedObj


@me.event 
async def on_message(message):
    if message.author.id != me.user.id:
        return
    if len(message.embeds) > 0:
        return

    actualDict = {}
    name = message.clean_content

    actualObj = makeEmbed(name=name, icon=me.user.avatar_url, values=actualDict)
    sleep(0.4)
    await me.edit_message(message, '  ', embed=actualObj)



token = "UserToken"  # Replace this with your user token
me.run(token, bot=False)
