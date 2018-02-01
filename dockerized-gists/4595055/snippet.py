#!/usr/bin/env python                                                                                                       
                                                                                
import os                                                                       
import json                                                                     
                                                                                
import grooveshark                                                              
                                                                                
client = grooveshark.Client()                                                   
client.init()                                                                   
                                                                                
def update(check_favorites=False):                                              
    user_id = 6494265                                                           
    if check_favorites:                                                         
        collection = client.favorites(user_id)                                  
        dir = '~/Music/favorites'                                               
    else:                                                                       
        collection = client.collection(user_id)                                 
        dir = '~/Music/collection'                                              
                                                                                
    dir = os.path.expanduser(dir)                                               
    try:                                                                        
        os.makedirs(dir)                                                        
    except OSError:  # if the directory already exists                          
        pass                                                                    
                                                                                
    try:                                                                        
        with open(dir + '/grooveshark.json') as f:                              
            index = json.load(f)                                                
    except IOError:  # if the file doesn't yet exist                            
        index = {}                                                              
                                                                                
    def writeout():                                                             
        with open(dir + '/grooveshark.json', 'w') as f:                         
            json.dump(index, f)                                                 
                                                                                
    print('Sum: ', len(collection))                                             
    for song in collection:                                                     
        print(song)                                                             
        if song.id not in index:                                                
            song.download(dir)                                                  
            content = song.export()                                             
            index[content['id']] = content                                      
            del content['id']                                                   
            # always write out after every song, so that no information can be lost
            writeout()                                                          
                                                                                
update(True)                                                                    
update(False)