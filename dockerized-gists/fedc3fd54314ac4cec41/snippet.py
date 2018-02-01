# Copyright (c) 2015 Heinrich Hartmann
# MIT License http://choosealicense.com/licenses/mit/

import gdata.spreadsheet.service

class GoogleDriveConnection(object):
    def __init__(self, email, password):
        self.client = gdata.spreadsheet.service.SpreadsheetsService()
        self.client.ClientLogin(email, password)
    
    def listSpreadsheets(self):
        for entry in self.client.GetSpreadsheetsFeed().entry:
            yield entry.title.text
            
    def getSpreadsheet(self, title):
        for entry in self.client.GetSpreadsheetsFeed().entry:
            if entry.title.text == title:
                key = entry.id.text.split('/')[-1]
                return GoogleSpreadsheet(client, key)
            
        raise NameError(title)

class GoogleSpreadsheet(object):
    def __init__(self, client, spreadsheet_key):
        self.client = client
        self.spreadsheet_key = spreadsheet_key
        
    def getWorksheets(self):
        for entry in self.client.GetWorksheetsFeed(self.spreadsheet_key).entry:
            yield entry.title.text

    def getWorksheet(self, title):
        for entry in self.client.GetWorksheetsFeed(self.spreadsheet_key).entry:
            if entry.title.text == title:
                worksheet_key = entry.id.text.split('/')[-1]
                return GoogleWorksheet(self.client, self.spreadsheet_key, worksheet_key)
        raise NameError(title)

class GoogleWorksheet(object):
    def __init__(self, client, spreadsheet_key, worksheet_key):
        self.client = client
        self.spreadsheet_key = spreadsheet_key
        self.worksheet_key   = worksheet_key
        
    def getRecords(self):
        list_feed = client.GetListFeed(self.spreadsheet_key, self.worksheet_key)
        for entry in list_feed.entry:
            yield dict((key, entry.custom[key].text) for key in entry.custom)
            
    def addRecord(self, record):
        rc = self.client.InsertRow(record, self.spreadsheet_key, self.worksheet_key)
        if not instanceof(rc, gdata.spreadsheet.SpreadsheetsList):
            raise IOError()
            
if __name__ == "__main__":
    import json
    with open("GoogleAppPw.json") as fh:
        config = json.load(fh)
    assert(config)
    
    connection = GoogleDriveConnection(config['email'], config['password'])
    worksheet  = connection.getSpreadsheet(config['spreadsheet']).getWorksheet(config['worksheet'])
    for r in w.getRecords():
        print r.values()