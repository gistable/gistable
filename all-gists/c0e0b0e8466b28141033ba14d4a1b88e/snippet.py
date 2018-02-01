import urllib2
import sqlite3
import pip
import os
import json
import pymysql.cursors
#inFile: SQL databse filename string (assuming .db) #outFile: JSON filename string
def getDataFromDBFile(inFile, outFile):
    try:
        conn=sqlite3.connect(inFile)  
        c=conn.cursor()
        c.execute("select latitude as lat, longitude as lng, (substr(disappear_time, 15, 2) * 60 + substr(disappear_time, 18, 2) + 2710) % 3600 as time from pokemon group by spawnpoint_id;")
        output=[]
        for row in c:  
            checkTime=str(row[2])
            if checkTime!="":
                spawn={'lat':row[0],'lng':row[1],'time':row[2]}                
                output.append(spawn)    
        wf=open(outFile,'w')
        json.dump(output,wf)
        wf.close()
        conn.close()
    except:
        msg=("ERROR:Issue converting "+inFile+" to "+outFile)
        
def checkReq(inReq):
    try:
        f=open('requirements.txt', 'r')
        reqs=f.read()
        if reqs.lower().find(inReq.lower(),0,len(reqs))>=0:
            f.close()
            return True
        else:
            f.close()
            return False
    except: 
        return False

def checkValidJSON(file):
    try:
        with open(file) as f:
            spawns = json.load(f)
            f.close()
            return True
    except:
        return False
    
def menu(present,valid):
    print("\n" * 75)
    print "------Main Menu: Works with v2.2.0 & v3.1.0 of Maps------"
    print("Note: I should be in the main directory alongside runserver.py\n\n Options:\n")
    if valid==False:
        print "1> Generate JSON --'spawns.json' not present or invalid JSON"
    else:
        print "1> Generate JSON"
    print "2> Merge search.py"
    if present:
        print "3> Add geojson to requirements.txt --Already Present!!"
    else:
        print "3> Add geojson to requirements.txt"
    print "4> Install geojson now"
    print "5> Temporary: Manual download flask_cache_bust requirement"
    print "            ^^For current map state as of v3.1.0"
    print "6> Quit"
    
#======START SETUP=======#
geoJsonVer="1.3.3"
jsonFile="spawns.json"
r1=False
r2=False
r3=False
msg=""

while 1==1:
    present=checkReq("geojson")
    valid=checkValidJSON(jsonFile)
    menu(present,valid)
    if(r1==True & r2==True & r3==True & valid==True):
        print("------COMPLETE------")
        print("Looks like all the implementation requirements are met")
        print("--------------------")
    if msg!="":
        print("\n"+msg+"\n")

    inOpt=raw_input("Option> ")
    if inOpt=="1":
        res_2=raw_input("\nSQLite (1) or MySQL (2) or menu (99)? (1/2) ")
        if res_2=="1":
            res_3=raw_input("\nEnter your database filename (default: pogom.db): ")  
            if res_3!="":
                getDataFromDBFile(str(res_3), jsonFile)
                r1=True
                msg=("File: 'spawns.json' created from'"+str(res_3)+"'")
            else:        
                getDataFromDBFile('pogom.db', jsonFile)
                r1=True
                msg=("File: 'spawns.json' created from 'pogom.db'")   
        elif res_2=="2":   
            sqlHost=raw_input("DB Host: ")
            sqlUser=raw_input("DB User: ")
            sqlPass=raw_input("DB Pass: ")
            sqlDB=raw_input("DB Name: ")
            sqlMode=raw_input("Set SQL_mode='traditional'?? (ONLY IF QUERY ERRORS) (yes/no) ")
            connection = pymysql.connect(host=str(sqlHost),
                                 user=str(sqlUser),
                                 password=str(sqlPass),
                                 db=str(sqlDB),
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
            try:
                with connection.cursor() as cursor:
                    if sqlMode.lower()=="yes":
                        sql="set sql_mode='traditional';"
                        cursor.execute(sql)
                    sql = "select latitude as lat, longitude as lng, ((extract(minute from cast(disappear_time as time)) * 60 + extract(second from cast(disappear_time as time))) + 2701) % 3600 as time from pokemon group by spawnpoint_id;"
                    cursor.execute(sql)
                    result=cursor.fetchall()        
                    output=[]
                    for row in result:
                        checkTime=str(row['time'])
                        if checkTime!="":                                
                            spawn= {'lat':float(row['lat']), 'lng':float(row['lng']), 'time':row['time']}                     
                            output.append(spawn)    
                    wf=open(jsonFile,'w')
                    json.dump(output,wf)
                    wf.close()                    
            finally:
                connection.close()
                r1=True
                msg=("File: 'spawns.json' created from MySQL DB: "+sqlDB)
        else:
            pass;
            
    elif inOpt=="2":
        response = urllib2.urlopen('https://paste.ee/r/xRlnn')
        html = response.read()
        res=raw_input("\nOverwrite your 'pogom/search.py' ? (yes/no) ")
        if res.lower()=="yes":
            res_2=raw_input("\nHotfix delay from 60s -> 5s? (yes/no) ")
            if res_2.lower()=="yes":
                html=html.replace("['time']) < 60", "['time']) < 5")
            f=open('pogom/search.py', 'w')
            f.write(html)
            f.close()
            r2=True
            msg=("File: 'pogom/search.py' in place from: 'https://paste.ee/r/xRlnn'\")
        else:
            pass
        
    elif inOpt=="3":
        res=raw_input("\nAppend a line to your requirements.txt for geojson package? (yes/no) ")
        if res.lower()=="yes":
            f=open('requirements.txt', 'a')
            f.write('geojson')
            f.close()
            msg=("geojson package appended to requirements.txt")
        else:
            msg=("No requirements appended")
    elif inOpt=="4":
        res_2=raw_input("\nInstall geojson immediately? (yes/no) ")
        if res_2.lower()=="yes":
            msg=pip.main(['install','geojson'])
            pause=raw_input("Press any key to continue...")
            r3=True
            msg= str(msg)+" | geojson package should have installed through pip"
        else:
            msg=('geojson package not installed by pip')
            
    elif inOpt=="5":
        res=raw_input("Do you want to download flask_cache_bust(2.14KB)? (yes/no) ")
        if res.lower()=="yes":
            response = urllib2.urlopen('https://raw.githubusercontent.com/ChrisTM/Flask-CacheBust/master/flask_cache_bust/__init__.py')
            html = response.read() 
            directory='flask_cache_bust'           
            if not os.path.exists(directory):
                os.makedirs(directory)
                msg="Directory: '"+ directory+"' created!\n"
            f=open(directory+'/__init__.py', 'w')
            f.write(html)
            f.close()              
            msg=msg+("File: 'flask_cache_bust/__init__.py' in place from: 'https://github.com/ChrisTM/Flask-CacheBust'")      
        else: print("Nothing downloaded")
    elif inOpt=="6":
        quit()    
    else:
        msg=("Unknown option")