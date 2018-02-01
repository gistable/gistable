import mysql.connector as mysql
import uuid
import yaml
import time

filepath = "playerfiles/"

conn = mysql.connect(user="", password="", 
                       host="localhost", database="mc_global_gesuit")

print("Fetching data")
cur = conn.cursor()
cur.execute("SELECT * FROM homes")
homes = cur.fetchall()
cur.execute("SELECT * FROM players")
players = cur.fetchall()

print("Processing data")
playerfiles = {}

for row in players:
    playername = row[0]
    playeruuid = row[1]
    lastonline = row[2]
    ipaddress = row[3]
    newuuid = str(uuid.UUID(playeruuid))
    timestamp = int(time.mktime(lastonline.timetuple()))
    playerfiles[playername.lower()] = {
        "uuid": newuuid, 
        "ipAddress": ipaddress,
        "timestamps": {"login": timestamp, "logout": timestamp*1000}
        }

for row in homes:
    playeruuid = row[0]
    home_name = row[1]
    server = row[2]
    world = row[3]
    x = row[4]
    y = row[5]
    z = row[6]
    yaw = row[7]
    pitch = row[8]
    
    newuuid = str(uuid.UUID(playeruuid))
    playername = None
    for playerkey in playerfiles:
        if newuuid == playerfiles[playerkey]["uuid"]:
            playername = playerkey.lower()
    if playername is None:
        continue
    if "homes" not in playerfiles[playername]:
        playerfiles[playername]["homes"] = {}
    playerfiles[playername]["homes"][home_name] = {
        "world": world, 
        "x": x, 
        "y": y, 
        "z": z, 
        "yaw": yaw, 
        "pitch": pitch}

print("Dumping players")
for playername, playerdata in playerfiles.items():
    playerpath = filepath + playername + ".yml"
    f = open(playerpath, "w")
    yaml.dump(playerdata, f, default_flow_style=False)
    f.close()