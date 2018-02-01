# codign: utf-8

import pandas as pd
import xlsxwriter


df = pd.read_csv("test.csv")

wb = xlsxwriter.Workbook("test.xlsx")
ws = wb.add_worksheet()


row = 0
col = 0

ws.write(row, col, "data")

for d in df["data"]:
    row += 1
    ws.write(row, col, d)

chart1 = wb.add_chart({"type": "line"})
chart2 = wb.add_chart({"type": "line"})
chart3 = wb.add_chart({"type": "line"})

chart1.add_series({
    "name": "=Sheet1!$A$1",
    "values": "=Sheet1!$A$2:$A$30001",
    })

ws.insert_chart("B1", chart1)

chart2.add_series({
    "name": "=Sheet1!$A$1",
    "values": "=Sheet1!$A$30002:$A$60001",
    })

ws.insert_chart("J1", chart2)

chart3.add_series({
    "name": "=Sheet1!$A$1",
    "values": "=Sheet1!$A$60002:$A$90001",
    })

ws.insert_chart("R1", chart3)

wb.close()


