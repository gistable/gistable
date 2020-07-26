# -*- coding: utf8 -*-
#!/usr/bin/python

### Imports libraries

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    import MySQLdb ### Not standard (not included in the standard Python package)
    from MySQLdb import OperationalError
    from MySQLdb import ProgrammingError
    from MySQLdb import InterfaceError
import shelve
from string import lower, upper
from string import replace
from operator import itemgetter
from PyRTF import * ### Not standard
from random import shuffle
import os
import random
from datetime import date
from time import sleep
import datetime
import csv
import copy
from urllib import urlopen
from xml.dom.minidom import parseString, parse
import unicodedata
from ltchinese import conversion ### Not standard
from tkMessageBox import showinfo
from wordnik import *

### There are some problems with handling weird letters in definitions, so this is the list that the program looks out
### for and doesn't allow. Not a very elegant solution, there's probably some way to deal with the encodings more directly.
global foreign_letters
foreign_letters = ['â', 'ê', 'î', 'ô', 'û', 'é', 'ë', 'ï', 'ü', 'ÿ', 'ç', 'ä', 'ö','ü','ñ']

###################################################################################
### FOUNDATIONAL COMMANDS
# do_command(command)
# get_words_list(dbase)
# get_generator_data(dbase, word, q_type)
###################################################################################

### This isn't used anywhere in the program, it's only if you want to test new commands a little faster
def do_test_command(command):
    cursor.execute(command) ### Executes the command
    reply = cursor.fetchall() ### Grabs data
    conn.commit()

    return reply ### Return data

### A more complicated way of doing commands, which fixes the connection time-out problem. Because 'conn' and 'cursor' are
### global variables, they can be redefined and don't need to be passed back along with the data, though that would be the
### more elegant and proper solution. In general, global variables are a weak spot in my knowledge, and I'm not sure why
### this particular solution works, while others don't.
def do_command(command):
    while True:
        try:
            cursor.execute(command) ### Executes the command
            reply = cursor.fetchall() ### Grabs data
            conn.commit()
            break
        except (OperationalError, InterfaceError):
            print "Connection timed out ("+command+"). Reconnecting..." ### If MySQL went away, reconnect
            host = "www.sophosacademics.com"
            user = "sophos_vocuser"
            try:
                conn.close()
            except ProgrammingError: ### Try closing the connection, but catch an error if it's already closed
                pass
            try:
                global conn
                conn = MySQLdb.connect(host = host, user = user, passwd = sophos_password) ### Reconnect globally
                global cursor
                cursor = conn.cursor()

                cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED") ### Allow different reads based on in-moment changes
                cursor.execute("SET SESSION WAIT_TIMEOUT = 60")
                cursor.execute("USE %s" % db)
            except OperationalError:
                pass
            except ProgrammingError:
                pass

    return reply ### Return data


### There's a file called vocab-log.csv in the same folder, which tracks activity. Three columns: student name, file name (changes depending on what operation you're in, obviously) and timestamp
def add_to_log(student_name, file_name):
    try:
        logwriter = open('vocab-log.csv', 'a') ## the 'a' is important because it means it starts writing at the end of the file, I think
    except IOError: ## actually, this error doesn't seem to come up, the open function just makes a new file
        print "No log file or log file in use. Make vocab-log.csv (Name/File/Date/Time)."
        return
    now = datetime.datetime.now()
    row = str(student_name+","+file_name+","+str(now.year)+"."+str(now.month)+'.'+str(now.day)+","+str(now.hour)+':'+str(now.minute))
    logwriter.write(row)
    logwriter.write("\n")
    logwriter.close()
    return

### Boolean function, which figures out whether the database, or a particular word in the database, is locked
def locked(dbase, word = False):
    if not word: ## if you're looked for a word's status
        row = do_command("SELECT lockvar FROM %s WHERE word = '__lockvar__'" % dbase)
        try:
            if eval(row[0][0]):
                return True
            else:
                return False
        except (TypeError, IndexError):
            return False

    else: ## if you're looking for a db's status
        row = do_command("SELECT lockvar FROM %s WHERE word = \'%s\'" % (dbase, word))
        try:
            if eval(row[0][0]):
                return True
            else:
                return False
        except (TypeError, IndexError):
            return False
        
    return False

### Locks a database (keep in mind this is an "in-house" solution, it's just text in the database that gets changed. It's
### not a command within MySQL that locks the database under the hood somehow. 
def lock_dbase(dbase):
    do_command("UPDATE %s SET data = 'True', lockvar = 'True' WHERE word = '__lockvar__'" % dbase)
    return

### Unlocks the database
def unlock_dbase(dbase):
    do_command("UPDATE %s SET data = 'False', lockvar = 'False' WHERE word = '__lockvar__'" % dbase)
    return

### Locks a word (not used in current set-up)
def lock_word(dbase, word):
    do_command("UPDATE %s SET lockvar = 'True' WHERE word = \"%s\"" % (dbase,MySQLdb.escape_string(word)))
    return

### Unlocks a word
def unlock_word(dbase, word):
    do_command("UPDATE %s SET lockvar = 'False' WHERE word = \"%s\"" % (dbase,MySQLdb.escape_string(word)))
    return

### All the important databases have 3 columns, the WORD, DATA associated with that word in this table and a
### variable for LOCKED or not. This command just produces a list of all the words in a given database
def get_words_list(dbase):
    row = do_command("SELECT word FROM %s" % dbase)
    words = []
    
    for word in row:
        if len(word[0])==0:
            continue
        elif word[0][0] in [' ','-','_']:
            continue
        else:
            words.append(word[0])
            
    return words

### Creates a python dictionary object from a database, using the WORD as the key and the DATA as the value. This is useful
### because it only takes one command call to make the dictionary, and subsequent calls, since the dictionary is local, are
### very fast. On the other hand, if the internet connection is choppy, the one longer call sometimes times-out midway
### through. Still, this approach is much faster (though it allows less flexibility in terms of locking individual words
### as opposed to whole databases)
def turn_dbase_into_dict(dbase):
    row = do_command("SELECT * FROM %s" % dbase)
    data = {}
    for item in row:
        try:
            if item[0]!= '' and item[0][0] not in [' ', '-','_']: ## if it's not nothing and it's not a special cell like the db's locked variable
                data[item[0]] = eval(item[1])
        except IndexError:
            print item

    return data

def get_generator_data(dbase, word, q_type):
    answers = do_command("SELECT data FROM %s WHERE word = \'%s\'" % (dbase, word))
    if len(answers)==0:
        print "Something wrong with: " + word
        return {}
    answers = answers[0][0]
    _answers = {}
    if answers=='{}':
        return _answers
    else:
        answers = eval(answers)
        for answer_key in answers:
            if answer_key[0] == q_type:
                _answers[answer_key] = answers[answer_key]
        return _answers

### Boolean function to see if a word is an entry in a db
def check_if_word_exists_in_db(word, dbase):
    row = do_command("SELECT data FROM %s WHERE word = \'%s\'" % (dbase, word))
    if len(row) == 0:
        return False
    else:
        return True

### Same as above, but for a local python dictionary instead
def check_if_word_exists_in_dict(word, ddict):
    if ddict.has_key(word):
        return True
    else:
        return False

### The next 3 functions were a bigger part of an earlier iteration of the program. They still get used when a testsheet
### gets uploaded and there are new entries. Basically, it's a way of making double-checking more manageable for the user.
### The idea is to break up a big group of entries into groups of 5, and have the user double-check each group of 5 individually.
    
### This takes a big list and sorts it into a list consisting of smaller (<5 item) lists. Could be used for any list.
def sort_into_5s(items):
    temp = []
    sorted_by_5s = []
    for item in items:
        if len(temp) < 5: #keep appending items till length of group = 5
            temp.append(item)
        else:
            sorted_by_5s.append(temp) # then append that group and start again
            temp = []
            temp.append(item)
    if len(temp) != 0:
        sorted_by_5s.append(temp)
        
    return sorted_by_5s


### This function runs the checking operation and spits back a revised list. The input is specific to the program, so it
### can't be used generally for any list.
def check_by_5s(words_by_5s, q_type):
    for group in words_by_5s: # go through each group
        while True: # until the user gives the okay, stay on that group, and print out the latest version of it as the "menu"
            print "\n"
            if len(group) == 0:
                break
            for n in range(len(group)):
                print str(n+1) + ". " + group[n][0]
                print "   "+q_type+" - " + group[n][1]
            print "\n"

            # asks the user which one that want to edit. anything that isn't a correct number moves you to the next group of 5.
            check = raw_input("Enter the number of the word you wish to edit or anything else to continue: ")
            try:
                check = int(check)-1
                if check in range(0,min(5, len(group))): # check if the number is correct
                    print group[check][1] # print the original
                    group[check][1] = raw_input("Enter the edit (hit return to delete). > ") # ask for the edit
                    if group[check] == "": # if the edit is just a return, that word is simply deleted, and will not be included in the test (and the new answer will not be added to the dbase, though the word won't be removed)
                        del group[check]
                    elif q_type == 's': # checks the requirements for a sentence completion
                        while '---' not in group[check][1]:
                            if group[check][1] == "":
                                del group[check]
                                break
                            else:
                                print "You forgot the ---."
                                group[check][1] = raw_input("Enter the edit (hit return to delete). > ") # asks again if missing the ---
                    elif q_type == 'm':
                        group[check][1]=lower(group[check][1])
                else: # anything that isn't a correct number moves you to the next group of 5
                    break
            except (ValueError, IndexError):
                break

    return words_by_5s

### Essentially, flattens the first two layers of a list into one layer. [[a,b],[c,d]] becomes [a,b,c,d]
def flatten_5s(words_by_5s):
    flat = []
    for group in words_by_5s:
        for wset in group:
            flat.append(wset)
    return flat

### A stand-alone function that returns a dictionary object with all of the relevant info. The format is:
### main word : [all words, level]
### Right now, it doesn't catch an error if the csv file isn't there; it will just quite with a standard python error
### This should be fixed.
def get_words_by_level():
    name = 'FINAL LIST.csv'
    reader = csv.reader(open(name, 'rb')) ### there should be an error-catcher here
    words_by_level = {}
    for row in reader:
        entries = eval(row[0])
        for entry in entries:
            words_by_level[entry] = [entries[0], int(row[2])]

    return words_by_level

### based on user-inputted initials, gets the full name of the adviser. (used for file headings)
### Data is stored inside the function, so in case of new advisers, type their info into the adviser key
def get_adviser_fullname(initials):
    initials = lower(initials)
    adviser_key = {} ## add new entries here
    if adviser_key.has_key(initials): 
        submit_to = adviser_key[initials]
    else:
        submit_to = raw_input("Please enter your full name. ") ## if there's no entry, asks for full name

    return submit_to

### based on user-chosen student id, gets the full name of the student. (used for file headings)
### Data is stored inside the function, so in case of new students, type their info into the student key
def get_student_fullname(student_id):
    student_key = {} # add new students here
    
    if student_key.has_key(student_id):
        return student_key[student_id]
    else:
        return student_id ## if there's no entry, it just returns the student id

### based on student id, gets the location of their directory. all files except test sheets (the ones used to generate new
### tests; they're temporary) are saved to this directory. if directory doesn't exist, it saves in the base vocab directory
def get_student_dir(student_id):
    # (make sure to escape backslashes)
    
    base_ext = '\\\\JASON1\\Sophos\\Clients\\' # this is dependent on the current server arrangement
    # since this function is network dependent, it doesn't do anything if used on a computer not connected to the
    # server. This might be something to fix.
    
    student_dir = {} # add new students here
    
    if student_dir.has_key(student_id):
        dir_prefix = base_ext + student_dir[student_id]
        if not os.path.exists(dir_prefix): ## checks if the path exists; if it doesn't, files will be put in the main vocab program directory
            return ""
        else:
            return dir_prefix
    else:
        return ""

### This function hasn't been implemented, but it's for speeding up the passive sheet creation process by immediately
### supplying a student's passive parameters. this assumes that they don't change much. Implementation should be straightforward
def get_student_PA_parameters(student_id):
    # the parameters are [chinese/english definitions, verb phrases?, idioms?, definitions limit]
    student_param = {} # add new students here

    if student_param.has_key(student_id):
        return student_dir[student_id]
    else:
        return False

## Main function for getting a definition for a word. "dbase" means the definitions dbase, chinese or english
## "cn_threshold" is only if *some* words are in english and otherse in chinese, in which case dbase is english definitions
## dbase and dbase2 is chinese definitions dbase. words_by_level is included if this sorting is necessary. (it would be
## more elegant to do that bit of sorting before this function is called)
def get_definition(word, dbase, language = 'e', cn_threshold = False, dbase2 = False, words_by_level = False):
    if language == 'e':
        defi = get_en_definition_wn(word, dbase)
    elif language == 'c':
        defi = get_cn_definition(word, dbase)
    elif language == 'b': # if it's a mix of chinese and english definitions, then...
        if words_by_level.has_key(word): # ... see if the words by level list has the word
            if words_by_level[word][1] in cn_threshold: # get chinese defi if level of word is in the chinese threshold
                defi = get_cn_definition(word, dbase2)
            else: # english otherwise
                defi = get_en_definition(word, dbase)
        else: # if words_by_level doesn't have the word, default to english definition (though this should in theory never happen)
            defi = get_en_definition(word, dbase)
    return defi

# wordnik definition getter
def get_en_definition_wn(word, dbase):
    if dbase.has_key(word): # first, checks if we already have the word in our definitions database
        return dbase[word]
    else:
        apiUrl = 'http://api.wordnik.com/v4'
        apiKey = 'afb0601cfb3549b52e0010482ff02f04351b041680401a749'
        client = swagger.ApiClient(apiKey, apiUrl)
        wordApi = WordApi.WordApi(client)
        
        definitions = wordApi.getDefinitions(word, sourceDictionaries="wiktionary")
        defi_list = []
        if definitions != None:
            for defi in definitions:
                defi_list.append([defi.partOfSpeech, defi.text])

        return defi_list

## Get's the english definition for a word, whether from our database or from dictionary.com
## There is a limit on the dictionary.com api, something like 1000 calls a day.
def get_en_definition(word, dbase):
    if dbase.has_key(word): # first, checks if we already have the word in our definitions database
        return dbase[word]
    else:
        #print "Finding definition for: " + word
        api_key = "7b44ly3m8yootpmdgni4s7aprwns4l0bw5fi3j4bit" # this is from my dictionary.com account, may need a different one at some point
        url = "http://api-pub.dictionary.com/v001?vid="+api_key+"&q="+word+"&type=define" # html for a word
        data = []
        try:
            parsed = parse(urlopen(url)) # gets the data from the website (xml)
            # most of the below is for
            entry_list = parsed.getElementsByTagName('entry') ## gets the various entries (i think only important for homonyms)
            for entry in entry_list:
                disp_f = entry.getElementsByTagName('display_form')
                _disp_word = str(disp_f[0].childNodes[0].nodeValue)
                disp_word = _disp_word.replace('&middot;','') # replaces the syllable seperating dot with nothing; the "disp_word" is not always the same as the original word, it can be a verb phrase or idiom as well
                pos_list = entry.getElementsByTagName('partofspeech') # a list of entries for the word by part of speech (POS)
                for pos in pos_list:
                    _pos = str(pos.getAttribute('pos')) #gets the POS
                    defi_list = pos.getElementsByTagName('def') # gets the list of definitions for that pos
                    _defi = ''
                    for defi in defi_list:
                        try:
                            defi_str = str(defi.childNodes[0].nodeValue) # for some reason, the definitions aren't exactly strings, so we have to stringify them
                        except UnicodeEncodeError:
                            ### this is a ghetto fix. they use smart quotes and other things for some defs,
                            ### which breaks the str() function. We need strings, so right now i have the user
                            ### fix the problem manually by retyping the definition without the offending characters.
                            defi_uni = unicode(defi.childNodes[0].nodeValue)
                            print defi_uni
                            print "Unicode error, copy-paste the above definition below and fix the problem."
                            showinfo('Unicode Error', 'Unicode Error (ignore the \'tk\' window)') # This makes a little graphical pop-up that alerts the user to the problem
                            defi_str = raw_input(">> ")
                            
                        if _defi == '': # the first definition
                            _defi = defi_str
                        else:
                            _defi = _defi + "; " + defi_str # add a ; between subsequent definitions
                    if _pos not in ('verb phrase','idiom'):
                        data.append([_pos, _defi])
                    else:
                        data.append([disp_word, _pos, _defi]) # for idioms and word phrases, keep the word as well
        except:
            print "Definition error: " + word
            # some words just get errors; they're usually the same words, and usually are ones with french marks in traditional spellings 
            data = []
        if data != []: # put the data into the database
            do_command("""INSERT INTO dictionary (word, data) VALUES (\"%s\", \"%s\")""" % (MySQLdb.escape_string(str(word)), MySQLdb.escape_string(str(data))))
        return data

# this function has been the most recently remade. it is the same as the above, but gets the Chinese definition instead of the
# English definition. it had to be remade because our previous API source, dict.cn, stopped offering (or broke) it's API,
# and so I found another source that works. unfortunately, unlike the dict.cn API, which was very fast, this one is super
# slow and prone to locking up the program. It doesn't seem to have a problem when run through a browser, but out of
# python it really has trouble. the dbase variable in this function is the cn_dictionary dbase, rather than the standard one.
# BTW, there are some difference between the new and old APIs and how they format their data; if the old API starts working
# again, or you find a new API and want to look at how we dealt with the last one, just go to an old version of the vocab program
def get_cn_definition(word, dbase):
    if dbase.has_key(word): # if we have the definition in the dbase, just return that definition
        return dbase[word]
    else:
        url = "http://dict-co.iciba.com/api/dictionary.php?w="+word # the API call
        try:
            text = urlopen(url)
        except IOError: # this error occurs a lot with Chinese definitions, I think it's just a time-out
            counter = 0
            while True: # if we get that error
                if counter == 20: # we try another 20 times before we quit
                    print "skipped (timeout): " + word
                    return []
                sleep(1) # we wait one second between calls; this seems to help a bit
                try:
                    text = urlopen(url) # here is our re-connect attemp
                    break
                except IOError:
                    counter += 1
                    continue

        text = text.read() # get the xml text
        parsed = parseString(text) # parse the xml

        # a conversion chart between the POS as the API provides it and the POS as we want it.
        pos_index = {'vt':'verb (used with object)', 'vi':'verb (used without object)','v':'verb', 'n':'noun','adv':'adverb',
                             'adj':'adjective','art':'article','abbr':'abbreviation','pron':'pronoun','prep':'preposition','conj':'conjunction',
                             'num':'number', 'int':'interjection', 'pref':'prefix', 'interj':'interjection', 'prop':'preposition',
                             'aux':'auxilliary', 'v.aux':'auxiliary', 'suf':'suffix', 'vt.& vi':'verb'}
        # not sure if this is 100% complete after the transition to the new API

        pos_list = parsed.getElementsByTagName('pos') # this gets a list of the parts of speech        
        def_list = parsed.getElementsByTagName('acceptation') # and this gets a list of the definitions
        
        data = []
        if len(pos_list)!=len(def_list): # unlike the English API, the POS and definitions data is seperate, so here we just check that there's a pos for every definition
            print 'uneven pos/defi problem: ' + word
        else: # if the POS and definitions line up
            for num in range(len(pos_list)): # we're gonna go through each POS and definition (pos_list and def_list are the same length, obviously)
                try:
                    _pos = pos_list[num].childNodes[0].nodeValue # and extract the POS and the def
                    _def = def_list[num].childNodes[0].nodeValue
                except IndexError:
                    break
                if pos_index.has_key(_pos[:-1]): # if we can find the POS we extracted in our pos_index (see above), then replace it with the version we want
                    _pos = pos_index[_pos[:-1]]
                else:
                    try:
                        _pos = str(_pos) # otherwise just stringify the pos they give
                    except (ValueError, TypeError):
                        _pos = "other" # and if that doesn't work, just make it 'other'
                clean_def = '' # we can't just use the definition straight-up, we have to clean it first (see below)..
                for letter in _def: # .. so we go letter by letter
                    if letter == '\n': # we skip any line breaks
                        pass
                    else: # otherwise we're gonna add the letter, but first..
                        try:
                            temp = conversion.python_to_ncr(letter, decimal=True) # this function, from the ltchinese pack, turns the chinese characters into decimals. we need to do this because pyrtf (I think - it may be python) can't handle Chinese characters directly
                            temp = '\\u'+temp[2:-1]+'?' # and this extra text packages that number in a way that pyrtf will be able to read it when we print the passive assignment (this is just magic as far as I can tell; encoding behavior is one thing I've never gotten a handle on with python. this works, but it's not a solution i feel terribly confident it)
                            clean_def += temp # add the processed character to the cleaned up definition
                        except ValueError:
                            clean_def += letter # if it's not a Chinese character, we just add it directly, without the packaging
                data.append([_pos,clean_def]) # finally, add the POS and cleaned up definition to the data we're gonna send to our db

            # send the data to mySQL
            do_command("""INSERT INTO cn_dictionary (word, data) VALUES (\"%s\", \"%s\")""" % (MySQLdb.escape_string(str(word)), MySQLdb.escape_string(str(data))))
            
        return data # and back to the function

