# Simple exporter for published Yahoo Pipes
# For use with (glue still required!) pipe2py - https://github.com/ggaughan/pipe2py

uid='' #Your Yahoo Pipes ID

#-------
import simplejson,urllib,csv

def getPipesPage(uid,pageNum):
	print 'getting',uid,pageNum
	pipesFeed='http://pipes.yahoo.com/pipes/person.info?_out=json&display=pipes&guid='+uid+'&page='+str(pageNum)
	feed=simplejson.load(urllib.urlopen(pipesFeed))
	return feed

def getPipesData(id):
	srcURL='http://pipes.yahoo.com/pipes/pipe.info?_out=json&_id='+id
	srcf = urllib.urlopen(srcURL)	
	return srcf.read()


page=1

scrapeit=True

f=open('pipesExport_'+uid+'.csv','wb+')
writer=csv.writer(f)
while (scrapeit):
	feeds= getPipesPage(uid,page)
	print feeds
	if feeds['value']['hits']==0:
		f.close()
		scrapeit=False
	else:
		for pipe in feeds['value']['items']:
			id=pipe['id']
			src=getPipesData(id)
			writer.writerow([pipe['description'],pipe['title'],src])
		page=page+1