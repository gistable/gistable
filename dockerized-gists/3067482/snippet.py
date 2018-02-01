#################################################################
## Written by: Assil Ksiksi				       ##
## 	                                                       ##														   ##	                                                       ##
## Scrapes IMDB for movie IDs, makes API requests, then writes ##
## the results to a database.				       ##
## 							       ##						   ##                                                             ##
#################################################################

import re, requests, sqlite3, json, time

headers = {'user-agent': "Automated data scraper; won't make too many requests"}

def write_data_to_table(headers, data):
	'''Writes passed headers and data to a sqlite3 table.'''
	conn = sqlite3.connect("top250.sqlite")
	c = conn.cursor()

	c.execute('''CREATE TABLE data
				 ({0})'''.format(", ".join(headers)))

	qmarks = ",".join(["?" for i in range(len(headers))]) # For input formatting

	c.executemany("INSERT INTO data VALUES (%s)" % qmarks, data)

	conn.commit()
	conn.close()

	return "\nSuccessfully written to DB."

def get_movie_data(id):
	'''Returns movie data of given IMDB ID in dictionary format using API request.'''
	return requests.post("http://imdbapi.com/?i={0}&tomatoes=true".format(id), headers=headers).json

def scrape_movie_ids():
	'''Scrapes the IDs of IMDB's Top 250 movies.'''
	source = requests.post("http://www.imdb.com/chart/top", headers=headers).text
	return re.findall(r'<a href="/title/(\w+)/">', source)

def main():
	ids = scrape_movie_ids()
	movie_data = []
	headers = [each + " text" for each in get_movie_data(ids[0]).keys()] # Automate column name and type
	
	print "\nWorking with API...\n"

	# Loop through IDs and make an API request for each one.
	for id in ids:
		try:
			response = tuple(get_movie_data(id).values())
			if len(response) == len(headers):
				movie_data.append(response)
				print "     * Request #{} succeeded.".format(ids.index(id) + 1)
			else: print "     * Request #{} failed.".format(ids.index(id) + 1)
		except:
			print "     * Request #{} failed.".format(ids.index(id) + 1)
		time.sleep(1.5)

	# Write final data to a table.
	print write_data_to_table(headers, movie_data)

if __name__ == '__main__':
	main()