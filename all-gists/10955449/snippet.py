#!/usr/bin/env python

import urllib.request
import json
import pprint


URL = 'http://www.thebluealliance.com/api/v2/'
HEADER_KEY = 'X-TBA-App-Id'
HEADER_VAL = 'frc1816:scouting-machine:1'


# returns a list of the teams (team key) participating in an event
def get_event_teams(event_key):
	request = urllib.request.Request(URL + 'event/' + event_key + '/teams')
	request.add_header(HEADER_KEY, HEADER_VAL)
	response = urllib.request.urlopen(request)
	jsonified = json.loads(response.read().decode("utf-8"))
	teams = []

	for team in jsonified:
		teams.append(team['key'])

	return teams

# returns a list of the awards a team has won
def get_team_awards(team_key):
	request = urllib.request.Request(URL + 'team/' + team_key + '/2014')
	request.add_header(HEADER_KEY, HEADER_VAL)
	response = urllib.request.urlopen(request)
	jsonified = json.loads(response.read().decode("utf-8"))
	events = jsonified['events']
	team_awards = []

	for event in events:
		for award in event['awards']:
			team_awards.append(award['name'])

	return team_awards


def main():
	# 2014arc, 2014new, 2014cur, 2014gal
	teams = get_event_teams('2014gal')
	chairmans_teams = []
	chairmans_counter = 0

	for team in teams:
		print("Processing team: " + team)
		awards = get_team_awards(team)
		for award in awards:
			if 'Regional Chairman\'s Award' in award:
				chairmans_teams.append(team)
				chairmans_counter = chairmans_counter + 1
				break

	print('Chairman\'s winners = ' + str(chairmans_counter))
	print(chairmans_teams)


if __name__ == "__main__":
    main()