### This function tracks the progress of finding the definitions for the words in a particular passive sheet
def progress_tracker(count, total, last): # count = number of words defined, total = total number of words, and last is last % complete displayed
    progress = float(count)/float(total)
    if progress-last > .05: ## you can change this number to see if you want to change how often it prints progress; right now it's every 5%
        print str(int(progress*100)) + '% complete. (' + str(count) + '/' + str(total) + ')'
        return progress
    else:
        return last

###################################################################################
### UPLOAD NEW WORDS TO ACTIVE/PASSIVE COMMANDS
# upload_csv_for_sdb(input_file_name)
# upload_to_sdb_checker(words)
# ask_overwrite()
# delete_word_from_db(word, dbase)
# add_word_to_db(word, dbase, date=False, source=False, passive_update=False)
# upload_to_sdb_error_check(words)
# upload_to_sdb(student)
# upload_to_sdb_passive(student)
###################################################################################

### Turns a word list (word/date/source) .csv into a list.
def upload_csv_for_sdb(input_file_name):
    
    words = []
    try:
        reader = csv.reader(open(input_file_name, "rb")) # open the file
    except IOError:
        print "No such file! Exiting."
        return False
    for row in reader:
        words.append([row[0],row[1],row[2]]) # convert file to list

    return words

### This function checks the format of word lists (word/date/source). However, since these sheets are now almost always generated
### automatically (and, in truth, unnecessary), it should never return errors (unless the user does use one of the
### deprecated functions, specifically A and B).
def upload_to_sdb_checker(words):
    new_words = []
    error = False
    words_list = []
    
    for word in words: # poorly formed; this should say word, date, source in words, but below these are treated as word[0], word[1], word[2]
        new_word = lower(word[0]) # make all words lower case
        if new_word in words_list: # ignore any words entered twice
            print "Repeat word ignored: " + new_word
            continue
        else:
            words_list.append(new_word) # this just keeps track of the words so far so that the above operation can be performed
            
        if len(new_word) == 0: # skip blanks
            continue
        for letter in new_word: # check for any foreign letters; there should be a better way to do this
            if letter in foreign_letters:
                print "Foreign letter error: " + new_word
                error = True
        if new_word[0] == ' ' or new_word[-1] == ' ': # if the first or last letter of the word is whitespace, that's a paddlin'
            print "Whitespace error (word): " + new_word
            error = True
        try: # word[1] = the date
            if word[1][:3]!='201': # years should be in this decade, watch out for Y2K2, this program will shit bricks
                print "Date error: " + new_word
                error = True
            new_date = date(int(word[1][:4]),int(word[1][4:6]),int(word[1][6:]))
        except (ValueError, IndexError): # if the int() function fails, you've got letters in your dates, or else if date() fails it's a bad date; right now there's no distinciton between the two errors
            print "Date error: " + new_word
            error = True
            new_date = word[1]
        new_source = word[2] # word[2] = the source
        if len(new_source) == 0: # no entered source
            print "No source: " + word
            error = True
        elif new_source[0] == ' ' or new_source[-1] == ' ': #check that source doesn't have whitespace at beginning or end
            print "Whitespace error (source): " + new_word
            error = True
        new_words.append([new_word,new_date,new_source]) # append the data to a new list

    if not error: 
        return new_words # return the data if there's no error
    else:
        return False
    
### Passive words, if already in the passive sheet, can be overwritten (the words stay there, but the sources are overwritten.)
### However, in the current implementation, this option is never used because passive words go straight to active. You'll only
### see passive words overwritten if you had to quit the program during passive sheet generation.    
def ask_overwrite():
    while True:
        overwrite = lower(raw_input("Overwrite previous sources and dates (y/n)? "))
        if overwrite in ['y','n']:
            break
    if overwrite == 'y':
        return True
    else:
        return False

### This function is a solution to updating the MySQL database word by word during passive sheet creating.
### As explained in some other function's description, this is much faster, since it limits the number of calls
### to the db. Each call is longer, but there are only three calls. Because we're skipping the passive list,
### the third command can be removed, though not independently of making other changes to the program.
def batch_add_active_words(to_add_active_words, to_delete_p_words, to_add_main_words, student_name, main_name, passive_name):
    if len(to_add_active_words) !=0: # words to add to the active database
        add_active_command = "INSERT INTO %s (word, data, lockvar) VALUES " % student_name
        for word, date, source in to_add_active_words:
            add_active_command += """(\"%s\", \"%s\", 'False'), """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str([[],[],[100.0],[],['active',date, source]])))
        add_active_command = add_active_command[:-2] + ';'
        
        do_command(add_active_command)

    if len(to_add_main_words) !=0: # words to add to the vocabmain list
        add_main_command = "INSERT INTO %s (word, data, lockvar) VALUES " % main_name
        for word, date, source in to_add_main_words:
            add_main_command += """(\"%s\", \"%s\", 'False'), """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str({})))
        add_main_command = add_main_command[:-2] + ';'
        
        do_command(add_main_command)

    if len(to_delete_p_words) !=0: # words to delete from the passive list (can be removed, see function note)
        delete_p_command = "DELETE FROM %s WHERE " % passive_name
        for word, date, source in to_delete_p_words:
            delete_p_command += """word = \"%s\" OR """ % MySQLdb.escape_string(word)
        delete_p_command = delete_p_command[:-3] + ';'
        
        do_command(delete_p_command)

    return

### Only used when words are directly loaded to the active sheet through the deprecated function.
def upload_to_sdb(student_name, main_name):
    passive_name = student_name+"passive" # name of student's passive dbase

    input_file_name = raw_input("Please enter the file name (without .csv; must be in same folder): ") ## asks for the upload file (word/date/source)
    input_file_name = input_file_name + '.csv'

    double_check = raw_input("Have you checked the file to remove adverbs, gerunds, etc.? (* to quit, Enter to continue)") ## standard warning
    if double_check == '*':
        return

    words = upload_csv_for_sdb(input_file_name) # turns file into list
    if words == False:
        return

    words = upload_to_sdb_checker(words) # checks list for formatting errors
    if words == False:
        print "Errors found. Exiting."
        return

    passive_words = get_words_list(passive_name) # gets all the relevant lists
    active_words = get_words_list(student_name)
    main_words = get_words_list(main_name)

    to_add_active_words = []
    to_delete_p_words = []
    to_add_main_words = []
    
    for word, date, source in words:
        if word in active_words: # if the word is already active, skip it
            print "Already an active word: " + word
        else:
            to_add_active_words.append((word, date, source)) # if not, add it to the active words, plus...
            if word in passive_words: # if there's a passive version, delete that passive version
                print "Passive verion deleted: " + word
                to_delete_p_words.append((word, date, source))
            if word not in main_words: # if there's no version in the main, add that
                to_add_main_words.append((word, date, source))

    # do all the changes in batch, not one-by-one
    batch_add_active_words(to_add_active_words, to_delete_p_words, to_add_main_words, student_name, main_name, passive_name)

    # log the activity
    add_to_log(student_name, input_file_name)

    print "Active upload complete."    
    return

### this function just adds all the passive words to the passive sheet, replacing any that are due to be overwritten
### It's connected only with the function below it.
def batch_add_passive_words(to_add_words, to_replace_words, passive_name):
    if len(to_add_words) !=0:
        add_command = "INSERT INTO %s (word, data, lockvar) VALUES " % passive_name
        for word, date, source in to_add_words:
            add_command += """(\"%s\", \"%s\", 'False'), """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str([date,source])))
        add_command = add_command[:-2] + ';'
        
        do_command(add_command)
    
    if len(to_replace_words) !=0:
        replace_command = "UPDATE %s SET data = CASE " % passive_name
        for word, date, source in to_replace_words:
            replace_command += """WHEN word = \"%s\" THEN \"%s\" """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str([date,source])))
        replace_command += "ELSE data END;"
        
        do_command(replace_command)
    
    return

### This function is still necessary. It is used in the one-shot upload process to add passive words from the
### _input_file_name. It also is used in the deprecated functions to just upload passive words
def upload_to_sdb_passive(student_name, main_name, _input_file_name = False, stats = False):

    passive_name = student_name+"passive" # name of student's passive db

    if not _input_file_name: # if there's no given file (which means you're using the deprecated function)
        input_file_name = raw_input("Please enter the file name (without .csv; must be in same folder): ") # get the file for upload
        input_file_name = input_file_name + '.csv'

        double_check = raw_input("Have you checked the file to remove adverbs, gerunds, etc.? (* to quit, Enter to continue)") # standard warning
        if double_check == '*':
            return False
        overwrite = ask_overwrite() # does the user want to overwrite older passive word duplicates?
    else:
        input_file_name = _input_file_name #
        overwrite = True # we always overwrite passive words in the one-shot solution, because the only reason they're ever
                         # in the passive sheet is if there was an error.
    
    raw_words = upload_csv_for_sdb(input_file_name) # get the data in list form
    if raw_words == False:
        print "Errors found. Exiting."
        return False

    raw_words = upload_to_sdb_checker(raw_words) # check the list form for errors; we should be able to skip this for the one-shot solution
    if raw_words == False:
        print "Errors found. Exiting."
        return False 

    active_words = get_words_list(student_name) # get words from the student's active and passive sheet
    passive_words = get_words_list(passive_name)
    # we don't need the vocabmain data yet because passive words are not added to the vocabmain until they become active

    to_add_words=[]
    to_replace_words=[]
    not_added_words=[]
    
    for word, date, source in raw_words:
        if word in active_words: # if the word is active, skip it
            print "Already an active word: " + word
            not_added_words.append(word) # we track not-added words only for the summary stats
        elif not overwrite and word in passive_words: # if the word is already passive, and we're not overwritting, skip it
            print "Already a passive word: " + word
            not_added_words.append(word)
        elif overwrite and word in passive_words: # if the word is already passive, but we're overwriting, then slate it for overwriting
            print "Overwritten previous version: " + word
            to_replace_words.append((word,date,source))
        else: # if the word is not passive, slate it for adding
            print "Passive word added: " + word
            to_add_words.append((word,date,source))

    if stats != False:
        # this pauses the process to give the user a chance to look at the summary stats; ostensibly to let them shorten
        # the assignment if there are too many words.
        stats_cont = print_summary_stats(stats, not_added_words)
        if not stats_cont:
            return False

    # adds all the passive words
    batch_add_passive_words(to_add_words, to_replace_words, passive_name)

    add_to_log(student_name, input_file_name) # logs the activity
    
    print "Passive upload complete."
    return _input_file_name # returns this info so that the file can then be deleted. 

###################################################################################
### DOWNLOAD FILL-IN ANSWER SHEET COMMANDS - THESE RARELY USED FUNCTIONS ARE FOR DOWNLOADING SHEETS THAT MAKE
### IN-ADVANCE ANSWER CREATION EASIER
# has_answers(dbase, word, q_type)
# csv_generator(q_type)
# add_to_generator_csv(writer, word, data)
# download_qless(q_type, dbase, main_name)
# download_all(q_type, dbase, main_name)
# download_answer_sheet(student_name)
###################################################################################

# checks if a word has any questions of a particular question type.
# (this could easily be replaced by a tweaked version of get_generator_data_from_dict; they're essentially the same function)
def has_answers(dbdict, word, q_type):
    if not dbdict.has_key(word):
        print "Not in main: " + word
        return True
    
    answers = dbdict[word]

    if answers=={}:
        return False
    else:
        for answer_key in answers:
            if answer_key[0] == q_type:
                return True
        return False

# makes the .csv file that will be filled with the words and questions, if any
def csv_generator(q_type):
    now = datetime.datetime.now()
    name = 'uploader-'+q_type+'-'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-('+str(now.hour)+'-'+str(now.minute)+').csv'
    writer = csv.writer(open(name, 'wb'), dialect = 'excel')
    
    return writer

# adds a word and any associated data to the .csv file
def add_to_generator_csv(writer, word, data):
    row = [word, '']
    if data == {}: # if there are no answers for the word, just add {}
        row.append(str(data))
    else: # if there are answers..
        for q in data: # attach each answer in a new column (here q is the answer number [m1,s1,etc.], and data[q] is the answer
            q_together = str(q) + ":" + str(data[q])# combine the answer number and the answer
            row.append(q_together) # add these two to their own column

    writer.writerow(row)
    return

### This function gets the relevant questions for a particular word
def get_generator_data_from_dict(main_dict, word, q_type):
    if not main_dict.has_key(word): # if the word is not in the main, that's a problem, but here we keep the word anyway; probably want to return an error
        print "Not in main: " + word
        return {}
    
    answers = main_dict[word] # get the questions we have for that word

    if answers=={}: # if there are no questions, return as much
        return answers
    else:
        _answers = {} # create a variable to store relevant questions
        for answer_key in answers: # go through each question
            if answer_key[0] == q_type: # if the question matches the question type we're looking for
                _answers[answer_key] = answers[answer_key] # add it to our storage varialbe
        return _answers # which we return at the end

### This function downloads only the words that don't have a particular type of question
### q_type is s or m, dbase is the one from which we'll get the words, and main_name is from where we'll get the answers
def download_qless(q_type, dbase, main_name):  
    writer = csv_generator(q_type) # make the csv that we'll fill

    words = get_words_list(dbase) # get the word subset we're considering
    main_dict = turn_dbase_into_dict(main_name) # get the words + answers set we're considering
    
    for word in words: # for every word from our word subset
        if not has_answers(main_dict, word, q_type): # if the word has no answer in the words + answers set
            add_to_generator_csv(writer, word, {}) # add the word to the csv

    return

### Same as above, only this time it includes words that have questions
def download_all(q_type, dbase, main_name):
    writer = csv_generator(q_type)

    words = get_words_list(dbase)
    main_dict = turn_dbase_into_dict(main_name)
    
    for word in words:
        data = get_generator_data_from_dict(main_dict, word, q_type)
        add_to_generator_csv(writer, word, data) # adds the word with any and all answer data to the csv

    return
    
# one minor note when you're looking over this set of functions, I used the words question and answer interchangeably
# They both mean "answer option", i.e., the m1, m2, s1, etc. for a particular word
def download_answer_sheet(student_name, main_name):    
    while (True): # Asks what type of questions you want to make
        q_type = raw_input("Enter either m (matching word) or s (sentence completion): ")
        if q_type in ["m","s"]:
            break
    
    while True: # Gives a few options for what type of sheet to make
        print ""
        print "Select an option. (* to quit)"
        print "1. All words without questions."                                     # All words without that type of question
        print "2. All words."                                                       # All words, regardless of how many questions they have
        print "3. All words in " + student_name + "'s list without questions."      # Same as 1, but only words that a particular student has
        print "4. All words in " + student_name + "'s list."                        # Same as 2, but only words that a particular student has
        option = raw_input(">>")
        if option == '*':
            return
        if not(option in ['1','2','3','4']): # reject invalid selections
            print "Invalid selection. Enter just the number of the option you want."
        else:
            break

    if option=='1':
        download_qless(q_type, main_name, main_name)
    if option=='2':
        download_all(q_type, main_name, main_name)
    if option=='3':
        download_qless(q_type, student_name, main_name)
    if option=='4':
        download_all(q_type, student_name, main_name)

    print "Answer upload sheet created."
    return

###################################################################################
### UPLOAD NEW ANSWER SHEET COMMANDS - THESE FUNCTIONS UPLOAD THE SHEETS THAT WERE CREATED IN THE PREVIOUS SET OF FUNCTIONS
### AFTER THE USER IS FINISHED ADDING THE NEW ANSWERS
# get_upload_csv()
# check_if_word_exists_in_db(word, dbase)
# clean_words(data, main_name, q_type)
# get_data_for_upload(main_name)
# check_for_changes(word, data, dbase, q_type)
# add_new_data(word, new_q, dbase, q_type)
# upload_answer_sheet(main_name)
###################################################################################

# This function lets the user pick which file with new answers they want to upload
def get_upload_csv():
    files = os.listdir(os.getcwd()) # gets all the files that are in the directory
    
    counter = 1
    v_files = []
    for f in files: # looks through each file
        if f[:9] =='uploader-' and f[-4:] == ".csv": # if the file name matches the uploader file template...
            print str(counter) + ". " + f # display it in a list
            counter += 1
            v_files.append(f) # and add it to a list

    if len(v_files)==0: # if there are no files with a name that matches the template
        print "No acceptable files."
        return False, False
        
    while True: # lets the user pick a file, based on the number from the list created above
        csv_name = raw_input('Enter the number of the file you wish to upload or * to quit. ')
        if csv_name == '*': # quits
            return False, False
        if int(csv_name) in range(1,len(v_files)+1): # checks that the number is in the correct range
            csv_name = v_files[int(csv_name)-1] # gets the filename value
            break

    q_type = csv_name[9] # retreives what type of questions we're uploading in this file
    if q_type not in ['m','s']: # double checks that it's either a matching or sentence completion; this should never be a problem, but we check anyway
        print "Invalid question type in file name."
        return False, False
    
    return csv_name, q_type

# this function looks through all the uploaded answers to see if there are any typographic or other obvious errors
# data = data from the csv, main_dict = the dict object version of mainvocab and q_type = m or s
def clean_words(data, main_dict, q_type):
    words = {} # this dict object collects all of the words and their defintions (new and old)
    error = False # this is for errors in the firt two columns 
    answer_error_holder = False # this is for errors in the last two columns
    for row in data: # goes through each row of data
        if len(row[0]) == 0 or len(row[1]) == 0: # if the word row or (more likely) the answer row are nil (i.e., no new answer was entered, skip it)
            continue
        if not main_dict.has_key(row[0]): # if the word in the list is not in the vocabmain (shouldn't happen)
            print "Not in main vocab: " + row[0] 
            error = True
            continue
        for letter in row[1]: # checks the answer column for any foreign letters
            if letter in foreign_letters:
                print "Foreign letter error (new answer): " + word
                error = True
        if q_type=='s': # makes sure that the --- is present in new sentence completion answers
            if '---' not in row[1]:
                print "You forgot the --- for: " + row[0]
                error = True
                continue
        if row[0][0] == ' ' or row[0][-1] == ' ' or row[1][0] == ' ' or row[1][-1] == ' ': # checks for whitespace at beginning or end of word or new answer
            print "Whitespace error for: " + row[0]
            error = True
            continue
        word = row.pop(0) # if we didn't hit any error, take the word from the row
        new_a = row.pop(0) # and the new answer
        words[word] = {'new':new_a} # and add these two to the words dict object
        answer_error = False 
        for _answer in row: # now we're going to check all the pre-existing answers (one-by-one) for that word that were included in the uploader sheet (columns 3 and onwards in the csv)
            if _answer=='{}': # if there's nothing, keep going
                continue
            if len(_answer)==0: # another nothing; this happens in empty overhung cells (i.e., if the longest row has 5 columns, a row with three columns would be 'word', 'answer','{}','','')
                continue
            else:
                try: # if we're here, it means there are pre-existing answers, so we're going to check that they're properly formatted
                    place_holder = _answer.index(':') # this finds the ':' symbol, which seperates key from answer
                    key = _answer[:place_holder] # everything before the : is the key
                    answer = _answer[place_holder+1:] # everything after is the answer
                except (ValueError, IndexError): # if you get this error, it means the ':' symbol is missing from that answer entry, which means something has been fucked up
                    answer_error = True # the reason for two error booleans is that this one resets every word/row
                    answer_error_holder = True # while this one stays true until the end, so that we know to exit the program
                    break
                if words[word].has_key(key): # if you get this error, that means you have the same key for different answers, which should never happen
                    answer_error = True
                    answer_error_holder = True
                    break
                words[word][key]=answer # if no errors, add that key and answer to the word's data

        if answer_error: # if we have an error in the answers, get rid of that word and notify the user
            del words[word]
            print "Answers error for: " + word
            continue

    if error or answer_error_holder: # save quitting due to errors until the end, so you see all the errors
        return False
    else:
        return words # if no errors, return your list of words. this data should include all words that have new answers, along with all of their past answers and the new answer
        
