import gspread
import pandas

gc = gspread.login('my@email.com', 'supersecretepassword')
book = gc.open('Spreadsheet name')
sheet = book.sheet1 #choose the first sheet
dataframe = pandas.DataFrame(sheet.get_all_records())