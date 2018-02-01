# -*- coding: utf-8 -*-


def glassdoorScrape(get_short = False):
    
    """
    Created on Tue Aug 16 22:41:30 2016
    Scrape Glassdoor website using SELENIUM
    @author: Diego De Lazzari
    """

    from selenium import webdriver
    #from bs4 import BeautifulSoup # For HTML parsing
    from time import sleep # To prevent overwhelming the server between connections
    from collections import Counter # Keep track of our term counts
    from nltk.corpus import stopwords # Filter out stopwords, such as 'the', 'or', 'and'
    import pandas as pd # For converting results to a dataframe and bar chart plots
    from selenium.webdriver.common import action_chains, keys
    from selenium.common.exceptions import NoSuchElementException
    import numpy as np
    import sys


    # call the helper
    
    from helperP3 import load_obj, save_obj, init_glassdoor, searchJobs, text_cleaner, get_pause
    
        # 1- Load existing dictionary. Check for initial dictionary. 
        # If empty initialize
            
    try:               
        jobDict = load_obj('glassDoorDict')
        link =    load_obj('glassDoorlink')
    except:
        save_obj([], 'glassDoorlink')
        save_obj({}, 'glassDoorDict')
        
        jobDict = load_obj('glassDoorDict')
        link =    load_obj('glassDoorlink')    
    
    # 2- Choose what you want to do: 
#        get_shot => Scraping for links, 
#        get_long => Scraping for data,


    get_long = (not get_short)
    
    if get_short or get_long:
        
    # 3- initialize website, cities and jobs
        
        website = "https://www.glassdoor.com/index.htm"
        
        jobName_lst = ['Data Scientist', 'Data Analyst']
        jobName = np.random.choice(jobName_lst)
    
        city_lst = ['San Jose','New York','San Francisco','Detroit','Washington','Austin','Boston','Los Angeles',' ']
        city = np.random.choice(city_lst)        
        
        # Initialize the webdriver
        
        browser = init_glassdoor()  
    
    # 4- Scrape the short list or the links (when you ae done, both are false)
    
    
    if get_short:
    
        browser.get(website)
            
        # search for jobs (short description) 
        try:    
                    update_jobDict, update_link = searchJobs(jobName, city, jobDict, link)
#                    sleep(get_pause())
        except:
            sys.exit("Error message")
            
        # save dictionary and link     
    
        save_obj(update_jobDict, 'glassDoorDict')
        save_obj(update_link, 'glassDoorlink')
        
     # 5- Scrape the job description, for every link
                    
    if get_long:        
        
        while len(link) > 0:
            
             
            try:
                rnd_job = np.random.choice(range(len(link)))
                
                ids = link[rnd_job][0]
                page = link[rnd_job][1]
                
                browser.get(page)                 
                sleep(3)
                
                # Extract text   //*[@id="JobDescContainer"]/div[1]
                desc_list = browser.find_element_by_xpath('//*[@id="JobDescContainer"]/div[1]').text
                description = text_cleaner(desc_list)
                
                # Update dictionary and remove succe
                jobDict[ids].append(description)               
                dummy=link.pop(rnd_job)
                               
                # if everything is fine, save
                save_obj(jobDict, 'glassDoorDict')
                save_obj(link, 'glassDoorlink')
                                                
                print 'Scraped successfully ' + ids
                
                sleep(get_pause())
            except:   
                print ids + ' is not working! Sleep for 10 seconds and retry'
                print 'Still missing ' + str(len(link)) + ' links' 
                sleep(8)
                
        browser.close()
        
    return