# just a higher level function that finds which file the user wants to upload, checks that there are no errors in the file
# and returns the relevant data.
def get_data_for_upload(main_dict):
    csv_name, q_type = get_upload_csv() # gets the csv
    if not csv_name:    
        return False, False

    # the below converts the csv data into a list object
    _words = [] 
    reader = csv.reader(open(csv_name, "rb"))
    for row in reader:
        _words.append(row)

    # checks that there is at least one word in the data
    if len(_words) == 0:
        print "No words at all, exiting."
        return False, False

    # runs the words through the cleaning function
    words = clean_words(_words, main_dict, q_type)

    # if there are errors, quit
    if words == False:
        print "Errors found, exiting."
        return False, False

    # if there are no words left after the cleaning function, quit
    if len(_words) == 0:
        print "No editted, acceptable words; exiting."
        return False, False

    return words, q_type

# The point of this function is to check if the data for a word in the vocabmain database has changed in the time between
# when the uploader file was created and when it was finally uploaded. This is there to prevent any accidental duplication
# (i.e. if you create an uploader and enter "go" as an answer for "walk", but someone else in the meantime has created that
# same answer, this would recognize that changes had been made).
# The function returns True for there are changes and False if there are none
# word = the word, data = the data for the word FROM THE UPLOADER FILE, ddict = the dictionary object that represents the
# CURRENT vocabmain, q_type = m or s
def check_for_changes(word, data, ddict, q_type): 
    if not ddict.has_key(word): # this checks that the word is actually in the vocabmain database
        print "Not in main: " + word
        return True
    else:
        # the next four lines create a dictionary object that contains all the questions of q_type, indexed by word.
        # check_for_changes should return False iff the data for a word in the answers dict is the same as the questions
        # added in the 3rd column and onwards in the uploader file
        answers = {}
        for key in ddict[word]:
            if key[0] == q_type:
                answers[key] = ddict[word][key]
        if len(data)-1 != len(answers): # if the data minus the new answer is not the same length as the old answers, we know something new has been addedin the meanwhile
            print "1. Pre-edited: " + word
            return True
        if len(data)==1 and len(answers)==0: # this is the case where there were no answers, and there still are none
            return False
        # now we're going to check each answer in the current vocabmain to make sure it lines up with each non-new answer from
        # the uploader file. this should never technically be necessary, since it will only catch times when an answer
        # has been editted in the vocabmain, or something else weird like that, but just in case...
        for key in data: # go through each key in the data from the uploader
            if key == 'new': # skip the new one
                continue
            else:
                try:
                    test = answers[key]
                    if test == data[key]: # make sure the key entries in the two dictionaries match up
                        continue
                    else:
                        print "2. Pre-edited: " + word # if they're not equal, that's a problem
                        return True
                except KeyError: # and if the key doesn't exist in the old answers, that's also a problem
                    print "3. Pre-edited: " + word
                    return True

        return False

# this function actually adds the new question into the vocabmain database
# word = the word, new_q = the new question, dbase = the dbase where we'll upload the new data (vocabmain), ddict = a dictionary version of the main vocab list, and q_type = m or s
def add_new_data(word, new_q, dbase, ddict, q_type):
    if not ddict.has_key(word): # if for whatever reason the main vocab list doesn't have the word, skip it; should never happen 
        print "Not in main, not being added: " + word
        return
    answers = ddict[word] # get all the existing answers for that word
    if answers=={}: # if there are no answers..
        key = q_type + '1' # ..set the key for the new answer to m1 or s1
        answers={key:new_q} # and set the answers for that word equal to the new answer
    else:
        counter = 1 # if there is at least one answer, make a counter to count the number of answers there are
        for answer_key in answers: # go through each answer
            if answer_key[0] == q_type: # check if the answer matches the answer type 
                counter+=1 # and increment the counter if it does
        key = q_type + str(counter) # assign the key for the new answer according the key
        answers[key]=new_q # add the new key:answer to the existing answers

    # add the updated words to the database - this has not yet been made into a batch adder, and so is slow, because we just don't use this much anymore
    do_command("""UPDATE %s SET data = \"%s\" WHERE word = \"%s\"""" % (dbase,MySQLdb.escape_string(str(answers)),MySQLdb.escape_string(word)))

    return

# this is the main function to handle uploading the .csv files that have been updated with new questions
def upload_answer_sheet(main_name):
    main_dict = turn_dbase_into_dict(main_name) # gets the main word list
    
    data, q_type = get_data_for_upload(main_dict) # gets the data for the upload
    if not data:
        return
    
    edited_words = []
    
    for word in data: # goes through each word in the data
        if check_for_changes(word, data[word], main_dict, q_type): # checks if any words have had questiosn added to then since the uploader file was downloaded
            print "Skipped: " + word # skips any words with questions added
            edited_words.append(word) # keeps track of skipped words for later
            continue
        else:
            print "Edited: " + word # otherwise, sends the words with the new data to be updated
            add_new_data(word, data[word]['new'], main_name, main_dict, q_type)

    if len(edited_words)!=0: # if there are words that had to be skipped, it makes a new uploader csv with those words
        writer = csv_generator(q_type) # note that this and two of the functions below are actually for the previous section of functions
        counter = 0
        for word in edited_words:
            data = get_generator_data_from_dict(main_dict, word, q_type)
            add_to_generator_csv(writer, word, data)
            counter+=1

        print str(counter) + " words had already been edited, new csv created."
    else:
        "Words uploaded, no further edits necessary."

    return

###################################################################################
### GENERATE ACTIVE(TESTING)/PASSIVE SHEET COMMANDS
### THESE COMMANDS ARE THERE FOR CREATING THE CSV FILES THAT ARE USED TO PICK WHAT WORDS TO PUT INTO AN ACTIVE OR A
### PASSIVE ASSIGNMENT. THE PASSIVE ASSIGNMENT GENERATION IS NOW NEVER USED INDEPENDENTLY.
# test_csv_generator(student_name)
# get_sdata_for_test(student_name, word)
# get_wdata_for_test(word, s_data, main_name, max_untested_counter)
# write_test_gen(writer, data, counter)
# generate_testing_sheet(student_name, main_name)
# passive_csv_generator(student_name)
# get_pdata_for_test(passivedb, word)
# generate_passive_sheet(student_name, main_name)
###################################################################################

# This function creates the csv for making an active assignment 
def test_csv_generator(student_name):
    now = datetime.datetime.now() # we use the current timestamp to distinguish between files; technically, this isn't great because two sheets made within the same minute will conflict. in that case I think an overwrite happens, though not sure. unlikely
    name = 'testsheet-'+upper(student_name)+'-'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-('+str(now.hour)+'-'+str(now.minute)+').csv'
    writer = csv.writer(open(name, 'wb'), dialect = 'excel')

    # adds activity to the log file
    add_to_log(student_name, name)

    # returns a pointer to the file
    return writer
    
# this function takes the dictionary version of the student database and the word, and retrieves, organizes and returns the
# student word data in a way that that will make creating the csv easier 
def get_sdata_for_test(student_dict, word):
    if not student_dict.has_key(word): # double-checks that the word is in the student dictionary
        print "Not in main: " + word
        return 'Error'
    
    data = student_dict[word] # get the data for the particular word
    total_tested, total_wrong, days_since = 0,0,0 # create a few variables

    if '^^^out^^^' in data[0]: # checks if the marker for a word that is currently being tested is there or not
        _out = True
    else:
        _out = False
    
    if len(data[1]) != 0: # if the word has been tested earlier
        for result in data[1]: # go through each tested result (these will be 1 if right, 0 if wrong)
            total_wrong += int(result) # add each result to total wrong (see two lines down)
            total_tested += 1 # add one each time you have a result to the count of number of times the word has been tested
        total_wrong = total_tested - total_wrong # calculate the actual number wrong
        
    if len(data[3]) != 0: # if the word has been tested before
        days_since = ( date.today() - data[3][-1] ).days # subtract from today's date the most recent tested date
    else:
        days_since = ( date.today() - data[4][1]  ).days # otherwise, subtract from today's date the day the word was added

    # return an arranged version of the data
    return [data[0],total_tested, total_wrong, days_since, data[2][0], str(data[4][2]), _out]

# this function retrieves, organizes and returns the answer data for a word (i.e. the possible answers)
# it also ends up keeping track of the largest number of untested answers that any of the words has
# word = word, s_data = the keys of the questions the student has already seen, main_dict = the vocabmain in dictionary form,
# max_untested_counter = the highest number of untested answers for one word in the student's list 
def get_wdata_for_test(word, s_data, main_dict, max_untested_counter):
    # if for whatever reason the main_dict doesn't have a word, that's a paddlin'
    if not main_dict.has_key(word):
        print "Not in main: " + word
        return 'Error', max_untested_counter

    counter = 0 # this counter tracks the number of untested answers
    data = main_dict[word] # get all the answers for the word
    for question in data: # for each answer...
        if question in s_data: # if the student has seen the question
            data[question] = '***' + data[question] # append a little code onto it to distinguish it later when we make the csv
        else:
            counter +=1 # otherwise, increment the counter

    return data, max(counter, max_untested_counter) # return the answer data for the word (now with *** appended to already seen questions), and also the larger of the two untested counters (either the one passed into the function from before, or the one from the current word)

# This function does all the nitty-gritty of sticking the information into the testsheet file
# writer = the csv file, data = what we're putting in, counter = the maximum number of untested questions for a single word
# data is structured like this: [word,[times tested, times wrong, days since entry/last test, score, source, is the word currently out?], {answer data}]
def write_test_gen(writer, data, counter):
    # q_counter is a little Excel script that we stick in the first row to count how many questions have been chosen
    q_counter = """="Qs Chosen: "&COUNTIF(E2:E50000,"<>")-COUNTIF(E2:E50000,"***needs new***")-COUNTIF(E2:E50000,"d")"""

    # the first five columns in the first row
    row = ['WORD', 'TIMES TESTED', 'TIMES WRONG', 'DAYS SINCE (SOURCE)', q_counter]

    # then it becomes a little trickier, because we want to separate questions that the student has been tested on
    # and those they have not been tested on into seperate sections, with a divider in between. to do this, we have to
    # know how many columns we need to set aside for the first section, so that the divider can be a single column.
    # Since untested questions come first, we need to figure out, among the words, which one has the largest number
    # of untested questions (this is the counter), and then create that many columns before inserting the divider. 
    if counter != 0: # if the counter = 0, we don't need an untested column
        row.append('UNTESTED') # otherwise, first add the section title
        _counter = counter-1 # subtract from the counter (and make a seperate variable so we hold onto the original value)
        while _counter>0: # if it's still above 0, and while it is above 0
            row.append('') # keep adding columns
            _counter-=1 # and subtracting from the _counter
    row.append('***') # then add the divider line
    row.append('TESTED') # then add the column heading for the last section, the untested questions
    writer.writerow(row) # add the header row

    # this is where we sort the words. each successive sort is applied to the one before, so the last one is most obvious
    data = sorted(data, key = lambda thing: thing[1][4], reverse=False) # first, sort by the source of word, in alphabetical order
    data = sorted(data, key = lambda thing: thing[1][2], reverse=True)  # then sort by how many days ago it was added, longest ago at the top 
    data = sorted(data, key = lambda thing: thing[1][3], reverse=True)  # finally by the word's score (a function of how many times they got it right or wrong (see grader intake functions for precise description), highest score at the top

    for datum in data: # go through each word (in the sorted order)
        word = datum[0] # the word
        s_data = datum[1] # the student data about the word
        s_data[2] = str(s_data[2]) + ' (' + s_data[4] + ')' # dates since last test + (source)
        if s_data[5]: # is the word currently out on a quiz that hasn't been graded yet?
            s_data[0] = str(s_data[0]) + '^' # if it is, add a like carat marker before the word
        w_data = datum[2] # the answer data for word
        _counter = counter # another duplicate of the counter, which we'll use for this word
        
        if w_data == {}: # if the word has no possible answers
            row = [word, s_data[0], s_data[1], s_data[2], '***needs new***'] # we stick in a little ***needs new*** in the answer selection box so the user knows they have to enter something new
            while _counter>0: # then we enter blank rows until we hit the end of the counter
                row.append('')
                _counter-=1 
            row.append('***') # then we append the divider column
            
        else:
            row = [word, s_data[0], s_data[1], s_data[2], ''] # otherwise, the answer box is empty

            _w_data = [] # the w_data is in dictionary form, but we want it in list for so we can iteration through it
            for k in w_data:
                _w_data.append(str(k)) # here, we make a list only of the keys of the w_data dictionary
            _w_data.sort() # the sort the keys alphabetically
                
            for question in _w_data: # then we go through each key
                if question[0]=='s': # first we skip the sentence completions
                    continue
                if w_data[question][:3]=='***': # and we skip any questions that have already been tested (note that we're using the key from _w_data to pull out the entry from w_data)
                    continue
                else:
                    try:
                        row.append(str(question)+" : " + str(w_data[question])) # if we haven't skipped it, stringify it and stick it in
                        _counter-=1 # and decrement the counter
                    except UnicodeEncodeError: # this error occurs if the answer for some reason is not a proper string
                        print 'uni error: ' + str(row[0])
            for question in _w_data: # repeat for all the previously untested sentence completions
                if question[0]=='m':
                    continue
                if w_data[question][:3]=='***':
                    continue
                else:
                    row.append(str(question)+" : " + str(w_data[question]))
                    _counter-=1

            while _counter>0: # if there's extra space left over, attach some blank rows
                row.append('')
                _counter-=1

            row.append('***') # attach the divider row
                    
            for question in _w_data: # now we're going to do the same thing, except that we'll skip untested questions...
                if question[0]=='s':
                    continue
                if w_data[question][:3]!='***': # note the != rather than the == here. it's the only difference
                    continue
                else:
                    row.append(str(question)+" : " + str(w_data[question][3:]))
            for question in _w_data: # again for sentence completions
                if question[0]=='m':
                    continue
                if w_data[question][:3]!='***':
                    continue
                else:
                    row.append(str(question)+" : " + str(w_data[question][3:]))
                
        writer.writerow(row) # write the whole row into the csv file, move onto the next word
    return

# This function is to get rid of "old words". The reasoning behind this is that any words that have not been tested within
# some number of days of being seen by the student should be deleted, because the student has probably forgotten them by then.
# The only times this is a bit of a pain is when you create a longer passive assignment (one for several weeks at a time)
# for convenience, only to have to the set deleted before you finish actually assigning it. In this case, you need to
# re-assign a passive assignment that covers the deleted words.
# s_name = the student's name, sdict = a dictionary object of the student database
def delete_old_words(s_name, sdict):
    forget_limit = 30 #### number of days after which we delete a never-tested word
    new_sdict = {} # this will be the dictionary object of the student database without the deleted words
    to_delete = [] # a list of words to delete
    for word in sdict: # go through each word in the student database
        data = sdict[word] # get the word's data
        if data[0] == []: # if the word has never been tested and is not currently in a quiz
            if data[4][0] == 'active': # get the date the word was assigned (depends on if it was once a passive word or not; this distinction is now irrelevent though)
                date_assigned = data[4][1]
            else:
                date_assigned = data[4][0]
            difference = datetime.date.today() - date_assigned # figure out how long ago it was added
            if difference.days > forget_limit: # if the difference is greater
                to_delete.append(word) # slate the word for deletion
            else:
                new_sdict[word] = data # otherwise put it in the new_sdict
        else: # if the word has been tested before or is currently out, put it back in the new_sdict 
            new_sdict[word] = data

    # this is a batch command to delete all the words at once from the student's database (in mysql)
    if len(to_delete) !=0: # (if there are words to delete)
        delete_command = "DELETE FROM %s WHERE " % s_name
        for word in to_delete:
            delete_command += """word = \"%s\" OR """ % MySQLdb.escape_string(word)
        delete_command = delete_command[:-3] + ';'
        
        do_command(delete_command)

    return new_sdict

# this function is the higher-level function that goes through all the steps to create a testing sheet.
# the only variables it takes are the student name and the vocabmain name
def generate_testing_sheet(student_name, main_name):
    main_dict = turn_dbase_into_dict(main_name) # gets the two databases as dictionaries
    student_dict = turn_dbase_into_dict(student_name)

    student_dict = delete_old_words(student_name, student_dict) # deletes the old words
    
    max_untested_counter = 0 # this is for keeping track of the highest number of untested answers any of the words has
    
    words = get_words_list(student_name) # gets the words from the student file

    writer = test_csv_generator(student_name) # creates the csv 
    
    data = [] # the variable for the data

    for word in words: # go through each word and get all the necessary data
        s_data = get_sdata_for_test(student_dict, word) # the data from the student database
        if s_data == 'Error':
            continue
        w_data, max_untested_counter = get_wdata_for_test(word, s_data[0], main_dict, max_untested_counter) # the data from the vocabmain database
        if w_data == 'Error':
            continue
        data.append([word, s_data[1:], w_data]) # append all data to one big list

    write_test_gen(writer, data, max_untested_counter) # make the testsheet

    print "Test sheet created."

# this functions creates the csv sheet for picking what words go into the passive assignment
def passive_csv_generator(student_name):
    now = datetime.datetime.now()
    # distinguishes sheets by date - see note in active sheet csv generator above
    name = 'passive-'+upper(student_name)+'-'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-('+str(now.hour)+'-'+str(now.minute)+').csv'
    writer = csv.writer(open(name, 'wb'), dialect = 'excel')

    # logs this
    add_to_log(student_name, name)
    
    return writer, name # note that the function returns the file name as well, unlike the active sheet version

# this function retrieves the relevant data for a particular word from the student's passive database, organizes it and returns it
def get_pdata_for_test(passive_dict, word):
    if not passive_dict.has_key(word): # if the the word isn't in the passive database, that's a paddlin'
        print "Not in passive: " + word
        return False, False, False
    
    data = passive_dict[word] # get the data from the passive database dictionary object

    source = data[1] # the source of the word

    days_since = ( date.today() - data[0] ).days # the number of days since the word was added

    return source, days_since, data[0] # return the source, days since, and the day the passive word was added

