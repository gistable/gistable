from lxml import etree
import json

outfile = open("kv.json", "w+")
outfile.write("[\n")

tree = etree.parse("medline11n0001.xml")
elem = tree.getroot()

# for every item in the xml file, parse it and create a JSON object of it
recordcount = 1
for sub in elem:
     
    if recordcount != 1:
        outfile.write(",")
        
    # parse the item into a dict        
    doc = {}
    doc["collection"] = ["medline"]
    
    # there is always a pmid 
    doc["pmid"] = sub.find("PMID").text

    # try/except blocks for each field we are interested in
    try:
        doc["affiliation"] = sub.find("Affiliation").text
    except:
        pass

    try:
        keywordlist = sub.find("KeywordList")
        doc["keywords"] = []
        for keyword in keywordlist:
            doc["keywords"].append(keyword.text)
    except:
        pass

    try:
        grantlist = sub.find("GrantList")
        doc["grants"] = []
        for grant in grantlist:
            doc["grants"].append(grant.find("Agency").text)
    except:
        pass

    try:
        article = sub.find("Article")
        doc["title"] = article.find("ArticleTitle").text
        doc["language"] = article.find("Language").text
    except:
        pass
    
    try:
        doi = article.find("ELocationID")
        if doi.attrib["EIdType"] == "doi":
            doc["doi"] = doi.text
    except:
        pass
    
    try:
        authorlist = article.find("AuthorList")
        doc["author"] = []
        for author in authorlist:
            lastname = author.find("LastName").text
            firstname = author.find("ForeName").text
            initials = author.find("Initials").text
            doc["author"].append(firstname + " " + lastname)
    except:
        pass

    try:
        journal = article.find("Journal")
        doc["journal"] = journal.find("Title").text
        doc["journaliso"] = journal.find("ISOAbbreviation").text
        doc["issn"] = journal.find("ISSN").text
    except:
        pass
    
    try:
        journalissue = journal.find("JournalIssue")
        doc["volume"] = journalissue.find("Volume").text
    except:
        pass
    
    try:
        journalpubdate = journalissue.find("PubDate")
        doc["year"] = journalpubdate.find("Year").text
        doc["month"] = journalpubdate.find("Month").text
    except:
        pass

    try:
        articledate = article.find("ArticleDate")
        doc["year"] = articledate.find("Year").text
        doc["month"] = articledate.find("Month").text
        doc["day"] = articledate.find("Day").text
    except:
        pass
    
    # dump the dict to JSON
    data = json.dumps(doc, indent=4)
    outfile.write(data + "\n\n")

    # increment the record count then it is time to loop
    recordcount += 1

outfile.write("]")
