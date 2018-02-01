client = gdata.spreadsheets.client.SpreadsheetsClient()
token.authorize(client)

sps = client.GetSpreadsheets()
print len(sps.entry) # shows how many spreadsheets you have

sprd_key = 'put an appropriate spreadsheet key here'
wss = client.GetWorksheets(sprd_key) # get a list of all worksheets in this spreadsheet, to look around for info in a debugger
ws = client.GetWorksheet(sprd_key, 'od6') # get the first worksheet in a spreadsheet; seems 'od6' is always used as a WS ID of the first worksheet

cq = gdata.spreadsheets.client.CellQuery(3,3,1,1) # form a query to get a cell in R3C1

cs = client.GetCells(sprd_key, 'od6', q=cq)
cell_ent = cs.entry[0]
print cell_ent.cell.input_value # get a current cell value
cell_ent.cell.input_value = '112'
client.Update(cell_ent) # update a cell entity, sending info back to Google