# this is the top level function that makes the passive csv sheet. we essentially don't use this independently of the
# all-in-one passive to active function. when we use it as part of this function, the function passes a list of
# "pre-selected words". basically, we skip the passive sheet step by making a passive sheet but selecting the words
# automatically, so that we can go to the upload step without needing input from the user. this is obviously inefficient,
# but was easier to make at the time. future versions should re-make the all-in-one function from scratch.
def generate_passive_sheet(student_name, main_name, pre_selected_words = []): 
    passive_name = student_name+'passive'

    # gets the words from the passive list
    words = get_words_list(passive_name)

    # turns the passive db into a passive dictionary
    passive_dict = turn_dbase_into_dict(passive_name)

    # gets the pointer to the csv file and file name
    writer, _writer_name = passive_csv_generator(student_name)

    q_counter="""="Choices (x): "&COUNTIF(B2:B50000,"x")""" # a little excel script that counts how many words you've chosen
    row = ['WORD', q_counter, 'DAYS SINCE ADDED', 'SOURCE', 'DATE ADDED'] # the header row
    writer.writerow(row)

    # note that there's no sorting of the words; in theory, there should be. as is I think you get the words in the order they were added, which is not a terrible option
    for word in words: # goes through each word 
        source, days_since, date = get_pdata_for_test(passive_dict, word) # gets the relevant data for each word
        if source == False: # checks for an error
            continue
        if word in pre_selected_words: # if the word has been pre-selected (in the all-in-one function), then add the row with an 'x' already in the selection cell
            row = [word, 'x', days_since, source, str(date)]
        else: # otherwise, keep that cell blank
            row = [word, '', days_since, source, str(date)]
        writer.writerow(row)

    print "Passive sheet created."

    if pre_selected_words != []: # if you're in the all-in-one function, you'll need the csv filename (so you can immediately turn around and upload that file)
        return _writer_name
    else: # otherwise, you don't (because the user has to first select the words, and only then can you upload the file)
        return

###################################################################################
### GENERATE ACTIVE/PASSIVE EXAM COMMANDS
# open_file ( name )
# make_test(t_database, test_type, student_name, due_date, dummies, submit_to, test_number)
# generate_passive_assignement(words_plus_source, student_name, test_number, assign_date, teach_id)
# ask_q_type()
# ask_test_details()
# get_test_number(q_type, dbase)
# upload_test_file(student_name)
# parse_reader(reader)
# clean_test_file(data, q_type)
# check_new_q(q)
# add_new_data(word, new_q, dbase, q_type)
# get_question_key(word, key, dbase, q_type)
# open_grading_file(filename)
# make_grading_file(data, order, filename, assign_date)
# intake_testing_sheet(student_name, main_name)
# ask_passive_details()
# upload_passive_file(student_name)
# parse_passive_file(reader)
# clean_passive_file(data)
# get_ptest_number(dbase)
# add_passive_to_active(dbase, word, source, date)
# add_to_main(dbase, word)
# delete_from_passive(dbase, word)
# intake_passive_sheet(student_name, main_name)
###################################################################################

# don't remember why this is a seperate function, it just makes the .rtf file. I think it came this way in the PyRTF sample and I was too afraid to touch it.
def open_file ( name ) :
    return file( '%s.rtf' % name, 'w' )

# this is the huge function that creates the actual .rtf document that is the test, plus the answer sheet. We use the PyRTF
# module, which is not a module that comes standard with Python. In fact, it would have probably been easier to use make
# a .pdf using the module we used in custom exams, but I learned that one after I had already started with this.
# this (and the passive sheet creator right after) will definitely be the hardest section for me to explain and for you to
# understand. Documentation is minimal on PyRTF, so a lot code here is more the product of trial and error than any kind
# of logical process (well, moreso than the rest of the program, at least). Look through the PyRTF examples and included
# documentation if you hope to make any changes to this.
def make_test(t_database, test_type, student_name, due_date, dummies, submit_to, test_number, filename):
    # this sets up the basic necessities for a PyRTF document
    DR = Renderer()
    doc     = Document()
    ss      = doc.StyleSheet
    paper   = Paper( 'A4', 9, 'A4 210 x 297 mm' , 11907, 16838 )
    section = Section(paper)
    doc.Sections.append( section )

    # sets the font and creates a paragraph    
    tps = TextPS(font=ss.Fonts.TimesNewRoman, size=18)
    ps = ParagraphPS(alignment = TabPS.RIGHT)
    p1 = Paragraph( ss.ParagraphStyles.Normal, ps)

    # this creates the header, including a smaller font upper-right hand corner with name/date/adviser, and the test name and number centered below that
    student_full_name = get_student_fullname(student_name)
    p1.append(Text(str(student_full_name), tps))
    section.append( p1 )
    p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
    p1.append(Text("Due: " + str(due_date), tps))
    section.append( p1 )
    p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
    p1.append(Text("Adviser: " + str(submit_to), tps))
    section.append( p1 )
    section.append(Paragraph(Text('',tps)))
    tps = TextPS( bold=1, font=ss.Fonts.TimesNewRoman, size=20)
    ps = ParagraphPS(alignment = TabPS.CENTER)
    if test_number[0] == 'M':
        p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('Vocabulary Matching Quiz # ' + str(test_number[1:]), tps))
        section.append( p1 )
    elif test_number[0] == 'S':
        p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('Vocabulary Sentence Completion Quiz # ' + str(test_number[1:]), tps))
        section.append( p1 )
    elif test_number[0] == 'D':
        p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('Vocabulary Definitions Quiz # ' + str(test_number[1:]), tps))
        section.append( p1 )
    elif test_number[0] == 'W':
        p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('Vocabulary Writing Quiz # ' + str(test_number[1:]), tps))
        section.append( p1 )
        
        ps = ParagraphPS(alignment = TabPS.LEFT) # here, for the writing test, we have a special set of instructions that we add
        tps = TextPS(font=ss.Fonts.TimesNewRoman, size=20)
        
        p1 =  Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('Write a sentence using each of the words below. The sentence should reflect the meaning of the word (if the word is replaced in the sentence with a _____, your adviser should be able to guess which word you intended to put in the _____).', tps))
        section.append( p1 )
        p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('For every word, write down in parentheses which part of speech the word in your sentence is (noun, verb, adj., adv., etc.)', tps))
        section.append( p1 )
        p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('Sample:', tps))
        section.append( p1 )
        p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
        p1.append(Text('run (noun) I went on a run this morning, but my legs became tired very quickly.', tps))
        section.append( p1 )
        section.append(Paragraph(Text('',tps)))

    # now that we made the header, we can get on with adding the questions
    order = [] # this variable is quite important. it will hold for us the order of the questions, so that when we make the grader sheet, we can keep the order in the grader the same

    # the font style for the questions
    qps = TextPS(font=ss.Fonts.TimesNewRoman, size=20)

    # for the matching exam. look at the general structure of the matching exams so you know what the program is building,
    # that should help you make sense of the code
    if test_type == 'm':
        letter_iter = ['','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'] # the answers have letters associated with them
        number_iter = 1 # question numbers
        page = 'first' # the first page is different from the other ones, so we need to keep track of where we are
        
        answer_sheet = [] # we'll use this for keeping track of answers for the answer sheet
        questions = [] # we'll seperate questions and answers into their own lists (you'll see why later)
        answers = []
        q_a = [] # and this list has both questions and answers together
        for question in t_database: # t_database is a dict, which means it can't be sorted, so we turn it into a list in this form [[question, answer],[q,a],...]
            q_a.append([question, t_database[question]])
        shuffle(q_a) # then we shuffle the q_a list so that the question order is random
        for qa in q_a:
            questions.append(qa[0]) # then we create additional seperate lists for just questions and just answers
            answers.append(qa[1])

        order = copy.copy(questions) # the questions are in the order that they will be in the test, so we can copy that order for using later in the crader

        page_number = 1 # iterator for the page number
        while len(questions) != 0: # the loop for adding more pages of questions keeps going until we've added all the questions
            if page == 'other': # this section creates the header and the table for the quiz; the header depends on if it's the first page or not, so that's why we have this if else setup
                p1 = Paragraph(ss.ParagraphStyles.Normal, ParagraphPS().SetPageBreakBefore( True ))
                section.append(p1)
                p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
                p1.append(Text("Section: " + str(page_number), qps)) # we call each page its own section
                page_number += 1 # increment the page number
                section.append( p1 )
                section.append(Paragraph(Text('',qps)))
                table = Table( TabPS.DEFAULT_WIDTH * 3, TabPS.DEFAULT_WIDTH * 4, TabPS.DEFAULT_WIDTH * 5)
                table.SetAlignment(3)
            else:
                p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
                p1.append(Text("Section: " + str(page_number), qps))
                page_number += 1
                section.append( p1 )
                section.append(Paragraph(Text('',qps)))
                table = Table( TabPS.DEFAULT_WIDTH * 3, TabPS.DEFAULT_WIDTH * 4, TabPS.DEFAULT_WIDTH * 5)
                table.SetAlignment(3)
                page = 'other' # this was the first page, so subsequent pages won't be

            # here things become a tad complicated, because we want the program to do several things. we already have the
            # order for the questions; that's good. the answers can't have an order - we want to shuffle them so that they
            # don't line up with the question. at the same time, we only want to shuffle them within the group of 15
            # that will appear on that particular section. But, after you've shuffled the answers, you want to note their
            # letter, because that letter will go in the blank for the answers. This is important because if you want to
            # make an answer sheet, you need to know the order that the letters should be listed in.
            q_15 = questions[:15] # first we take the first fifteen questions
            a_15 = answers[:15] # and the first fifteen answers
            _a_15 = copy.deepcopy(a_15) # then we make an independent copy of the answers
            shuffle(_a_15) # and we shuffle this copy (this gives us the shuffled 15 answers for this section)
            __a_15 = [] # and we make a third temp variable, which will have the answers combined with their letter

            num = 1 # we'll use this for counting what question number we're on
            _answer_sheet = [] # we'll use this to hold the data that goes into making the answer sheet
            for ans in _a_15:
                # first we match the answer with the letter (the first ans with a, the second with b, etc.)
                letter = letter_iter[num]
                
                # next, we look up the location, in the a_15 list, of the ans. in other words, remember that q_15 and a_15
                # match up (the first answer is the answer for the first questoin), whereas _a_15 is randomized, but we can
                # look up where a particular answer in _a_15 would be if it were in a_15. another way of putting this is that
                # place keep is the question number for the word that ans is the answer to.
                place_keep = a_15.index(ans)+1 

                __a_15.append(letter_iter[num] + '. ' + ans) # we combine the letter with the answer and append it to __a_15 (this is how they'll apear in the quiz)
                num += 1 # we increment our 1-15 counter by 1
                _answer_sheet.append([place_keep, letter]) # and we append the place_keep (which we'll use for sorting) and the letter of the answer to the list we'll use for making the answer sheet

            answer_sheet.append([page_number-1, _answer_sheet]) # finally, we add the full answer sheet for that page, along with the page number

            num = 1 # we'll start the question counting back to one
            for que, ans in map(None, q_15, __a_15): # go through the questions and the shuffled letters + answers list that we made above
                p1 = Paragraph(ss.ParagraphStyles.Normal) # the text for the left cell
                p2 = Paragraph(ss.ParagraphStyles.Normal) # the text for the middle cell
                p3 = Paragraph(ss.ParagraphStyles.Normal) # the text for the last cell
                p1.append(Text(str(num)+'. ', qps)) # the question number
                p1.append(Text(str(que), qps))  # the word
                c1 = Cell(p1) # first cell
                p2.append(Text('____________',qps)) # space for the answer
                c2 = Cell(p2) # second cell
                p3.append(Text(str(ans),qps)) # the answer (note this isn't the answer for the word on the left, just whichever answer was matched up with the word)
                c3 = Cell(p3) # third cell
                table.AddRow(c1,c2,c3) # add the row to the table
                c1 = Cell(Text('',qps))
                c2 = Cell(Text('',qps)) # add an extra row of cells
                c3 = Cell(Text('',qps))
                table.AddRow(c1,c2,c3) # add the extra cells
                num += 1 # increment the question number
                questions.pop(0) # this and the below removes a question and answer from the list, so that next time we do q_15 = questions[:15] we have a new set of questions
                answers.pop(0)

            section.append(table) # add the table for this section

        ### Once we've used up all the questions and answers, we move onto the next step for the matching quiz, which is
        ### to generate the answer sheet.
            
        p1 = Paragraph(ss.ParagraphStyles.Normal, ParagraphPS().SetPageBreakBefore( True )) # add a page break
        section.append(p1)
        section.append(Paragraph(Text('Answer Key ' + str(student_name) + ' ' + str(test_number),qps))) # the header
        section.append(Paragraph(Text('',qps)))

        # take a look at some of the answer sheets. you'll see that it's three columns of answers in a row, each column
        # comprised actually of two rows (the section number and the answers). first, we're going to need to sort the answers into these
        # groups of 3
        count = 0 # we'll use this to count out 3 sections
        sec = [] # this variable is going to hold 3 sections in one list until we move that list to the variable below
        secs_in_3s = [] # MIND OUT OF THE GUTTER
        for section_num, answers in answer_sheet:
            if count == 3: # once we hit 3 sections (ie once sec is [sec#, ans, sec#, ans, sec#, ans])
                secs_in_3s.append(sec) # add them to the bigger variable
                count = 0 # reset count and sec
                sec = []
            sec.append(section_num) # add the section number to sec
            answers.sort() # sort the answers (this will sort them according to the question number, so that we have 1-15 in order)
            sec.append(answers) # append the answers to sec
            count += 1

        # since we're putting the answers in sections in a 3 by x table, if the number of sections is not a multiple
        # of 3 then we have to add some blank sections to fill out the rest of the table
        if sec != []:
            if len(sec) == 6: # if our last set of three sections is a length of 6 (each section has two pieces), we just add it
                secs_in_3s.append(sec)
            if len(sec) == 4: # if we're short a section we append two pieces of whitespace
                sec.append('')
                sec.append('')
                secs_in_3s.append(sec)
            if len(sec) == 2: # if we're short two sections, we append four pieces of whitespace
                sec.append('')
                sec.append('')
                sec.append('')
                sec.append('')
                secs_in_3s.append(sec)

        # now we make the table for the answers sheets (three columns)
        table = Table( TabPS.DEFAULT_WIDTH * 4, TabPS.DEFAULT_WIDTH * 4, TabPS.DEFAULT_WIDTH * 4)
        table.SetAlignment(3)
        for sec_num1, ans_1, sec_num2, ans_2, sec_num3, ans_3 in secs_in_3s: # go through the sections-sorted-into-threes
            p1 = Paragraph(ss.ParagraphStyles.Normal)
            p2 = Paragraph(ss.ParagraphStyles.Normal)
            p3 = Paragraph(ss.ParagraphStyles.Normal)
            p1.append(Text(str('Section ' + str(sec_num1)),qps)) # add the first section number
            if sec_num2 != '':
                p2.append(Text(str('Section ' + str(sec_num2)),qps)) # and second, if there is one
            if sec_num3 != '':
                p3.append(Text(str('Section ' + str(sec_num3)),qps)) # and third, if there is one
            c1 = Cell(p1)
            c2 = Cell(p2)
            c3 = Cell(p3)
            table.AddRow(c1,c2,c3) # append the section number
            for i in range(0, len(ans_1)): # here we go through each of the answers. note that the length of the first (or leftmost) answer set is the one we use. given the current set-up, the first column will never be shorter than any subsequent ones)
                p1 = Paragraph(ss.ParagraphStyles.Normal) 
                p2 = Paragraph(ss.ParagraphStyles.Normal) 
                p3 = Paragraph(ss.ParagraphStyles.Normal)
                try:
                    p1.append(Text(str(str(ans_1[i][0])+'.   '+str(ans_1[i][1])),qps)) # add the answer for the first column, if it exists
                except IndexError:
                    p1.append(Paragraph(Text('',qps))) # otherwise, add a blank
                try:
                    p2.append(Text(str(str(ans_2[i][0])+'.   '+str(ans_2[i][1])),qps)) # add the answer for the second column, if it exists
                except IndexError:
                    p2.append(Text('',qps))
                try:
                    p3.append(Text(str(str(ans_3[i][0])+'.   '+str(ans_3[i][1])),qps)) # and for the third
                except IndexError:
                    p3.append(Text('',qps))
                c1 = Cell(p1)
                c2 = Cell(p2)
                c3 = Cell(p3)
                table.AddRow(c1,c2,c3) # add this row of answers
            c1 = Cell(Text('',qps))
            c2 = Cell(Text('',qps)) # add an extra blank row
            c3 = Cell(Text('',qps))
            table.AddRow(c1,c2,c3)
        section.append(table) # add the whole answer sheet table

    ### Below is the sequence of steps for making 
    elif test_type == 's':
        number_iter = 1 # we'll use this for question numbers
        questions = [] # seperate lists for the questions (in this case the words) and the answers (in this case the sentences)
        answers = []
        q_a = []
        for question in t_database:
            q_a.append([question, t_database[question]]) # make an ordered list of questions and answers from the t_database dict
        shuffle(q_a) # randomize that list
        for qa in q_a:
            questions.append(qa[0]) # make the seperate question and answer lists
            answers.append(qa[1])

        order = copy.copy(questions) # a copy of the list of words, in the order that they should appear as answers, which we'll use for making the grader

        # once we've copied the order of the words, we can make them into a unordered wordbank
        questions.extend(dummies) # add the dummies to the word bank
        questions.sort() # alphabetically sort the words for the wordbank

        n = 2000
        wordbank_table = Table( n, n, n, n, n ) # the wordbank table (5 words per row)
        while len(questions)!=0: # go through each of the words
            try:
                c1 = Cell( Paragraph( Text( questions.pop(0), qps) ) ) # and add them to the table in sets of 5, until you reach the last row and then you'll fill out the remaining cells with blankness
            except IndexError:
                c1 = Cell( Paragraph( ) )
            try:
                c2 = Cell( Paragraph( Text( questions.pop(0), qps) ) )
            except IndexError:
                c2 = Cell( Paragraph( ) )
            try:
                c3 = Cell( Paragraph( Text( questions.pop(0), qps) ) )
            except IndexError:
                c3 = Cell( Paragraph( ) )
            try:
                c4 = Cell( Paragraph( Text( questions.pop(0), qps) ) )
            except IndexError:
                c4 = Cell( Paragraph( ) )
            try:
                c5 = Cell( Paragraph( Text( questions.pop(0), qps) ) )
            except IndexError:
                c5 = Cell( Paragraph( ) )
            
            wordbank_table.AddRow( c1, c2, c3, c4, c5 )

        section.append(wordbank_table) # the wordbank has been added
        section.append(Paragraph(Text('',qps))) # add a bit of whitespace
        section.append(Paragraph(Text('',qps)))

        for answer in answers: # now go through each of the sentences
            p1 = Paragraph(ss.ParagraphStyles.Normal)
            p1.append(Text(str(number_iter)+'. ', qps)) # add the question number
            p1.append(Text(answer, qps)) # add the sentence
            section.append(p1) # add the paragraph to the section
            section.append(Paragraph(Text('',qps))) # add a linebreak
            number_iter += 1 # increment the question number

        ### Move on to the answer key, which is this case is quite straightforward
        p1 = Paragraph(ss.ParagraphStyles.Normal, ParagraphPS().SetPageBreakBefore( True )) # add a section break
        section.append(p1)
        section.append(Paragraph(Text('Answer Key ' + str(student_name) + ' ' + str(test_number),qps))) # add a header
        section.append(Paragraph(Text('',qps))) # linebreak
        num = 1 # for question numbering
        for question in order: # go through the words in order (as a reminder, the "order" here is the order of their respective sentences-with-a-blank in this quiz)
            p1 = Paragraph(ss.ParagraphStyles.Normal)
            p1.append(Text(str(num)+'. ', qps)) # add the question number
            p1.append(Text(question, qps)) # add the word
            section.append(p1)
            num += 1 # increment question number

    # if the test is a definitions test, it's much easier, because we can just list the words with a blank space
    # next to them
    elif test_type == 'd':
        questions = [] # where we'll store the words to put in the assignment
        number_iter=1 # we'll use this to number the questions
        for word in t_database: # go through the words
            questions.append(word) # and add them to the questions list (because t_database is a dict, so we're turning it into a list so it can have an order)
        shuffle(questions) # we randomize the questions
        order = copy.copy(questions) # then save a copy of the questions list in order for use for the grader
        for word in questions: # go through each word in the list
            p1 = Paragraph(ss.ParagraphStyles.Normal) # make a new paragraph
            p1.append(Text(str(number_iter)+'. ',qps)) # add the question number
            p1.append(Text(word, qps)) # add the word
            p1.append(Text('    _________________________',qps)) # add a blank
            section.append(p1) # add the paragraph to the document
            section.append(Paragraph(Text('',qps))) # add a line break
            number_iter += 1 # iterate the question number

    # same for the sentence writing test; here we don't even need the blank. besides the blank, it's identical to the above
    elif test_type == 'w':
        questions = []
        number_iter=1
        for word in t_database:
            questions.append(word)
        shuffle(questions)
        order = copy.copy(questions)
        for word in questions:
            p1 = Paragraph(ss.ParagraphStyles.Normal)
            p1.append(Text(str(number_iter)+'. ',qps))
            p1.append(Text(word, qps))
            section.append(p1)
            section.append(Paragraph(Text('',qps)))
            number_iter += 1

    # get the directory where we'll put the file, and add it to the filename
    dir_prefix = get_student_dir(student_name)
    filename = dir_prefix + filename

    # create the actual document
    DR.Write( doc, open_file( str(filename) ) )
    
    return order

