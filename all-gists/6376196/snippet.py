import urllib2
import json
import re

class SoccerwayTeamMatches:

    def __init__(self, teamId):
        self.teamId = str(teamId)
        self.data = {'all': [], 'home': [], 'away': []}

    def parseJson(self, jsonStr):
        """
        Handles the parsing of the JSON object returned
        by Soccerway API (nr.soccerway.com/a/block_team_matches).
        
        Input: The JSON object returned by the API as a string
        
        Return: Two dimensional array of the match results

        """
        jsonPy = json.loads(jsonStr)

        # Fetch the interesting part of inputted JSON obj
        content = jsonPy['commands'][0]['parameters']['content']

        # Remove uninteresting header and footer data
        cleanContent = content.split('</tbody>',1)[0].split('<thead',1)[1]

        # Split content by <tr> -tags (tr is shorthand for table row)
        p1 = re.compile(r'<tr[^<]+?>')
        splitted = p1.split(cleanContent)
        header = splitted[1] # First row is the table header data
        data = splitted[2:-1] # Rest are the match info 

        # Split content by <td> -tags (table columns) and clean other tags
        p2 = re.compile(r'<td[^<]+?>')
        f = lambda x: map(lambda y: re.sub('<[^<]+?>','',y).strip(), p2.split(x)[1:-2])
        return map(f, data)

    def getData(self, matchType):
        """ 
        Return the cleaned match data in 2D array.
        Does simple caching of the GET queries, that is,
        same data is not queried twice.

        Input: Type of the matches, must be one of
        the following strings: 'all', 'away' or 'home'.

        Output: 2d array of match results

        """
        if matchType not in ['all','away','home']:
            return []

        if not self.data[matchType]:
            url = "http://nr.soccerway.com/a/block_team_matches" \
                  "?block_id=page_team_1_block_team_matches_5" \
                  "&callback_params=%7B%22page%22%3A0%2C%22" \
                  "bookmaker_urls%22%3A%5B%5D%2C%22block_service_id" \
                  "%22%3A%22team_matches_block_teammatches%22%2C%22" \
                  "team_id%22%3A"+self.teamId+"%2C%22competition_id" \
                  "%22%3A0%2C%22filter%22%3A%22all%22%7D" \
                  "&action=filterMatches&params=%7B%22" \
                  "filter%22%3A%22"+matchType+"%22%7D"
            jsonStr = urllib2.urlopen(url).read()
            self.data[matchType] = self.parseJson(jsonStr)
        
        return self.data[matchType]
