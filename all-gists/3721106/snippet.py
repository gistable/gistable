import pywinauto
import os
import doctest
from pywinauto import application
from time import sleep
from pywinauto.timings import Timings

Timings.Slow()
Timings.after_sendkeys_key_wait =0.015
Timings.after_menu_wait =0.1
Timings.after_click_wait =0.2
Timings.after_closeclick_wait =0.2

path_to_files = "C:\\My Documents\\Mini Projects\\sk2ToMol\\input\\"
path_to_output = "C:\\My Documents\\Mini Projects\\sk2ToMol\\output\\"

def escape(filename):
   """Escape the filename
   >>> escape("(3-ethoxypropyl)mercury bromide.sk2")
   '{(}3-ethoxypropyl{)}mercury bromide.sk2'
   """
   newfilename = filename.replace("(", "{(}").replace(")", "{)}")

   return newfilename

if __name__ == "__main__":
   doctest.testmod()

   dir = os.listdir(path_to_files);
   app = application.Application()
   dontConvert = False # Set to True to skip successfully converted files
   for filename in dir:
      if filename.endswith("ContinueHere.sk2"):
         dontConvert = False
      if dontConvert:
         continue
         
      window = app.window_(title_re='ACD/ChemSketch.*\.sk2')
      window.TypeKeys("^o")

      window2 = app.window_(title_re='Open Document')
      window2.TypeKeys("%n")
      filename = path_to_files + escape(filename)

      window2.TypeKeys(filename +"%o", with_spaces = True)
      sleep(0.2)
      window.TypeKeys("%fe")
      window3 = app.window_(title_re='Export')
      window3.TypeKeys("{ENTER}");

      window = app.window_(title_re='ACD/ChemSketch.*\.sk2')
      sleep(0.5)
      window.TypeKeys("^w")