# this is the function that creates the passive assignment. same caveats apply as for the active assignment
def generate_passive_assignement(words_plus_source, student_name, test_number, assign_date, teach_id):
    # we're going to start with asking for some details about how the assignment will look
    
    cn_threshold = False # these variables will be used when we figure out where to pull definitions from words
    cn_dict_dict = False
    words_by_level = False

    # we used to ask if you wanted the words in the order they appeared in the book (or alphabetically), but
    # we always wanted the former, so I cut this step out for now
    in_order = 'y' #lower(raw_input("""Do you want words in order they appeared in book (y if yes)? """))
    if in_order == 'y':
        in_order = True
    else:
        in_order = False

    # first, we ask if the teacher wants definitions, and if yes, in what language
    defin = lower(raw_input("Do you want definitions added to this quiz (enter for no, e for English, c for Chinese, b for combination)? "))
    if defin not in ['e','c','b']:
        defin = False

    # if we want definitions in a combination of languages, we need to decide which levels of words gets Chinese, and which levels get English
    if defin == 'b':
        while True:
            cn_threshold = []
            _cn_threshold = raw_input("Enter the levels that will have Chinese definitions (i.e. 456, 56, 234) ")
            try:
                for number in _cn_threshold: # go through each number added and make sure the number is a number and between 0 and 6
                    cn_threshold.append(int(number))
                    if int(number)>6 or int(number)<0:
                        raise ValueError
                break
            except ValueError:
                continue

    # next we want to ask if the user wants to include verb phrases, then if they want idioms, then if they want a limit on
    # the number of definitions (we only ask if there's a chance of English definitions)
    if defin in ['b','e']:
        __vp = lower(raw_input("Include verb phrases (English) y/n? "))
        if __vp == 'y':
            __vp = True
        else:
            __vp = False

        __id = lower(raw_input("Include idioms (English)? y/n"))
        if __id == 'y':
            __id = True
        else:
            __id = False

        def_limit = raw_input("Enter definitions limit (English; hit enter for no limit). ")
        try:
            def_limit = int(def_limit)
        except ValueError:
            def_limit = 99 # suck it intro CS professors
    else:
        __vp = True
        __id = True
        def_limit = 99

    # some basic document creation functions for pyrtf
    DR = Renderer()
    doc     = Document()
    ss      = doc.StyleSheet
    paper = Paper( 'A4', 9, 'A4 210 x 297 mm' , 11907, 16838 )
    section = Section(paper)
    doc.Sections.append( section )

    # setting the font and making the first paragraph
    tps = TextPS(font=ss.Fonts.TimesNewRoman, size=18) 
    ps = ParagraphPS(alignment = TabPS.RIGHT)
    p1 = Paragraph( ss.ParagraphStyles.Normal, ps)

    # this section puts the upper-right header that has the name, the date and the name of the adviser
    student_full_name = get_student_fullname(student_name)
    p1.append(Text(str(student_full_name), tps))
    section.append( p1 )
    p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
    p1.append(Text("Date: " + str(assign_date), tps))
    section.append( p1 )
    p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
    submit_to = get_adviser_fullname(teach_id)
    p1.append(Text("Adviser: " + submit_to, tps))

    # add a line break
    section.append( p1 )
    section.append(Paragraph(Text('',tps)))

    # this adds the assignment type and number, centered and bigger than the header
    ps = ParagraphPS(alignment = TabPS.CENTER)
    qps = TextPS(font=ss.Fonts.TimesNewRoman, size=20)
    tps = TextPS( bold=1, font=ss.Fonts.TimesNewRoman, size=20)
    p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
    p1.append(Text('Passive Study Assignment #' + str(test_number[1:]), tps))
    section.append( p1 )
    section.append( Paragraph( Text( '', qps) ) ) # add another line

    # that's the set-up for the document, now we have to deal with the word and their definitions
    
    if in_order: # if we want the words to appear in the order that they were in the book
        words_plus_source = sorted(words_plus_source, key = lambda thing: thing[1]) # we need to sort the words according to the source (remember, the source includes a number code for the order in which the words were pulled from the text, which allows this sorting to happen)
    else: # otherwise, we just sort them alphabetically by word
        words_plus_source.sort()

    if not defin: # if we're not defining anything
        n = 3000
        word_table = Table(n, n) # we make a simple 2 column table
        for word, source in words_plus_source:
            if source[-6] == '^': # remove the number tag from the source if there is one
                source = source[:-6]
            c1 = Cell( Paragraph( Text( word, qps) ) ) # one cell gets the word
            c2 = Cell( Paragraph( Text( source, qps) ) ) # the other gets the source
            word_table.AddRow( c1, c2 ) # and we add those cells to the table

        section.append(word_table) # add the table to the document
        
    else: # if we are using definitions, it gets much more complicated
        words_def_source = [] # we'll need new data structure for storing the word with the definition
        if defin == 'e': # if we're using english definitions
            dict_dict = turn_dbase_into_dict('dictionary') # then dictionary is our main dictionary
            cn_dict_dict = False # and there is no secondary dictionary
        elif defin == 'c': # if we're using chinese definitions
            dict_dict = turn_dbase_into_dict('cn_dictionary') # then cn_dictionary is our primary dictionary
            cn_dict_dict = False # and there's no secondary dictionary (sorry, poor choice of variable name)
        else: # if we use a mix
            dict_dict = turn_dbase_into_dict('dictionary') # then we need both dictionaries
            cn_dict_dict = turn_dbase_into_dict('cn_dictionary')
            words_by_level = get_words_by_level() # we'll need words_by_level to tell which word to define with which dictionary

        total_words = len(words_plus_source) # total number of words
        progress_counter = 0 # words we've added so far
        last_progress_print = 0 # a variable that helps the progress tracker determine when to print a progress update
        print "0% completed" # just to get started


        # in this section we're going to fill up the word_def_source table with the words, parts of speech, definitions and sources, in the
        # order that they'll appear in the final document. Note the structure of this table, which mirrors the final
        # document:
        # [
        # [word, part of speech, definition, source]
        # [''  , part of speech, definition, ''    ]
        # [''  , part of speech, definition, ''    ]     (<- this is because each word can have several parts of speech and associated definition)
        # ]
        for word, source in words_plus_source: # we go through each word and its source
            if source[-6] == '^': # if the source is formated like Source^00001..
                source = source[:-6] # then remove the ending section to just make it Source

            definition = get_definition(word, dict_dict, defin, cn_threshold, cn_dict_dict, words_by_level) # get the definition for the word
            progress_counter += 1 # increment a counter that counts the number of words defined so far
            last_progress_print = progress_tracker(progress_counter, total_words, last_progress_print) # feed the progress counter to the progress printing function
            if definition == []: # if there is no definition
                words_def_source.append([word, '', '', source]) # add just the word and the source
            else:
                first = True # this tells us we're in the first line of a word's definition (ie the line that will need the word in the first column)
                for row in definition: # go through each of the definitions for the word (seperated by p.o.s.)
                    if len(row) == 2: # if the length of of the definition is 2, it means it's a standard definition for the word (the alternative, a length of 3, means it's an idiom or a verb phrase, with the idiom or verb phrase itself being the first element in the list)
                        pos = row[0] # get the part of speech
                        if pos == 'verb (used with object)': # these are just some abreviations for longer parts of speech
                            pos = 'verb (trans)'
                        if pos == 'verb (used without object)':
                            pos = 'verb (intrans)'
                        if pos == 'verb (used with or without object)':
                            pos = 'verb'
                        if pos == 'abbreviation': # skip any abbreviations (these are usually things like Department of Transportation D.O.T. under definition for "dot".
                            continue
                        _def = row[1] # get the definition

                        # we now have to assemble the definition. it's not as simple as just tacking it on, because there
                        # are several alterations we want to make. first, some characters have to be packaged so that they
                        # display properly in PyRTF. Next, each definition is composed of a bunch of smaller definitions,
                        # and we sometimes choose to limit the number of these definitions for clarity. these definitions
                        # aren't inheretly seperated out (though that could easily be done), so we have to do some letter
                        # by letter parsing. finally, we want to make the definitions into a list rather just a block of
                        # text, and the vagaries of PyRTF don't make this simple.
                        _def_by_line = "Text(\'-  "  # first, you'll notice that _def_by_line, which is what will fill the definition cell in the passive sheet table, is actually a function. this is related to PyRTF, I can't explain why it works
                        def_counter = 0 # this counts the number of definitions
                        stop_rec = False # this means stop recording, or stop adding letters to the definition
                        for letter in _def: # go through each letter of the definition
                            if letter not in [';','\'','<','>']: # if it's not a special character
                                if not stop_rec:
                                    _def_by_line += letter # add it (assuming we're not in stop_rec)
                            elif letter == '\'': # if there's a quote, we have to couch both the quote and the backslash
                                _def_by_line += "\\\'"
                            elif letter == ';': # if we hit a semi-colon, that's the end of a definition
                                def_counter += 1 # so increment the definition counter by one
                                if def_counter == def_limit: # if we've reached the limit we set for definitions, then quit
                                    break
                                _def_by_line += "\', qps), LINE, Text(\'- " # otherwise, prep the line for the next definition
                            elif letter == '<': # whenever these marks appear in a definition, it's usually some kind of an aside or otherwise unnecessary, so we stop taking the definition
                                stop_rec = True
                            elif letter == '>': # and go back to recording once we reach the end
                                stop_rec = False
                        _def_by_line += "\', qps)" # once we're done with all the definitions (for that p.o.s.), add the ending for the function
                        if first: # once we have _def_by_line done, we either append the below data, if it's the first p.o.s. definition for that word..
                            words_def_source.append([word, pos, _def_by_line, source])
                            first = False
                        else: # or, if not, we append the same, but without the word or the source
                            words_def_source.append(['',pos,_def_by_line,''])

                    # if the p.o.s is an idiom or a verb phrase, it will have three sections instead of two,
                    # because the first one will be the idiom or verb phrase itself (ie, under the definition for
                    # drop, you will have the verb phrase "drop out". we add this extra word as if it is it's own
                    # definition, right below the origianl word (just look at some examples, and it should be clear)
                    elif len(row) == 3:
                        _writer = True # this is just what we'll use to tell if we're adding this definition or not
                        __word = row[0] # the verb phrase or idiom
                        pos = row[1] # part of speech
                        if not __vp: # sometimes we skip vps and/or idioms; here we check if we're going to skip this definition
                            if pos == 'verb phrase':
                                _writer = False
                        if not __id:
                            if pos == 'idiom': # and again if it's an idiom
                                _writer = False
                        if _writer: # if we're not skipping
                            _def = row[2] # the process for definitions is the same as above
                            _def_by_line = "Text(\'-  "
                            def_counter = 0
                            for letter in _def:
                                if letter not in [';','\'']:
                                    _def_by_line += letter
                                elif letter == '\'':
                                    _def_by_line += "\\\'"
                                elif letter == ';':
                                    def_counter += 1
                                    if def_counter == def_limit:
                                        break
                                    _def_by_line += "\', qps), LINE, Text(\'- "
                            _def_by_line += "\', qps)"
                            words_def_source.append([__word,pos,_def_by_line,'']) # the only thing that changes is that we append the vp or idiom where the word would normally go.
                        

        thin_edge  = BorderPS( width=20, style=BorderPS.SINGLE, colour=ss.Colours.Grey ) # defining the edges for a table in pyrtf
        thin_frame  = FramePS( thin_edge,  thin_edge,  thin_edge,  thin_edge )

        last_source = '' # we'll use this to check if the word source has changed (ie if we've reached words from a different chapter)
        word_table = Table(1500, 1350, 7097) # make a three column table (word, pos, definition)
        for word, pos, _def, source in words_def_source: # go through each set of data
            if source != last_source and source != '': # this checks if the source has changed. if it has..
                section.append(word_table)
                p1 = Paragraph( ss.ParagraphStyles.Normal, ps)
                p1.append(Text(source, tps))                          # .. we break the table, add the source as centered text and start a new table
                section.append( p1 )
                word_table = Table(1500, 1350, 7097)
                last_source = source # now the current source is last_source, and we'll wait for it to change
        
            # here we fill out the table, line by line
            c1 = Cell( Paragraph( Text( word, qps) ), thin_frame ) # the word
            c2 = Cell( Paragraph( Text( pos, qps) ), thin_frame ) # the pos
            _def_eval = "Paragraph( " + _def + ")"
            c3 = Cell( eval(_def_eval), thin_frame ) # the definition, but note the use of the eval function, so that we can have a paragraph in the cell, rather than just undifferentiated text
            word_table.AddRow( c1, c2, c3 )

        section.append(word_table) # add the last table section

    dir_prefix = get_student_dir(student_name) # where we'll save the file
    filename = dir_prefix + "V"+'-'+str(test_number)+'-'+str(assign_date.isoformat()[:4])+str(assign_date.isoformat()[5:7])+str(assign_date.isoformat()[8:])+'-'+str(student_name)+'-'+str(teach_id) # the filename

    # log that the passive sheet was created
    add_to_log(student_name, filename)

    # write the file
    DR.Write( doc, open_file( filename ) )

# asks the user what type of test this will be (m/matching, s/sentence completion, d/write definitions, w/write sentences)
def ask_q_type():
    while (True): # will keep looping unless it gets one of the 4
        test_type = raw_input("Enter test type (m, s, d or w): ")
        if test_type in ["m","s","d","w"]:
            return test_type

# this function gets some of the relevant details for the test
def ask_test_details():
    while True: # here we ask for the due date, only accepting properly formatted responses
        due_date = raw_input("Please enter the due date for the exam. (Enter for today) (yyyymmdd) ")
        if due_date == "":
            due_date = date.today()
            break
        try:
            due_date = date(int(due_date[:4]),int(due_date[4:6]),int(due_date[6:]))
            break
        except ValueError:
            pass
    while True: # here we ask for the assign date (the date when the quiz will be given)
        assign_date = raw_input("Pleaser enter the assign date for the exam. (Enter for today) (yyyymmdd) ")
        if assign_date == "":
            assign_date = date.today()
            break
        try:
            assign_date = date(int(assign_date[:4]),int(assign_date[4:6]),int(assign_date[6:]))
            break
        except ValueError:
            pass

    # then we get the teacher's initials
    teach_id = raw_input("Please enter your initials. ")

    # we turn the initials into a full name
    submit_to = get_adviser_fullname(teach_id)

    # and we return all the data
    return due_date, assign_date, teach_id, submit_to

# here we get the test number. the test number is the type of question (m/s/d/w) plus a sequential number. this data is stored
# inside each student's active database (seperately for each type of question). one poor element of the implementation is that because the incremenation is done
# immediately when we run this function, as opposed to as the last step, if there is an error in making a test, the incrementation
# will often stay, depending on how far along the process there was an error.
def get_test_number(q_type, dbase):
    key = '-----'+q_type+'testcounter-----' # this is the "word" in the student database that has the test number information
    tests = do_command("SELECT data FROM %s WHERE word = \'%s\'" % (dbase, key)) # gets the data from that "word"
    if len(tests)==0: # if there is no such "word" (which isn't something that happens anymore)...
        do_command("""INSERT INTO %s (word, data, lockvar) VALUES (\'%s\', \"['0']\", 'False')""" % (dbase, key)) #... add it
        tests = do_command("SELECT data FROM %s WHERE word = \'%s\'" % (dbase, key)) #... re-do the command

    tests = eval(tests[0][0]) # evaluate the text in the data, which will give you a python list
    test_number = str(int(tests[-1]) + 1) # turn the last element of the list into an integer, add one, turn it into a string...
    tests.append(test_number) #... and append it back to the end of the list

    # upload the new list, with the new test number to the counter
    do_command("""UPDATE %s SET data = \"%s\" WHERE word = \"%s\"""" % (dbase,MySQLdb.escape_string(str(tests)),MySQLdb.escape_string(key)))

    return upper(q_type)+test_number # return the test number in complete form

# this function lets the user pick a testsheet file to upload, and opens that file for reading
def upload_test_file(student_name):
    # this is the standard set-up for a "pick a file" function, with only the if statement 6 lines
    # down being different. to see notes on this type of funciton, see get_upload_csv()
    files = os.listdir(os.getcwd())
    
    counter = 1
    v_files = []
    for f in files:
        if f[:10] =='testsheet-' and f[10:10+len(student_name)] == upper(student_name) and f[-4:] == ".csv":
            print str(counter) + ". " + f
            counter += 1
            v_files.append(f)

    if len(v_files)==0:
        print "No acceptable files."
        return False, False
        
    while True:
        csv_name = raw_input('Enter the number of the file you wish to upload or * to quit. ')
        if csv_name == '*':
            return False, False
        if int(csv_name) in range(1,len(v_files)+1):
            csv_name = v_files[int(csv_name)-1]
            break

    # opens up the csv file for reading
    reader = csv.reader(open(csv_name, "rb"))
    return reader, csv_name # returns the reader pointer and the file name

# this function turns the csv reader into a list object
def parse_reader(reader):
    data = [] # the important stuff
    not_data = [] # the not important stuff

    first = True # we make sure we skip the first row
    for row in reader:
        if first:
            not_data.append(row) # I'm not sure why we do this, probably no reason
            first = False # now it's not the first row
        else: # if not the first row, then append to the data
            data.append(row)

    # return the data
    return data

