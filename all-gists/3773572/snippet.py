import cx_Oracle
 
conn = cx_Oracle.Connection("userid/password@tns")
curs = conn.cursor()
curs.callproc("dbms_output.enable")
 
sqlCode = """
some long
sql code 
with dbms_output
"""
 
curs.execute(sqlCode)
 
statusVar = curs.var(cx_Oracle.NUMBER)
lineVar = curs.var(cx_Oracle.STRING)
while True:
  curs.callproc("dbms_output.get_line", (lineVar, statusVar))
  if statusVar.getvalue() != 0:
    break
  print lineVar.getvalue()