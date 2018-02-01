#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import json
import os
import csv

API_URL = "http://wiki.piratenbrandenburg.de/api.php"
# remove content and applicaions_list manually
CATEGORIES = ["Kategorie:Landesparteitag_2013.2_Satzungsänderungsantrag",
              "Kategorie:Landesparteitag_2013.2_Grundsatzprogrammantrag",
              "Kategorie:Landesparteitag_2013.2_Wahlprogrammantrag",
              "Kategorie:Landesparteitag_2013.2_Positionspapier",
              "Kategorie:Landesparteitag_2013.2_Sonstiger_Antrag",]
MAX_PAGEIDS = 50

def get_json(endpoint):
  url = ''.join([
           API_URL,
           '?',
           endpoint,
           '&format=json',
           ])
  print url
  return urllib2.urlopen(url).read()

def get_category(category, query_continue=""):
  data = get_json("action=query&list=categorymembers&cmtitle=%s&cmcontinue=%s" % (category, query_continue))
  json_data = json.loads(data)
  if not "query" in json_data:
    print category
    print json_data
  pages = json_data["query"]["categorymembers"]
  if "query-continue" in json_data:
    pages += get_category(category,json_data["query-continue"]["categorymembers"]["cmcontinue"])
  return pages

def list_applications(categories):
  if os.path.isfile("application_list"):
    f = open('application_list','r')
    return json.load(f)
  return download_applications(categories)

def download_applications(categories):
  applications = _list_applications(categories)
  f = open('application_list','w+')
  json.dump(applications, f)
  f.flush()
  return applications

def _list_applications(categories):
  applications = {}
  for category in categories:
    pages = get_category(category)
    applications[category] = pages
  return applications

def get_raw_pageid(pageid):
  data = get_json("action=query&prop=revisions&rvprop=content&pageids=%s" % pageid)
  json_data = json.loads(data)
  pages = json_data["query"]["pages"]
  content = []
  for pageids in pages:
    content += pages[pageids]["revisions"]
  return content

def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

def get_pageid(pageids):
  pages = []
  for chunk in chunks(pageids, MAX_PAGEIDS):
    pages += get_raw_pageid("|".join(str(i) for i in chunk))
  return pages

def _list_content(applications):
  pageids = {}
  content = {}
  for category in applications.iterkeys():
    for application in applications[category]:
      if category in pageids:
        pageids[category] += [application["pageid"]]
      else:
        pageids[category] = [application["pageid"]]
    content[category] = get_pageid(pageids[category])
  return content

def download_content(applications):
  content = _list_content(applications)
  f = open('content','w+')
  json.dump(content,f)
  f.flush()
  return content

def list_content(applications):
  if os.path.isfile("content"):
    f = open('content','r')
    return json.load(f)
  return download_content(applications)

def parse_content(content):
  applications = {}
  for category in content.iterkeys():
    applications_for_category = []
    for application_content in content[category]:
      application = mediawiki_template(application_content["*"])
      #if application["Eingereicht"] != "":
      if "Antragsteller" in application:
        application["autor"] = application.get("Antragsteller")
      if "Antragstitel" in application:
        application["titel"] = application.get("Antragstitel")
      if "Titel" in application:
        application["titel"] = application.get("Titel")
      #Titel zu titel conversion
      applications_for_category.append(application)
    applications_for_category.sort(key = lambda a: a.get("titel"))
    applications[category] = applications_for_category
  return applications

def mediawiki_template(mw_string):
  """ returns media wiki template element as a hash"""
  #Split content inside Template
  strings = mw_string.split("{{")[1].split("}}")[0].split("\n|")
  #remove "Antragsfabrikat"
  strings = strings[1:]
  mw_hash = {}
  for string in strings:
    keyval = string.split("=",1)
    if 2 != len(keyval):
      raise SyntaxError("Mediawiki parsing Error %s" % keyval)
    keyval = [s.strip() for s in keyval]
    key, val = keyval
    mw_hash[key] = val
  return mw_hash

def filter_content(content):
  """ simple filter for some html tags to plain text"""
  content = content.replace("<sup>1</sup>","¹")
  content = content.replace("<sup>2</sup>","²")
  content = content.replace("<sup>3</sup>","³")
  content = content.replace("<br>","\n")
  content = content.replace("<br\>","\n")
  content = content.replace("<br\\n>","\n")
  content = content.replace("<br />","\n")
  content = content.replace("<br/>","\n")
  return content


def write_content(applications, positions=[]):
  open_position = []
  open_position.extend(positions.keys())
  for category in applications:
    f = open(category,'w+')
    writer = csv.writer(f,delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow( ("Number","Title","Text","Reason",
                      "Submitter (First Name)","Sachgebiet"))
    for a in applications[category]:
      try:
        #number = applications_position.index(a.get("titel")) + 1
        open_position.remove(a.get("titel"))
      except ValueError:
        if not "titel" in a:
          a["titel"] = ""
        print '"' + a.get("titel") + '" im Antragsbuch nicht gefunden'
        continue
      if not "autor" in a:
        a["autor"] = ""
      if not "text" in a:
        a["text"] = ""
      if not "begruendung" in a:
        a["begruendung"] = ""
      writer.writerow( ( positions[a.get("titel")],
                        a.get("titel").encode('utf8'),
                        "<pre>"+filter_content(a.get("text").encode('utf8'))+"</pre>",
                        "<pre>"+filter_content(a.get("begruendung").encode('utf8'))+"</pre>",
                        a.get("autor").encode('utf8'),
                        "") ) #sachgebiet
    f.flush()
    f.close()
  if open_position != []:
    print "\nAnträge aus dem Antragsbuch, die nicht gefunden wurden: "
    for a in open_position:
      print '"' + a + '"'

#def write_participants(applications):
#  f = open("participants",'w+')
#  authors = []
#  writer = csv.writer(f,delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
#  writer.writerow( (
#    "title", "first name", "last name", "gender", "email", "group id",
#    "structure level", "committee", "about me", "comment", "is active"))
#  for category in applications:
#    for a in applications[category]:
#      if not "autor" in a:
#        a["autor"] = ""
#      if a.get("autor") in authors:
#        continue
#      authors.append(a.get("autor"))
#      writer.writerow( ( "",
#                        a.get("autor").encode('utf8'),
#                        "",
#                        "",
#                        "",
#                        "",
#                        "",
#                        "",
#                        "",
#                        "",
#                        "") ) #sachgebiet
#  f.flush()
#  f.close()

def get_application_positions(filename):
  f = open(filename,'r')
  lines = {}
  for l in f.readlines():
    line = l.decode('utf8').strip().split(" - ")
    lines[line[1]] = line[0]
    #Titel => WPXX
  return lines

if __name__ == '__main__':
  #download_applications(CATEGORIES)
  applications = list_applications(CATEGORIES)
  #download_content(applications)
  content = list_content(applications)
  applications = parse_content(content)
  #Ein Titel per Zeile, TO-Reihenfolge gegeben
  positions = get_application_positions("reihenfolge-lpt2013.2") 
  #write_participants(applications)
  write_content(applications, positions)