# this function checks the testsheet data for any errors, cleans the data up, and returns it
def clean_test_file(data, q_type):
    clean_data = [] # this variable will collect the cleaned up data
    dummies = [] # this variable will collect dummy words (extra answers for sentence completion quizzes)
    error = False
    for row in data:

        if len(row[0])==0: # skip any empty rows
            continue

        for item in row: # here we check for excess whitespace at the beginning or end of a cell; we go through each cell
            if len(item)!= 0: # and if the cell is not nothing
                if item[0] == ' ' or item[-1] == ' ': # check the first and last character
                    print "White space error: " + row[0]
                    #error = True # there were some words that had whitespace errors, so i didn't make this an error that stopped the program, but I think that should be fixed now

        # row[4] is the user input answer selection column. first, we'll check any one-character entries in this
        # column because these should only be either x's or d's. An x is to select a word for definition and sentence writing
        # tests, and a d is to select a word as a dummy for a sentence completion test. this is technically imperfect, because
        # what if you make a new a matching entry that is only one letter, but that shouldn't ever happen
        if len(row[4])==1:
            # if the entry is 'x' and the test type matches, we're good
            if row[4] == 'x' and q_type in ['d','w']:
                pass
            # if the entry is 'd' and the test type matches, we're good
            elif row[4] == 'd' and q_type == 's':
                dummies.append(row[0]) # plus append the word (row[0]) to the dummy list
                continue
            else:
                print "Answer error: " + row[0] # otherwise, we have a one-letter answer that isn't right
                error = True
                
        # next, we'll run some checks for not one-letter entries 
        if len(row[4])!=0 and row[4][0] != '*':  # if the entry isn't nothing and it doesn't start with '*' (i.e. has "***needs new***" in the cell)
            for letter in row[4]: # then go through each letter and ...
                if letter in foreign_letters: # make sure none of them are part of the foreign letters list
                    print "Foreign letter error: " + row[0]
                    error = True
            if q_type == 'm': # at this point, we append the data to clean_data
                clean_data.append([lower(row[0]),lower(row[4])]) # if it's matching, we make both the word and the answer lower-case, just in case
            else:
                clean_data.append([lower(row[0]),row[4]]) # whereas if it's sentence completion, or anything else, we keep it as is

    # now, we'll go through the clean data, to check a few more things
    for row in clean_data:
        if row[1][1:].isdigit(): # if the part after the first character of the entry is a number (as in m1, s12, m7, etc.)
            if row[1][0]!=q_type: # make sure that the first letter is the same as the question type that was selected for the exam (i.e., you did select s1 for a matching exam)
                print "m/s error: " + row[0]
                error = True
        if q_type == 's' and not row[1][1:].isdigit(): # if we're doing a sentence completion exam, and it's a new entry (i.e., not s1 or s2 but a new sentence completion answer), then 
            if '---' not in row[1]: # check that we have the '---' fill-in-the-blank marker somewhere in there
                print "--- error: " + row[0] 
                error = True

    # even if there's an error, we go to the end, and then return the same variables, either with error or without
    if error:
        return clean_data, dummies, True
    else:
        return clean_data, dummies, False

# we do this manually above, but this function is to check if a question is a new entry or a selection of an existing entry
def check_new_q(q):
    if q[1:].isdigit(): # if the characters after the first character are numbers, odds are it's an existing answer (m1, m2, s11, etc.)
        return False
    else: # otherwise, it's definitely new 
        return True

# this function takes a word, the new question for the word, the existing answers for the word, and the question type.
# it produces a new key (m1, s1, ...) for the new question, adds it to the dictionary object of the existing answers.
def assign_new_key(word, new_q, answers, q_type):
    if answers=={}: # if there are no existing answers
        key = q_type + '1' # the key is just the question type plus 1 (m1 or s1)
        answers={key:new_q} # that's your new answers dictionary object
    else:
        counter = 1 # otherwise, we make a counter
        for answer_key in answers: # and we go throught the existing answers
            if answer_key[0] == q_type: # and for every answer that matches the question type
                counter+=1 # increment the counter by 1
        key = q_type + str(counter) # then we combine the question type (m or s) and the counter, to get the new key
        answers[key]=new_q # and we add the new question and the new key to the answers dictionary

    data = (word,str(answers)) # we make a new data object that is a list with the word and a string version of the answers
    
    return key, data # and we return the new key and the data

# this function takes in a word and a key and the mainvocab dictionary and returns the answer associated with the key
def get_question_key(word, key, ddict, q_type):
    if not ddict.has_key(word): # make sure the vocabmain has that word (unlikely but not impossible, like if someone accidently changed a word in the testsheet)
        print "Word not in main: " + word
        return False
    
    answers = ddict[word] # get all the possible answers for that word
    for _key in answers: # go through each key
        if _key == key: # and if the key matches 
            return answers[key] # return the answer associated with the key (this is kind of a silly way of doing it, oh well)

    # this means that key doesn't exist for that word (i.e., user entered m4 when it only goes up to m3 for that word)
    print "Question not found: " + word
    return False

# this function creates a grading file, the one that will associated with this test
# filename = the filename of the new created test
def open_grading_file(filename, student_name):
    dir_prefix = get_student_dir(student_name) # the program puts the grading file in the student's directory
    
    name = dir_prefix + 'grader'+filename+'.csv' # the grader file name is just the test file name with "grader" in front
    writer = csv.writer(open(name, 'wb'), dialect = 'excel') # creates the file, ready for writing
    
    return writer

# this function creates the grader csv file and then fills it up with all the relevant data
# data is a dictionary object formated like word:[answer, answer key], order is the order the words are in, filename is
# the name of the test document, assign_date = the date the test was assigned
def make_grading_file(data, order, filename, assign_date, student_name):
    writer = open_grading_file(filename, student_name) # creates the files

    # note that order is a list object, and data is a dict object, because list objects have an order to them.
    # we go word by word through the order, and pull the data from the dict object
    for word in order:
        row = [word, ''] # start by adding the word and the user input column
        row.append(data[word][0]) # the answer
        row.append(data[word][1]) # the key for the answer
        row.append(str(assign_date)) # the assign date
        writer.writerow(row) # add the row

    return

# this takes all the data and sorts it into new answers and ones that already existed (see check_new_q(q) for details on method)
def sort_out_new_from_old(data):
    new = []
    old = []
    for item in data:
        if item[1][1:].isdigit(): # not sure why we don't just use check_new_q(q) here, since we made that function already
            old.append(item)
        else:
            new.append(item)

    return new, old # returns old and new seperately

# this function takes in all the words and data, and has the user double-check all of the new answers
def user_question_checker(data, q_type):
    new_q_data, old_q_data = sort_out_new_from_old(data) # first get the new answers seperate from the already existing ones
    _5s_data = sort_into_5s(new_q_data) # run the new answers through the check by 5s method
    new_5s_data = check_by_5s(_5s_data, q_type)
    new_data = flatten_5s(new_5s_data) # in the end, you get a list of the new answers post-editting
    for item in old_q_data:
        new_data.append(item) # add all of the already existing answers back into the post-editting new answers data set
    
    return new_data # returns all the words and their data, post-editting

# this function updates, in one batch command, the vocabmain database with the new information taken from the
# testsheet (essentially, adding any new answers to words stored in the vocab main)
def batch_update_main(to_add_main_data, main_name):
    replace_command = "UPDATE %s SET data = CASE " % main_name
    for word, data in to_add_main_data:
        replace_command += """WHEN word = \"%s\" THEN \"%s\" """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(data))
    replace_command += "ELSE data END;"
        
    do_command(replace_command)

# this function updates, in one batch command, the student's database, updating words that have been added for testing
def batch_update_active(to_replace_words, student_name):
    if len(to_replace_words) !=0:
        replace_command = "UPDATE %s SET data = CASE " % student_name
        for word, data in to_replace_words:
            replace_command += """WHEN word = \"%s\" THEN \"%s\" """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str(data)))
        replace_command += "ELSE data END;"
        
        do_command(replace_command)

# this function goes through the data and marks words as being "out" in the student data, in other words, marks that they
# are currently in an exam that has not been graded yet. it's fine if the word is out in several exams at the same time.
# clean data is organized as a list of lists structured as [word, question]
def mark_student_words(student_dict, clean_data):
    new_data = [] # this is the new variable where we'll put the updated data

    for word, q in clean_data: # we go through each word in clean_data
        word_data = student_dict[word] # get the student database data for that word
        word_data[0].append('^^^out^^^') # add the out marker to the word's data in the student database
        new_data.append([word, word_data]) # append add the updated data to the new variable

    return new_data

# this is the higher level function that, taking the student's name and the name of the vocabmain database, uploads
# a testing sheet, cleans it up, creates the document and finally makes relevant changes in the student and main databases.
def intake_testing_sheet(student_name, main_name):
    pause = raw_input("Save and close the testsheet file and hit enter.") # this is there just to get the user to save and close the file, so the program can delete it later
    
    reader, to_delete_file_name = upload_test_file(student_name) # gets a csv reader version of the test, and the file name for later deletion
    if reader == False:
        return False

    q_type = ask_q_type() # asks the user for the question type

    due_date, assign_date, teach_id, submit_to = ask_test_details() # asks the user for other details
    
    data = parse_reader(reader) # get the csv data into a local python object
    
    clean_data, dummies, _error = clean_test_file(data, q_type) # clean up the data, + get any sentence completion dummy words
    if len(clean_data)==0: # check that there are at least some questions selected 
        print "No questions selected."
        return False

    dict_for_grader = {} # the dictionary object we'll use for the data that will go into the grader file
    dict_for_test = {} # the same, but for the actual test

    main_dict = turn_dbase_into_dict(main_name) # get the vocabmain database as a dict
    
    error = False
    for word, q in clean_data: # go through each word and selected question
        if not check_if_word_exists_in_dict(word, main_dict): # make sure the word exists in the vocabmain
            print "Incorrect word: " + word
            error = True
            continue
        if q_type not in ['d','w']: # if the question is a matching or sentence completion question...
            if not check_new_q(q): # ... and if the question is not a new, user-generation question...
                question = get_question_key(word, q, main_dict, q_type) # ... make sure the selected question key is proper
                if question == False:
                    error = True   

    if error or _error: # if during either the cleaning or the previous round of checking, there was an error, quit
        print "Errors found."
        return False

    if q_type not in ['d','w']: # if we have the possibility of new questions
        clean_data = user_question_checker(clean_data, q_type) # let the user review and edit all of the new additions before we add them for good 

    student_dict = turn_dbase_into_dict(student_name)
    marked_student_words = mark_student_words(student_dict, clean_data) # mark the words as being "out" in the student db

    to_add_main_data = [] # this list will hold all the words with new questions, along with the new question data, for adding to the vocabmain

    if q_type not in ['d','w']: # if we're making an M or S test
        for word, q in clean_data: # look at the word and the q (which is either a key or a typed in new question) and find the key and the question

            if check_new_q(q): # if it's a new question
                key, to_add_batch = assign_new_key(word, q, main_dict[word], q_type) # generate a key for that question
                if key == False: # if there's some problem, go to the next word
                    continue
                question = q # the question is the q
                to_add_main_data.append(to_add_batch) # and we're going to add the new question 
            else: # it's not a new question
                key = q # then q is the key
                question = get_question_key(word, q, main_dict, q_type) # and we'll used that key to get the question
                if question == False: # if we don't find a question, then skip it
                    continue

            # now, whether it was a new question or an old one, we have both a key and a question
            dict_for_grader[word] = [question, key] # add the question and the key to this dict, which will be used to make the grader
            dict_for_test[word] = question # add just the question to this dict, which will be used to make the test

    elif q_type in ['d','w']: # if we're making a D or W test, then it's a bit easier
        for word, q in clean_data: # for each word..
            dict_for_grader[word] = ['___', 'd'] # .. we just add some standard text
            dict_for_test[word] = 'd'

    # if we have new questions to add to the vocabmain, add them
    if len(to_add_main_data)!=0:
        batch_update_main(to_add_main_data, main_name)

    # get the test number for this test
    test_number = get_test_number(q_type, student_name)

    # the filename for the test
    filename = "V"+'-'+test_number+'-'+str(assign_date.isoformat()[:4])+str(assign_date.isoformat()[5:7])+str(assign_date.isoformat()[8:])+'-'+upper(student_name)+'-'+teach_id

    # make the test (it returns the order of the questions)
    order = make_test(dict_for_test, q_type, student_name, due_date, dummies, submit_to, test_number, filename)

    # make the grading file (the order is used to make sure the order is the same in the grader as in the test)
    make_grading_file(dict_for_grader, order, filename, assign_date, student_name)

    # print a confirmation
    print "Test (" + str(filename) + ") created."

    # update the marked words in the student db
    batch_update_active(marked_student_words, student_name)

    # log that a test was created
    add_to_log(student_name, filename)

    return to_delete_file_name
    
####################################
#################################### below are functions for making the passive sheet
####################################

# gets the details for the passive assignment - however, in the current one-step intake system, this function is skipped
def ask_passive_details():
    while True: # this asks for when the passive assignment will be assigned
        assign_date = raw_input("Pleaser enter the assign date for the reading. (Enter for today) (yyyymmdd) ")
        if assign_date == "":
            assign_date = date.today()
            break
        try:
            assign_date = date(int(assign_date[:4]),int(assign_date[4:6]),int(assign_date[6:]))
            break
        except ValueError:
            pass

    # this asks for the teacher initials
    teach_id = raw_input("Please enter your initials. ")

    return assign_date, teach_id

# this function either let's the student pick the passive sheet to upload or (in the one-step system) just has the file
# inputted directly, and it just opens the file
def upload_passive_file(student_name, passive_sheet_name):
    if not passive_sheet_name: # if this variable is false, it means we're outside of the one-step system
        files = os.listdir(os.getcwd()) # the below mechanism should be familiar already
        
        counter = 1
        v_files = []
        for f in files:
            if f[:8] =='passive-' and student_name in lower(f) and f[-4:] == ".csv":
                print str(counter) + ". " + f
                counter += 1
                v_files.append(f)

        if len(v_files)==0:
            print "No acceptable files."
            return False
            
        while True:
            csv_name = raw_input('Enter the number of the file you wish to upload or * to quit. ')
            if csv_name == '*':
                return False
            if int(csv_name) in range(1,len(v_files)+1):
                csv_name = v_files[int(csv_name)-1]
                break
    else: # if we are in the one-shot system, then we've been passed the name of the file we want and..
        csv_name = passive_sheet_name

    reader = csv.reader(open(csv_name, "rb")) # we just open the file
    return reader # and return it

# this functions turns the passive sheet into data that we can clean and parse
def parse_passive_file(reader):
    data = []
    not_data = []

    first = True # this just means we're in the first row of the file
    for row in reader:
        if first: # if it is the first row
            not_data.append(row) # it's not data
            first = False # then we're no longer in the first row
        else:
            data.append(row) # so we start appending the data

    return data # and return the data

# this function takes the data from the passive sheet, cleans it up, checks it for errors and returns it
def clean_passive_file(data):
    clean_data = [] # where we'll store the cleaned up data
    error = False # something to keep track of if there's an error (we don't want to quit as soon as there's an error, because we want the user to see all the errors before quitting)

    for row in data: # go through each row
        for item in row: # in each row go through each column
            if len(item)!= 0: # if it's not a blank space
                if item[0] == ' ' or item[-1] == ' ': # make sure there's no extra whitespace
                    print "White space error: " + row[0]
                    error = True
                    continue
        if len(row[1])!=0: # if the row where you choose words isn't empty..
            if row[1] != 'x': # it should be an 'x'. if it isn't, you have an error
                print "Choosing mark error: " + row[0]
                error = True
                continue
            else: # if it is an 'x', which means the words has been chosen, then we do a few more things
                try:
                    date = row[4] # we check the date to make sure it's a proper date
                    dm_date = date[:-5]
                    _date = datetime.date(int(date[-4:]), int(dm_date[:dm_date.index('/')]), int(dm_date[dm_date.index('/')+1:]))
                except (ValueError, IndexError):
                    try: # we try taking in the date in two formats - this is because when passive sheets are manually filled out, the date is saved in a different format from when the program creates a pre-filled out passive sheet in the one-step system
                        date = row[4]
                        date = date.replace('-','')
                        _date = datetime.date(int(date[:4]),int(date[4:-2]),int(date[-2:]))
                    except (ValueError, IndexError): # if neither works, then you've got an error
                        print "Date problem: " + row[0]
                        print row[4]
                        error = True
                        continue
                clean_data.append([lower(row[0]), row[3],_date]) # if we've made it this far, add the marked word and the cleaned data to the list

    if error: # either send back an error or the data
        return False 
    else:
        return clean_data

# this gets a new number for the passive assignment (see similar function in active assignment above for mechanism)
def get_ptest_number(dbase):
    key = '-----ptestcounter-----'
    tests = do_command("SELECT data FROM %s WHERE word = \'%s\'" % (dbase, key)) # get the current counter
    if len(tests)==0:
        print "Something wrong with test numbers."
        return 'P0'

    tests = eval(tests[0][0]) # figure out the latest number
    test_number = str(int(tests[-1]) + 1) # add one to get your new number
    tests.append(test_number) # add that number to the list

    # update the databse with the new number
    do_command("""UPDATE %s SET data = \"%s\" WHERE word = \"%s\"""" % (dbase,MySQLdb.escape_string(str(tests)),MySQLdb.escape_string(key)))
    return 'P'+test_number

# this is the batch one command updates that should be familiar aleady, in this case for an uploaded passive sheet
def batch_passive_sheet_update(to_add_main_words, to_add_active_words, to_delete_p_words, main_name, student_name, passive_name):
    # first, add the words that are going into the passive assignment to the active list
    if len(to_add_active_words) !=0:
        add_active_command = "INSERT INTO %s (word, data, lockvar) VALUES " % student_name
        for word, date, source in to_add_active_words:
            add_active_command += """(\"%s\", \"%s\", 'False'), """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str([[],[],[100.0],[],[date, date.today(), source]])))
        add_active_command = add_active_command[:-2] + ';'
        
        do_command(add_active_command)

    # then add any words that aren't in vocabmain to vocabmain
    if len(to_add_main_words) !=0:
        add_main_command = "INSERT INTO %s (word, data, lockvar) VALUES " % main_name
        for word, date, source in to_add_main_words:
            add_main_command += """(\"%s\", \"%s\", 'False'), """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str({})))
        add_main_command = add_main_command[:-2] + ';'
        
        do_command(add_main_command)

    # then, delete the passive words that are going into the passive assignment from the passive list
    if len(to_delete_p_words) !=0:
        delete_p_command = "DELETE FROM %s WHERE " % passive_name
        for word, date, source in to_delete_p_words:
            delete_p_command += """word = \"%s\" OR """ % MySQLdb.escape_string(word)
        delete_p_command = delete_p_command[:-3] + ';'
        
        do_command(delete_p_command)

    return

# turns a string date into date variable
def turn_into_date(str_date): 
    var_date = date(int(str_date[:4]),int(str_date[4:6]),int(str_date[6:])) # oof, this should be error-checked
    return var_date

# this is the function that handles the intake of a passive sheet on the higher level, going through all the steps
# note the variables with default values. these three are passed values in the one_step system, so that we can
# circumvent some user inputs during this step, notably because in the one-step system the passive sheet is pre-prepared,
# so we know exactly which sheet we already want to upload (passive_sheet_name).
def intake_passive_sheet(student_name, main_name, passive_sheet_name = False, _assign_date = False, _teach_id = False):
    passive_name = student_name+"passive" # the name of the passive db

    # get the passive sheet
    reader = upload_passive_file(student_name, passive_sheet_name)
    if reader == False:
        return

    # turn the passive sheet into data
    data = parse_passive_file(reader)

    # clean up the data
    data = clean_passive_file(data)

    # quit if there's been an error
    if data == False:
        print "Error..."
        return

    # if we're not in the one shot system, ask for some details about this assignment. otherwise, just take them from the variables we were passed
    if not _assign_date or not _teach_id:
        assign_date, teach_id = ask_passive_details()
    else:
        assign_date = turn_into_date(_assign_date)
        teach_id = _teach_id

    # get the assignment number for this assignment
    test_number = get_ptest_number(passive_name)

    # where we'll store the data for when we make the actual assignment
    words_sources = []

    # get all the words from the three databases: vocabmain, the student's active and the student's passive
    main_words = get_words_list(main_name)
    active_words = get_words_list(student_name)
    passive_words = get_words_list(passive_name)

    to_add_main_words = [] # new words that need to be added to the main
    to_add_active_words = [] # new words that need to be added to the active
    to_delete_passive_words = [] # words that need to be added to the passive

    # go through each word in the data
    for word, source, date in data: ### NOTE: should be word, date, source (for consistency), but not fixing now
        if word not in passive_words: # if the word isn't actually a passive word, problem
            print "Not actually a passive word (epic fail): " + word
        elif word in active_words: # if it's already an active word, skip it
            print "Already active word: " + word
        else: # otherwise..
            to_add_active_words.append((word,date,source)) # .. we'll be adding it to the active sheet
            to_delete_passive_words.append((word,date,source)) ## .. deleting it from the passive
            if word not in main_words:
                to_add_main_words.append((word,date,source)) ##.. and adding it to the main list if it isn't there yet (under the current system that should never happen since we're picking from a closed set of words, all of which are already in the vocabmain file)
            words_sources.append([word,source]) # .. adding it to the list that we use for the test.

    # create the actual assignment
    generate_passive_assignement(words_sources, student_name, test_number, assign_date, teach_id)

    # update all three databases
    batch_passive_sheet_update(to_add_main_words, to_add_active_words, to_delete_passive_words, main_name, student_name, passive_name)
    
    print "Passive assignment generated."

    return  

