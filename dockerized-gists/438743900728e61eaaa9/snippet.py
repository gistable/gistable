import os

#make sure every chromedriver.exe is closed
with os.popen('tasklist') as task_list_file:
    task_list_str = task_list_file.read()

flag = task_list_str.find("chromedriver.exe")
if flag != -1:
    os.system("taskkill /F /IM chromedriver.exe") 