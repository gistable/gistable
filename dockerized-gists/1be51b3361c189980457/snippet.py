import requests
import csv
import sys

# get me all active players

url_allPlayers = ("http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason"
		"=0&LeagueID=00&Season=2015-16")

#request url and parse the JSON
response = requests.get(url_allPlayers)
response.raise_for_status()
players = response.json()['resultSets'][0]['rowSet']

# use roster status flag to check if player is still actively playing
active_players = [players[i] for i in range(0,len(players)) if players[i][2]==1 ]	

ids = [active_players[i][0] for i in range(0,len(active_players))]

print("Number of Active Players: " + str(len(ids)))

name_height_pos = []

for i in ids:

	url_onePlayer=("http://stats.nba.com/stats/commonplayerinfo?"
		"LeagueID=00&PlayerID=" + str(i) + "&SeasonType=Regular+Season")
	#request url and parse the JSON
	response = requests.get(url_onePlayer)
	response.raise_for_status()
	one_player = response.json()['resultSets'][0]['rowSet']
	stats_player = response.json()['resultSets'][1]['rowSet']

	try:
		points = stats_player[0][3]
		assists = stats_player[0][4]
		rebounds = stats_player[0][5]
		PIE = stats_player[0][6]
	# handle the case, where player is active, but didn't play
	# in any game so far in this season (-1 just a place holder value)
	except IndexError:
		points = -1
		assists = -1
		rebounds = -1
		PIE = -1

	name_height_pos.append([one_player[0][1] + " " + one_player[0][2], 
		one_player[0][10], 
		one_player[0][14], 
		one_player[0][18],
		"http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/"+one_player[0][1].lower()+"_"+ one_player[0][2].lower() +".png",
		points,
		assists,
		rebounds,
		PIE])

#convert from inches to cm
for i in range(0,len(name_height_pos)):
	feet = name_height_pos[i][1][0]
	inches = name_height_pos[i][1][2:]

	result = (float(feet) * 12 + float(inches)) * 2.54;
	name_height_pos[i][1] = result



answer = input("Save as player.csv -- y/n\t")
if answer[0] == "n":
	sys.exit()
elif answer[0] != "y":
	sys.exit()
else:

	with open("player.csv", "w") as csvfile:
		writer = csv.writer(csvfile, delimiter=",", lineterminator="\n")
		writer.writerow(["Name","Height","Pos","Team","img_Link","PTS","AST","REB","PIE"])
		for row in name_height_pos:
			writer.writerow(row)
		print("Saved as \'player.csv\'")