###################################################################################
### UPLOAD GRADING SHEET COMMANDS
# upload_grading_sheet(student_name)
# upload_grader_data(reader)
# question_exists(word, question, key, main_name)
# add_graded_result(word, grade, key, date, dbase)
# intake_grading_sheet(student_name, main_name)
###################################################################################

# this function follows the standard mode for getting the user to choose a file, in this case the grader file they want.
def upload_grading_sheet(student_name):
    dir_pre = get_student_dir(student_name) # gets the student directory
    try:
        files = os.listdir(dir_pre) # looks there for files
    except WindowsError: # if they can't find the directory
        dir_pre = '' # we'll be looking in the same folder as the vocab program
        files = os.listdir(os.getcwd())
    
    counter = 1
    v_files = []
    for f in files:
        if f[:6] =='grader' and lower(student_name) in lower(f) and f[-4:] == ".csv": # find all the files that are graders and for the current student
            print str(counter) + ". " + f
            counter += 1
            v_files.append(f)
    
    if len(v_files)==0:
        print "No acceptable files."
        return False, False
    
    while True: # ask for the file the user wants
        csv_name = raw_input('Enter the number of the file you wish to upload or * to quit. ')
        if csv_name == '*':
            return False, False
        elif not csv_name.isdigit(): # make sure it's a number
            continue
        elif int(csv_name) in range(1,len(v_files)+1):
            csv_name = v_files[int(csv_name)-1]
            break
        else:
            continue


    csv_name = dir_pre+csv_name # add the directory prefix to the file name
    reader = csv.reader(open(csv_name, "rb")) # open the file
    return reader, csv_name

# this function turns the csv.reader object into a list that has all the in the file and returns it
def upload_grader_data(reader):
    data = []
    for row in reader:
        data.append([row[0],row[1],row[2],row[3],row[4]])
    return data 

# this function checks that there's a match between the key and question in the grader sheet and
# what should be the same key and question in the mainvocab file. this is to make sure that the grader file itself
# hasn't been tampered with (although this isn't super important) and that (more importantly) the mainvocab database hasn't
# been changed in some way.
def question_exists(word, question, key, main_dict):
    if not main_dict.has_key(word): # first we check that mainvocab has word at all
        print "Not in main: " + word
        answers = {}
    else:
        answers = main_dict[word]
    
    if answers.has_key(key): # then we check if the mainvocab entry for that word has the key
        if answers[key] == question: # and if the question associated with the key matches the question we're uploading
            return True
        
    print "Corrupt question: " + word
    return False

# this function takes the grading information and creates an updated entry for that word in the student database 
def parse_graded_result(word, grade, key, date, ddict, dbase):
    if not ddict.has_key(word): # first, just make sure the student database has the word in question
        print "Not in student db: " + word
        return False, False, False
    data = ddict[word] # get the student database data for that word
    try:
        data[0].remove('^^^out^^^') # try to remove the marker that states the word is outstanding (not that this operation is order independent - if the word is out in multiple tests, it doesn't matter which one is removed)
    except ValueError:
        print "^^^out^^^ error: " + word # while we transitioned to the out system, this happened, but it shouldn't anymore unless someone duplicates a grader sheet by accident. still, just in case, i'm not marking this as an error that stops the grading process
    data[0].append(key) # this adds the question key to the list of questions that the student has done already
    if lower(grade) == 'x': # if the student got it wrong
        data[1].append('0') # add a zero to the right/wrong list
        one_wrong = True # (then we have at least one wrong in this grader sheet)
    elif grade == '': # otherwise
        data[1].append('1') # add a 1
        one_wrong = False
    elif grade == 's': # OTHERWISE
        one_wrong = True  # it's a skipped question - neither right nor wrong, we just get rid of the ^^^out^^^
    else: # OTHER OTHERWISE
        print "Invalid grade marker ("+grade+"): " + word # you done fucked up
        return False, False, False

    # here we re-calucate the "weight" variable, which is just a score for how important it is to test that word again
    # it's fairly straightforward. if a word has never been tested, it's 100. if it has been tested, but the student
    # has never gotten it right, it is higher than 100, the more times wrong the higher. if the student has gotten it
    # right at least once, it's under 100, and the weight just becomes a ratio of wrong to right. in the testsheet
    # words are sorted according to this weight.
    corrects = 0
    for result in data[1]:
        corrects += int(result)
    incorrects = len(data[1]) - corrects
    weight = 0.0
    try:
        weight = float(incorrects) / float(corrects)
    except ZeroDivisionError:
        weight = 100.0 + float(incorrects * 10) 
    data[2] = [weight]

    # hmm, here we add the date of the test, though it seems like we do this even if a question is "skipped". that shouldn't happen, even if it won't lead to any major errors.
    try:
        dm_date = date[:-5]
        _date = datetime.date(int(date[-4:]), int(dm_date[:dm_date.index('/')]), int(dm_date[dm_date.index('/')+1:]))
        if grade != 's': # well, this should fix it, though i'll keep the note above in case you have a problem with excess dates later on that you can't explain
            data[3].append(_date)
    except (ValueError, IndexError): # note the explanation below; i forget why but after you save it the way the date is stored actually changes. should be fixed.
        print "Date problem: " + word + ". If you get this for every question, open the grader file, don't change anything, but save it, then close it, then try again. Sowweeee."
        return False, False, False
    
    return word, data, one_wrong

# this just makes a long MySQL command that updates all the words in the grader file with the new data in one go (this should be a famliar mechanism)
def batch_grader_update(to_replace_words, student_name):
    if len(to_replace_words) !=0:
        replace_command = "UPDATE %s SET data = CASE " % student_name
        for word, data in to_replace_words:
            replace_command += """WHEN word = \"%s\" THEN \"%s\" """ % (MySQLdb.escape_string(word),MySQLdb.escape_string(str(data)))
        replace_command += "ELSE data END;"
        
        do_command(replace_command)

# this is the main function for taking in the grading sheet. it goes through each step, from finding the file, to uploading it,
# to changing the data, to sending the changes back to the mysql db
def intake_grading_sheet(student_name, main_name):

    # just a reminder to close the file so we can delete it
    pause = raw_input("Close the grader file and hit enter.")
    
    reader, csv_name = upload_grading_sheet(student_name) # get the file
    if reader == False:
        return False

    data = upload_grader_data(reader) # get the data from the file

    main_dict = turn_dbase_into_dict(main_name) # get the mainvocab
    student_dict = turn_dbase_into_dict(student_name) # get the student active db
    
    error = False
    for word, grade, question, key, date in data: # go through the data once to see if there are any errors
        if len(word) == 0: # check if a word has been removed
            continue
        if question!="___" and key!="d": # and, if the test is an M or S test
            if not question_exists(word, question, key, main_dict): # make sure the questions that were in the test are the same as the ones in mainvocab
                print "Question mismatch error: " + word
                error = True

    if error: # if any errors were found, don't upload
        print "Mismatches found. Grades not uploaded."
        return False

    one_wrong = False # this variable checks whether there is at least one mistake - this is to prevent cases where the teacher actually forgot to enter grades before uploading

    to_replace_words = [] # this is the list that will be used to update the mysql database
    for word, grade, question, key, date in data: # go through each word in the test
        if len(word)!=0:
            _word, _data, _one_wrong = parse_graded_result(word, grade, key, date, student_dict, student_name) # this changes the student active database to reflect the new grade
            if not _word: # this checks if there's an error
                error = True
            if _one_wrong: # this tracks if there is at least one mistake
                one_wrong = True
            to_replace_words.append((_word,_data)) # add the word and the new student data for the word to a list

    if error:
        print "Errors found. Grades not uploaded."
        return False

    # if there aren't any mistakes, we just double check that that is what the teacher intended
    if not one_wrong:
        double_check = lower(raw_input("Looks like no questions were wrong, is that correct? (y to confirm, anything else to quit): "))
        if double_check != 'y':
            return False

    #update the mysql database
    batch_grader_update(to_replace_words, student_name)

    # log it
    add_to_log(student_name, csv_name)
    
    print "Upload sucessful."
    return csv_name

# this basically does the same thing as the above function, but it's for if you want to un-assign the test, rather than
# grade it. it just removes all the ^^^out^^^ markers associated with the word
def intake_null_grading_sheet(student_name, main_name):
    reader, csv_name = upload_grading_sheet(student_name)
    if reader == False:
        return False

    to_unmark = []

    for row in reader: # we'll unmark every word
        to_unmark.append(row[0])

    student_dict = turn_dbase_into_dict(student_name)

    unmark_data = []

    for word in student_dict: # go through each word in the student active db
        if word in to_unmark: # if it's slated for unmarking
            w_data = student_dict[word]
            try:
                w_data[0].remove('^^^out^^^') # take out the marker
            except ValueError:
                print "^^^out^^^ error: " + word
            unmark_data.append([word, w_data]) # save the new data in a list

    batch_grader_update(unmark_data, student_name) # upload the new data to mysql

    return csv_name

###################################################################################
### ONE-SHOT SHORTCUTS
#
# print_summary_stats(stats)
# book parser
# text_active_one_shot(student_name, main_name)
#
###################################################################################

# this function prints summary statistics for a selection of text after it's been parsed
def print_summary_stats(stats, n_words):
    _sum = 0 # this will count the total number of new words
    print 'All words by level:'
    for level in range(7):
        print 'Level '+ str(level) + ': ' + str(stats[level]) # print each level and the number of words corresponding to it
        _sum += stats[level] # add the words to the word total
    print ''

    # provide # of new words + estimate of passive assignment length
    print "Total new words: " + str(_sum-len(n_words)) + " (~" + str((_sum-len(n_words))/20) + " pages with definitions)"
    
    cont = raw_input('Hit enter to continue, * to quit with no changes. ') # ask if the person wants to continue or quit
    if cont == '*':
        return False
    else:
        return True

# this big function handles all the steps of taking in a piece of text, parsing it for words, seperating them according
# to difficulty, and returning the relevant words in a way that the passive sheet functions can read
def book_parser():
    while True:
        # gets the name of the text file
        book_name = raw_input("Enter text file name for text they will be assigned (without .txt extension; * to quit): ")
        if book_name == '*':
            return False, False, False, False

        book_name = './textfiles/' + book_name + '.txt' # appends the directory where we'll find it, plus extension
        try:
            l = open(book_name) # opens the file
            break
        except IOError: # if we can't open it, the name is wrong
            print "File not found, make sure you put the file in the 'textfiles' subfolder."
            
    while True: # get the date when that text will be assigned
        assign_date = raw_input("Please enter the assign date for the text. (Enter for today) (yyyymmdd) ")
        if assign_date == "": # if the user hits enter, it's just today's date
            assign_date = date.today() # get date
            assign_date = str(assign_date) # stringify
            assign_date = assign_date.replace('-','') # change the dashes to nothing
            break
        if assign_date == "*": # if quit, then quit
            return False, False, False, False
        try: # otherwise, try to turn what they entered into a date
            assign_date = date(int(assign_date[:4]),int(assign_date[4:6]),int(assign_date[6:]))
            assign_date = str(assign_date) # and stringify
            assign_date = assign_date.replace('-','') # and get rid of dashes
            break
        except ValueError: # if it's not a number, it's a mistake
            pass
        
    # asks if the input file is chaptered with ^^^^^ marks (see SUMMARY if you're not sure what this is)
    chaptered = lower(raw_input("Is your input file chaptered with ^^^^^ marks (y/n, * to quit)? "))
    if chaptered == 'y':
        chaptered = True # if it is, we have a variable for that
    elif chaptered == '*':
        return False, False, False, False
    else:
        chaptered = False # if it's not, we mark it as such
        add_words = True # this variable says that we're going to start adding words immediately once we start parsing (ie we're not skipping any chapters at the start of the textfile)
        add_all = True # this variable says adding all of the words in the text file (ie we're not skipping any chapters at all)

    if chaptered:
        ch_counter = 0
        first_ch = raw_input("Enter assignment start chapter (enter for all chapters): ") # if it's chaptered, enter the start chapter for the passive assignment
        if first_ch == '': # if we're doing all chapters...
            add_words = True # .. it's the same as if there were no chapters
            add_all = True
        else:
            add_words = False # otherwise, we're assuming we may skip chapters
            add_all = False
            try:
                first_ch = int(first_ch) # we turn the given chapter into a number
            except ValueError: # unless we can't, then we quit
                print "Not a number."
                return False, False, False, False

            # now we ask for when the 
            end_ch = raw_input("Enter assignment end chapter (enter for same as start chapter, 'l' for last chapter): ")
            if end_ch == '': # if it's a one chapter assignment
                add_words_chapters = [first_ch] # then it's just the one chapter
            elif end_ch == 'l': # if we're going to the end of the book...
                add_words_chapters = range(first_ch, 10000) # OMG BIGGEST HACK EVER - better would be to check the number of chapters but WEEEEEE
            else: # otherwise, we'll check if the entered chapter is a number..
                try:
                    end_ch = int(end_ch)
                except ValueError:
                    print "Not a number."
                    return False, False, False, False
                add_words_chapters = range(first_ch, end_ch+1) # .. and these are the chapters of the assignment

    # here we ask for the name of the book
    source = raw_input("Enter title of book (for \'source\' field): ")
    if chaptered: # since we want the chapter to be part of the source name, we'll change the source name with the chapter as we go along. here we add the first chapter in our assignment range
        _first_ch = " Ch" + (2-len(str(ch_counter)))*'0' + str(ch_counter) # note that this doesn't work if more than 100 chapters
        source = source + _first_ch
    
    try: # here we need the minimum word level (this is inclusive, ie 2 will include level 2 words)
        level = int(raw_input("Enter the minimum word level for this book (0-6, * to quit): "))
    except ValueError: # if it's not a number then aaaaaaaaaaahhhhhhhhhhhh actually this should limit to 0-6
        print "Not a number."
        return False, False, False, False

    words_by_level = get_words_by_level() # this retrieves a list of words with their level assignment


    # this section is for getting all the words from the text file and seperating them as entries in a list. because the
    # file is just a collection of characters, we have to read the file letter by letter and figure out what's a word
    # and what isn't.
    
    words = [] # this will hold the words
    counter = 1 # this is used in another section for counting words
    for n in l: # for each section? in the file (i'm not actually what the "n" here is; it's not letter, maybe .txt files are seperated by breaks?)
        word = '' # this is for holding the current word as it's built
        first_word = '' # the next three will be used for when words have a hyphen in them (because it's ambiguous if it's two words hyphenated together or one word that's been broken up between lines)
        second_word = ''
        second_count = False
        for letter in n: # for each character in whatever the n section is..
            if letter == '-': # if the character is a hyphen
                first_word = word # we hold the word we've been building in this place-holder
                second_count = True # and we indicate that we're starting counting the second word (or the second half of the first word)
            elif letter.isalpha() or letter == '^': # otherwise, if the character is a letter or the chapter header "^"
                word = word + letter # add it to the word
                if second_count: # if we're counting the second word post-hyphen
                    second_word = second_word + letter # add the letter to the second word as well
            else: # otherwise, we've reached a space or a punctuation mark or something else that should mark the end of a word
                if second_count: # if we've been building a hyphenated word, then we actually have 3 variables, first_word (which has the part before the hyphen), second_word (which has the part after the hyphen), and word (which has the word together, but with the hyphen removed)
                    if words_by_level.has_key(lower(word)): # which of the three do we add? well, we check if our database has the whole word in it as a word. if it does, add that one.
                        words.append(lower(word))
                    else:                                   # if the big word isn't in the databse, we'll add both of the smaller words
                        if first_word != '':                # (assuming they aren't nothing)
                            words.append(lower(first_word))
                        if second_word != '':
                            words.append(lower(second_word))
                    second_count = False # then reset all the variables to their original state
                    first_word = ''
                    second_word = ''
                    word = ''
                elif word != '': # if we're not building a hyphenated word
                    words.append(lower(word)) # just add it
                    word = '' # and reset the variable

    l_name = book_name[:-4] + '_level_' + str(level) + '.csv' # a file that's going to have all the words for that level (the later passive sheet functions will read this file)
    l_writer = csv.writer(open(l_name, 'wb'), dialect = 'excel')

    already_added = [] # the words we've added to the file
    stats = {0:0,1:0,2:0,3:0,4:0,5:0,6:0} # the stats for how many words we have at each level
    for word in words: # go through each of the words in the text file (remember these are still in the order they appeared in the text)
        
        if chaptered and word == '^^^^^': # if the file is chaptered and we hit a chapter marker among the words
            ch_counter += 1 # we increment the chapter counter
            _first_ch = " Ch" + (2-len(str(ch_counter)))*'0' + str(ch_counter) # we make the current chapter into a text string
            source = source[:-5] + _first_ch # and update the source
            if not add_all: # finally, if we're not just adding everything (in which case add_words is always true)
                if ch_counter in add_words_chapters: # if the current chapter is within the range we want
                    add_words = True # then add words
                else:
                    add_words = False # otherwise don't

        if add_words: # if we're in the right chapters
            if words_by_level.has_key(word): # check the word to see if we have it in our database
                if words_by_level[word][1] >= level: # and then if the word is of an equal or greater level than our minimum level
                    if words_by_level[word][0] not in already_added: # and if it's not already added
                        _counter = str(counter) # first we're going to add a number to the word's source (this will help us keep the words sorted later)
                        _counter = '^'+(5 - len(_counter))*'0'+_counter # this is how the counter will appear: ^00005
                        _source = source + _counter # add the counter to the source
                        _row = [words_by_level[word][0], assign_date, _source] # makes the row for the document we'll upload to the passive sheet
                        already_added.append(words_by_level[word][0]) # add that word to our already added words list
                        l_writer.writerow(_row) # write the row to the .csv
                        counter += 1 # increment the counter
                        stats[words_by_level[word][1]] = stats[words_by_level[word][1]] + 1 # increment the stats counter in the appropriate level

    return l_name, assign_date, already_added, stats # send back the relevant data


# this function handles all of the passive to active sheet creation in one go. as I mentioned before, and as I explain more
# in-depth at the end of the SUMMARY file, this function takes three steps that we used to do in the old system and
# does them in a row. upload_to_sdb_passive, generate_passive_sheet and intake_passive_sheet used to be three seperate
# functions, but we eventually merged it all into one, and added book_parser. this is not efficient at all, and it wouldn't
# be too hard to make it one straightforward function, and do away with the passive databases altogether. this was just
# an easy fix given the contraints we had at the time.
def text_active_one_shot(student_name, main_name):
    teach_id = raw_input("Please enter your initials. ")

    # parse the text file, make a passive upload sheet    
    parsed_name, assign_date, temp_word_list, stats = book_parser() # these variables are: the name of the file with the words slated for passive, the assignment date, a list of the words in the first variable in a different format, and the stats
    if not parsed_name:
        return False

    # upload the passive words to the passive word list
    passive_upload_name = upload_to_sdb_passive(student_name, main_name, parsed_name, stats)
    if not passive_upload_name: 
        return False
    else: # we delete the passive_upload file at this point if we can
        try:
            os.remove(passive_upload_name)
        except WindowsError:
            print "Couldn't delete word uploading file." 

    # create a passive assignment sheet, with the temp_word_list marking which words to pre-mark for assignment
    passive_sheet_name = generate_passive_sheet(student_name, main_name, temp_word_list)

    # take in that passive sheet, with the pre-marked words, making a passive assignment from them and moving the words into the active list
    intake_passive_sheet(student_name, main_name, passive_sheet_name, assign_date, teach_id)

    return passive_sheet_name

