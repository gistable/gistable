#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import time, os, discord

from multiprocessing.dummy import Pool as WorkerPool

logdir      = "/home/sektour/.local/share/starconflict/logs"                #путь к логам
libopus     = "/usr/lib64/libopus.so"                                       #путь к libopus
soundfile   = "/home/sektour/files/NLD.mp3"                                 #путь к звуку проигрываему при запуске торпед
owner       = "nick"                                                        #никнейм владельца бота
token       = "token"                                                       #токен авторизации бота

client = discord.Client()
runned = False
lastTime = ""
channel = ""
if not discord.opus.is_loaded():
    discord.opus.load_opus(libopus)

    
def findLastLog():
    global logdir
    
    lastdir = max([os.path.join(logdir,f) for f in os.listdir(logdir)], key=os.path.getctime)
    lastLog = os.path.join(lastdir, "combat.log")
    return lastLog

def lastMsgCheck():
    global lastTime
    
    f = open(findLastLog(),"r")
    strings = f.readlines()
    f.close()
    
    for i in reversed(strings):
        time = i[:5]
        if time == lastTime:
            return False
        if "ClanShip_AimPointShield" in i:
            lastTime = time
            return True
    return False
    
def rocketAlert():
    global runned
    global channel
    global soundfile
    while True:
        while channel == "":
            time.sleep(2)
        while runned:
            if lastMsgCheck():
                player = channel.create_ffmpeg_player(soundfile)
                player.start()
            time.sleep(0.5)
        time.sleep(1)
        
    
@client.event
async def on_message(message):
    global channel
    global runned
    global owner
    
    if message.author == client.user or message.author.name != owner:
        return

    if  message.content.startswith("rr"):
        #await client.send_message(message.channel, 'rocket alert started')
        print("rocket alert started")
        runned = True
        if channel != "":
            await channel.disconnect()
        channel = await client.join_voice_channel(message.author.voice_channel)
        return
    if message.content.startswith("rs"):
        #await client.send_message(message.channel, 'rocket alert stoped')
        if not runned:
            print("rocket alert not runned")
            return
        print("rocket alert stoped")
        runned = False
        if channel == " ":
            channel = ""
            return
        if channel.is_connected():
            await channel.disconnect()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    await client.change_presence(game=discord.Game(name='$tar Conflict'))

pool = WorkerPool(1)
pool.apply_async(rocketAlert)
client.run(token)
pool.close()
pool.join()
                
