from selenium import webdriver
driver = webdriver.Firefox()
driver.get('https://www.facebook.com/')

with open('jquery-1.9.1.min.js', 'r') as jquery_js: 
    jquery = jquery_js.read() #read the jquery from a file
    driver.execute_script(jquery) #active the jquery lib
    driver.execute_script("$('#email').text('anhld')")