#############################################################################################################
### ERROR CORRECTION
#
# delete_active_words(student_name)
#
#############################################################################################################

# this function deletes words from a student's active list
def delete_active_words(student_name):
    # gets the file with the words that will be deleted (just a list in the first column)
    file_name = raw_input("Enter filename of to-remove wordlist (without .csv): ")

    # opens the file
    reader = csv.reader(open(file_name, "rb"))
    to_delete = []

    # goes row by row and gets the word in the first column, appends it to a list
    for row in reader:
        to_delete.append(row[0])

    # makes a single MySQL function that deletes all the words in one go
    if len(to_delete) !=0:
        delete_command = "DELETE FROM %s WHERE " % student_name
        for word in to_delete:
            delete_command += """word = \"%s\" OR """ % MySQLdb.escape_string(word)
        delete_command = delete_command[:-3] + ';'

        # does the command
        do_test_command(delete_command)

    return

###################################################################################
### ADMIN TASKS
# indep_add_words_to_main(main_name)
# admin_tasks()
# admin_word_unlock(main_name)
###################################################################################

# this function lets you independently add words to the vocabmain database (you'll never use this)
def indep_add_words_to_main(main_name):
    while True:
        word = lower(raw_input("Enter word (* to quit): ")) # asks for words one by one
        if word == '*':
            return
        elif check_if_word_exists_in_db(word, main_name): # checks if word exists already
            print "This word is already in there."
        else: # adds it
            data = {}
            do_command("""INSERT INTO %s (word, data, lockvar) VALUES (\"%s\", \"%s\", 'False')""" % (main_name,MySQLdb.escape_string(word),MySQLdb.escape_string(str(data))))

# unlocks the main dbase
def admin_main_unlock(main_name):
    unlock_dbase(main_name)
    return

# unlocks a single word (we don't use this right now and probably won't, so I won't bother commmenting it)
def admin_word_unlock(main_name):
    while True:
        row = do_command("SELECT word FROM %s WHERE lockvar = 'True'" % main_name)
        print "Locked words:"
        counter = 1
        locked_word = []
        
        if len(row) == 0:
            print "No more locked words."
            return
        
        for word in row:
            print str(counter) + '. ' + str(word[0])
            counter += 1
            locked_word.append(str(word[0]))
            
        while True:
            word = raw_input('Enter the number of the word you wish to unlock or * to quit. ')
            if word == '*':
                return
            if int(w) in range(1,len(locked_word)+1):
                word = locked_word[int(word)-1]
                break

        unlock_word(main_name, word)

# this also won't be used. it lets us change the spelling of a word across databases (ie if you spelled 'song' with an m, you
# can use this to change all 'somg's to 'song's). This is non-trivial, and this is an imperfectly made function (a better one
#, but since now we only add words that are in the MASTER LIST file, we should never have this problem.
def admin_change_word_spelling():
    while True:
        tables = do_command("SHOW TABLES")

        old_word = raw_input("Old spelling (or * to quit): ")
        if old_word == '*':
            break
        new_word = raw_input("New spelling (or * to quit): ")
        if new_word == '*':
            break

        aff_tables = []

        for table in tables:
            table = table[0]
            if check_if_word_exists_in_db(new_word, table):
                print "This dbase has the new spelling already: " + table
            if check_if_word_exists_in_db(old_word, table):
                aff_tables.append(table)
                print "This dbase has the old spelling: " + table

        cont = raw_input("Continue (Y/N)? ")

        if lower(cont)=='y':
            for table in aff_tables:
                if check_if_word_exists_in_db(old_word, table):
                    print "Updating in " + table
                    replace_command = """UPDATE %s SET word = \"%s\" WHERE word = \"%s\"""" % (MySQLdb.escape_string(table), MySQLdb.escape_string(new_word), MySQLdb.escape_string(old_word))
                    do_command(replace_command)

    return

# this creates copies for all the tables in the database, placing them to sophos_vocab2
def admin_backup_all():
    tables = do_command("SHOW TABLES") # get all the tables

    for table in tables: # for each table
        table = table[0] # get the name
        now = datetime.datetime.now() # get the date
        date = str(now.year)+str(now.month)+str(now.day) # stringify the date
        backup_table = "sophos_vocab2.backup_" + date + "_" + table # make the name of the backup (we're assuming we're in 'sophos_vocab', hence specifying the db name)
        drop_command = "DROP TABLE IF EXISTS %s" % backup_table # delete the table if it already exists
        create_command = "CREATE TABLE %s LIKE %s" % (backup_table, table) # make the backup table
        fill_command = "INSERT %s SELECT * FROM %s" % (backup_table, table) # fill up the backup table
        do_command(drop_command) # do the commands
        do_command(create_command)
        do_command(fill_command)
        print "Backed up " + backup_table # tell the user it's been made

    return

# this function let's you fill up the dictionary table in the MySQL database for words that don't have definitions stored
# yet. here's the deal: whenever we get the definition of a word, we save it in our database for fast recall later. we're
# limited to 1000 lookups per day, so we can't just get them all at once. with some persistence though, we can get them
# before we need them. that's what this function does - it goes through our tables to find words that we haven't stored
# the definitions for (in no particular order) and looks up the definition. the function is essentially like our standard
# dictionary look-up function, so I won't repeat those parts
def admin_fillup_dict():
    dictionary_name = 'dictionary'
    api_key = "7b44ly3m8yootpmdgni4s7aprwns4l0bw5fi3j4bit"
    
    limit = 700 # max number of look-up calls to make (700 not 1000 in case you need to make a passive sheet that day)
    success = 0 # how many we looked up successfully
    failure = 0 # how many we couldn't find the definition for

    tables = do_command("SHOW TABLES") # get all the tables in db
    for table in tables: # for each table
        table = table[0] # get the table name
        if table == dictionary_name: # skip the dictionary table
            continue
        words = get_words_list(table) # get words list from the table
        dwords = get_words_list(dictionary_name) # get words list from the dictionary

        for word in words: # for each word
            if limit == 0: # if we reach our limit, get out of there
                break
            else:
                if word in dwords: # if the word is defined, skip it
                    continue
                else: # otherwise, look it up
                    print "Finding definition for: " + word
                    url = "http://api-pub.dictionary.com/v001?vid="+api_key+"&q="+word+"&type=define"
                    data = []
                    try:
                        limit = limit - 1
                        parsed = parse(urlopen(url))
                        entry_list = parsed.getElementsByTagName('entry')
                        for entry in entry_list:
                            disp_f = entry.getElementsByTagName('display_form')
                            _disp_word = str(disp_f[0].childNodes[0].nodeValue)         # this look up is standard
                            disp_word = _disp_word.replace('&middot;','')
                            pos_list = entry.getElementsByTagName('partofspeech')
                            for pos in pos_list:
                                _pos = str(pos.getAttribute('pos'))
                                defi_list = pos.getElementsByTagName('def')
                                _defi = ''
                                for defi in defi_list:
                                    try:
                                        defi_str = str(defi.childNodes[0].nodeValue)
                                    except UnicodeEncodeError:
                                        defi_uni = unicode(defi.childNodes[0].nodeValue)
                                        print defi_uni
                                        print "Unicode error, enter the correct definition."
                                        defi_str = raw_input(">> ")
                                    if _defi == '':
                                        _defi = defi_str
                                    else:
                                        _defi = _defi + "; " + defi_str
                                if _pos not in ('verb phrase','idiom'):
                                    data.append([_pos, _defi])
                                else:
                                    data.append([disp_word, _pos, _defi])
                    except:
                        print "Definition error: " + word
                        data = []
                    if data != []:
                        do_command("""INSERT INTO %s (word, data) VALUES (\"%s\", \"%s\")""" % (dictionary_name, MySQLdb.escape_string(str(word)), MySQLdb.escape_string(str(data))))
                        success += 1 # at the end, count the successes ...
                    else:
                        failure += 1 # ... and failures

    print '' 
    print "Successes: " + str(success) # print the stats
    print "Failures: " + str(failure)
    print ''

    return

# the main menu for admin tasks. very straightforward
def admin_tasks(main_name):
    while (True):
        while (True):
                print "Select an option."
                print "1. Add words independently to vocab main."
                print "2. Unlock words."
                print "3. Unlock main database."
                print "4. Change word spelling across databases."
                print "5. Backup all databases (once per day)."
                print "6. Fill-up dictionary from tables."
                print "---"
                print "*. Exit"
                option = raw_input(">>")
                if not(option in ['1','2','3','4','5','6','*']):
                    print "Invalid selection. Enter just the number of the option you want."
                else:
                    break

        if option == '1':
            indep_add_words_to_main(main_name)
        elif option == '2':
            admin_word_unlock(main_name)
        elif option == '3':
            admin_main_unlock(main_name)
        elif option == '4':
            admin_change_word_spelling()
        elif option == '5':
            admin_backup_all()
        elif option == '6':
            admin_fillup_dict()
        elif option == '*':
            break

        if lower(raw_input('Reload admin tasks? (y/n) > ')) != 'y':
            break
    return

###################################################################################
### INITIALIZATION COMMANDS
# initialization_sequence()
# select_student_db()
# check_if_db_exists(name)
# create_new_sdb(name)
###################################################################################

# this function sets up the MySQL connection
def initialization_sequence():
    main_name = "vocabmain" # the name of the main db of all the words and all the questions

    # as I mentioned earlier, we define a bunch of these global variables so that reconnecting is easier. it's
    # a very ugly solution, it works for now
    global host
    host = "www.sophosacademics.com" # our domain
    global user
    user = "sophos_vocuser" # the login name
    global sophos_password
    sophos_password = raw_input("Password: ") # the password (entered by the user)
    global db # the variable for the name of the database we're using (we have two: sophos_vocab and sophos_vocab2, the latter is used for testing and backup)
    if sophos_password[-2:] == 'dx': # a little shortcut i made for when we enter the password, if we add an extra x, it pre-unlocks a database (if you exited with an error)
        db = "sophos_vocab"
        sophos_password = sophos_password[:-1] # remove the x from the password
        pre_unlock = True
    elif sophos_password[-3:] == 'ddd': # another shortcut - an extra 'dd' at the end of the password switch to the alt database, for testing
        db = 'sophos_vocab2'
        sophos_password = sophos_password[:-2]
        pre_unlock = False
    else:
        db = "sophos_vocab" # otherwise, nothing special
        pre_unlock = False

    # two variables you need for a mysql connection. conn makes the connection and cursor, which is a function of conn, let's you send commands and receive replies
    global conn
    global cursor
    
    while True:
        try:
            conn = MySQLdb.connect(host = host, user = user, passwd = sophos_password) # make the connection
            cursor = conn.cursor() # create a cursor
            break
        except OperationalError: # if there's a problem
            print "Probably a wrong password or no internet connection or db is down." # probably one of these two things
            sophos_password = raw_input("Password or * to quit: ") # try again, or quit
            if sophos_password == '*':
                return False 

    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED") # Allow different reads based on in-moment changes
    cursor.execute("SET SESSION WAIT_TIMEOUT = 60") # Set a longer timeout, though in fact playing with this variables doesn't seem to change much
    cursor.execute("USE %s" % db) # sets the db

    if not check_if_db_exists("vocabmain"): # should never happen
        print "No main vocab."
        return False

    if pre_unlock: # if we're pre-unlocking, do that (note if the database is unlocked anyway, that won't make a problem)
        admin_main_unlock(main_name)

    return main_name

# this function asks the user to pick which student they want to work on
def pick_student_name():
    row = do_command("SHOW TABLES") # get all the tables

    dbs = []
    counter = 1

    # this is the list of students that are in the database but that are not currently active. whenever a student
    # finishes or leaves the program, they can be added here. if they come back to the program for some reason later
    # just remove them from this list. this should really be added to the database itself
    deprec_stud = []

    # this makes a list of all the selectable students, using a mechanism that should be familiar by now
    print "Current students:"
    for db in row:
        # below we make sure we're not listing the vocabmain, or any passive dbs, or any backups or anything else like that
        if str(db[0])!='vocabmain' and str(db[0][-7:])!='passive' and str(db[0][:6])!='backup' and str(db[0][0])!='*' and str(db[0]) not in deprec_stud:
            print str(counter) + '. ' + str(db[0])
            dbs.append(str(db[0]))
            counter+=1

    # gets the user input
    while True:
        db_name = raw_input('Enter student\'s number, @ for new student or * to quit. ')
        if db_name == '@': # here the user is asking to make a new student
            while True:
                new_name = raw_input('Enter the new student\'s name or * to quit. ') # enter the student's name
                if new_name in dbs or new_name == 'vocabmain' or new_name[-7:]=='passive': # if the name matches some bad criteria
                    print 'That name already exists or is illegal.' # don't allow it
                    continue
                if new_name == '*': # otherwise leave
                    return False
                else: # if we're not leaving and the name is right
                    create_new_sdb(new_name) # add the new student
                    return new_name # that's the student we're picking
        if db_name == '*': # if you want to quit
            return False
        try: # if you selected a number
            if int(db_name) in range(1,len(dbs)+1): # check that the number is a valid choice
                db_name = dbs[int(db_name)-1] # get the name associated with that number
                return db_name # return the name
        except ValueError: # otherwise, we have problem, try again
            print "Not a valid choice."
            continue

# this function checks if a particular database already exists (i.e. if you want to make sure you're not overwriting)    
def check_if_db_exists(name):
    row = do_command("SHOW TABLES")     # get all the tables
    for db in row:                      # go through each one
        if name == str(db[0]):          # if it matches
            return True                 # then it matches
    return False                        # otherwise, it don't

# this function goes through the steps of adding a new student database
def create_new_sdb(name):
    do_command("""CREATE TABLE %s (word CHAR(60), data TEXT, lockvar CHAR(60) )""" % name) ### Create the student active db
    do_command("""INSERT INTO %s (word, data, lockvar) VALUES ('__lockvar__', 'False', 'False')""" % name) # Insert the lockvar (not used currently)
    do_command("""INSERT INTO %s (word, data, lockvar) VALUES ('-----mtestcounter-----', \"['0']\", 'False')""" % name) # Insert test counters
    do_command("""INSERT INTO %s (word, data, lockvar) VALUES ('-----stestcounter-----', \"['0']\", 'False')""" % name) # for each type of test
    do_command("""INSERT INTO %s (word, data, lockvar) VALUES ('-----dtestcounter-----', \"['0']\", 'False')""" % name) # ...
    do_command("""INSERT INTO %s (word, data, lockvar) VALUES ('-----wtestcounter-----', \"['0']\", 'False')""" % name) # ...
    p_name = name + 'passive' # make the name of the passive database for the student
    do_command("""CREATE TABLE %s (word CHAR(60), data TEXT, lockvar CHAR(60) )""" % p_name) ### Create the student passive db
    do_command("""INSERT INTO %s (word, data, lockvar) VALUES ('__lockvar__', 'False', 'False')""" % p_name) ### Insert the lockvar
    do_command("""INSERT INTO %s (word, data, lockvar) VALUES ('-----ptestcounter-----', \"['0']\", 'False')""" % p_name) ### Insert test counters
    return name

###################################################################################
### RUNNING THE PROGRAM
# run_program()
###################################################################################

# the function that handles the startup sequence
def run_program():
    main_name = initialization_sequence() # makes the MySQL connection
    if not main_name: # if there was an error, quit
        return

    if locked(main_name): # check if the database is locked. if it is..
        print "Database in use. Please try again later." # tell the user
        leave = raw_input("Hit enter to quit, * to go to admin. ") # they can either quit or go to the admin to unlock it
        if leave == '*': # if *...
            admin_tasks(main_name) # go to admin
            if locked(main_name): # check if it still locked after the admin
                return # if yes, quit
            else: # otherwise..
                if db == "sophos_vocab": # if we're using the primary db, not the alternate
                    lock_dbase(main_name) # lock it
        else: # if they don't go to admin
            return # quit
    else: # if the database isn't locked
        if db == "sophos_vocab": # and we're using the primary db
            lock_dbase(main_name) # lock it
            pass

    # get the student name
    student_name = pick_student_name()
    if not student_name: # if the user wanted to quit
        unlock_dbase(main_name) # unlock the db before quitting
        return

    # present the main options menu
    while (True):
        while (True):
            print ""
            print "Select an option. (Student: " + get_student_fullname(student_name) + ")"
            print "-----------------------------------"
            print "1. Create a passive assignment from a text file."
            print "2. Generate an active testing sheet."
            print "3. Upload an active testing sheet."
            print "4. Upload a grading sheet."
            print "-----------------------------------"
            print "a. Delete a list of words from active list."
            print "b. Upload a null grading sheet."
            print "-----------------------------------"
            print "A. Upload words to active list. (word/yyyymmdd/source)"
            print "B. Upload words to passive list. (word/yyyymmdd/source)"
            print "C. Generate a passive testing sheet." 
            print "D. Upload a passive testing sheet"
            print "E. Download an answer fill-in sheet." 
            print "F. Upload answer fill-in sheet." 
            print "-----------------------------------"
            print "@. Switch student"
            print "!. Admin tasks"
            print "*. Exit"
            print "-----------------------------------"
            option = raw_input(">>")
            if not(option in ['1','2','3','4','a','b','A','B','C','D','E','F','@','!','*']):
                print "Invalid selection. Enter just the number of the option you want."
            else:
                break

        # the four main functions
        if option == '1':
            passive_sheet_name = text_active_one_shot(student_name, main_name)
            if passive_sheet_name != False: # if there wasn't an error...
                try:
                    os.remove(passive_sheet_name) # ...remove the passive_sheet file
                except WindowsError: # unless it's open (unlikely, since the user doesn't need to open the file)
                    print "You left the grading sheet open, so it wasn't deleted. Manually delete." 
        elif option == '2':
            generate_testing_sheet(student_name, main_name)
        elif option == '3':
            testsheet_name = intake_testing_sheet(student_name, main_name)
            if testsheet_name != False:
                try:
                    os.remove(testsheet_name) # same as above, remove the testsheet file if it's not open
                except WindowsError:
                    print "You left the grading sheet open, so it wasn't deleted. Manually delete." 
        elif option == '4':
            grader_name = intake_grading_sheet(student_name, main_name)
            if grader_name != False:
                try:
                    os.remove(grader_name) # ibid
                except WindowsError:
                    print "You left the grading sheet open, so it wasn't deleted. Manually delete."

        # two ancillary functions
        elif option == 'a':
            delete_active_words(student_name)
        elif option == 'b':
            grader_name = intake_null_grading_sheet(student_name, main_name)
            if grader_name != False: # if there wasn't an error
                try: # delete the grader file
                    os.remove(grader_name)
                except WindowsError: # unless it's open
                    print "You left the grading sheet open, so it wasn't deleted. Manually delete."     

        # list of the essentially deprecated functions. nothing special here
        elif option == 'A':
            upload_to_sdb(student_name, main_name)
        elif option == 'B':
            upload_to_sdb_passive(student_name, main_name)            
        elif option == 'C':
            generate_passive_sheet(student_name, main_name)
        elif option == 'D':
            intake_passive_sheet(student_name, main_name)
        elif option == 'E':
            download_answer_sheet(student_name, main_name)
        elif option == 'F':
            upload_answer_sheet(main_name)

        # let's the user pick a new student name
        elif option == '@':
            student_name = pick_student_name()
            if not student_name: # or quit if none is chosen
                unlock_dbase(main_name)
                return
        elif option == '!': # loads the admin tasks
            admin_tasks(main_name)
        elif option == '*': # quits
            break

    # once we quit, unlock the db
    unlock_dbase(main_name)
    
    try: # try closing the connection
        conn.close()
    except ProgrammingError: # though sometimes the connection won't close
        pass # in which case, cry

    return

# this runs the program
if __name__ == '__main__':
    run_program()
    print "Successful exit."
