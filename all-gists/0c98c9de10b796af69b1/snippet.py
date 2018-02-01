from flask import Flask, render_template, request
import os , shelve , atexit , threading , urllib2 , time
app = Flask(__name__)

poll_data = {
	'question' : 'You agree that the Brazilian internet should be stapled?',
	'fields': ['Yes', 'No']
}

db = shelve.open("votes.db",writeback=True)

r_ip = urllib2.urlopen("http://myip.dnsdynamic.org").read()

def clean() :
	print "Cleaning up the shit"
	db.close()

def check_votes(ip) :
	for x in range(99999) :
		pass
	
	if len(db[ip]) > 1 :
		db[ip] = list(set(db[ip]))

@app.route('/')
def root():
	if request.remote_addr not in db.keys() :
		db[request.remote_addr] = []
	
	return render_template('poll.html', data=poll_data)

@app.route('/poll')
def poll():
	if request.remote_addr not in db.keys() :
		db[request.remote_addr] = []
	vote = request.args.get('field')
	print vote
	if vote in poll_data["fields"] :
		db[request.remote_addr].append(vote)
		if db[request.remote_addr][db[request.remote_addr].index(vote)-1] != vote :
			db[request.remote_addr].remove(db[request.remote_addr][db[request.remote_addr].index(vote)-1])	

	t = threading.Thread(target=check_votes,args=(request.remote_addr,))
	t.start()

	return render_template('thankyou.html', data=poll_data)
	
@app.route('/results')
def show_results():

	if request.remote_addr not in db.keys() :
		redirect("http://v0t3.pwn2win.party/")

	votes = {}
	votes["Yes"] = 15
	votes["No"] = 14

	votes[db[request.remote_addr][0]] += len(db[request.remote_addr])

	flag = "The Internet is not free anymore :("

	if votes["No"] > votes["Yes"] :
		flag = open("flag","r").read()

	return render_template('results.html',f=flag , data=poll_data, votes=votes)

if __name__ == "__main__":	
	atexit.register(clean)
	app.run(host='0.0.0.0',threaded=True,debug=False,port=80)