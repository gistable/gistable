import mechanize
import pandas as pd
import os

from bs4 import BeautifulSoup 
from IPython.core.display import display, HTML

br = mechanize.Browser()

br.open("http://www.adm.uwaterloo.ca/infocour/CIR/SA/under.html")
br.select_form(nr=0)
br.form["subject"] = ["CS"]
br.form["cournum"] = "230"
br.submit()

soup = BeautifulSoup(br.response().read())
table = pd.read_html(str(soup.table.table))[0]

table.columns = table.loc[0,:]
table = table.loc[1:,:]
table = table.set_index(["Class", "Comp Sec"])

can_enroll = (table["Enrl Cap"] > table["Enrl Tot"]).any()

if can_enroll:
    os.system('say "time to enroll"')
    print("time to enroll")
else:
    os.system('say "you will never graduate on time"')
    print("you will never graduate on time")