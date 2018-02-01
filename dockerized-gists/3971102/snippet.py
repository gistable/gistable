def get_data_hardread(self, ts_list, symbol_list, data_item, verbose=False, bIncDelist=False):
        '''
        Read data into a DataFrame no matter what.
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param bIncDelist: If true, delisted securities will be included.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then 
        continues as usual. No errors are raised at the moment.
        '''
        
        ''' Now support lists of items, still support old string behaviour '''
        bStr = False
        if( isinstance( data_item, str) ):
            data_item = [data_item]
            bStr = True
        
        
        # init data struct - list of arrays, each member is an array corresponding do a different data type
        # arrays contain n rows for the timestamps and m columns for each stock
        all_stocks_data = []
        for i in range( len(data_item) ):
            all_stocks_data.append( np.zeros ((len(ts_list), len(symbol_list))) );
            all_stocks_data[i][:][:] = np.NAN
        
        list_index= []
        
        ''' For each item in the list, add to list_index (later used to delete non-used items) '''
        for sItem in data_item:
            if( self.source == DataSource.CUSTOM ) :
                ''' If custom just load what you can '''
                if (sItem == DataItem.CLOSE):
                    list_index.append(1)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(2)
            if( self.source == DataSource.COMPUSTAT ):
                ''' If compustat, look through list of features '''
                for i, sLabel in enumerate(DataItem.COMPUSTAT):
                    if sItem == sLabel:
                        ''' First item is date index, labels start at 1 index '''
                        list_index.append(i+1)
                        break
                else:
                    raise ValueError ("Incorrect value for data_item %s"%sItem)
            
            if( self.source == DataSource.NORGATE ):
                if (sItem == DataItem.OPEN):
                    list_index.append(1)
                elif (sItem == DataItem.HIGH):
                    list_index.append (2)
                elif (sItem ==DataItem.LOW):
                    list_index.append(3)
                elif (sItem == DataItem.CLOSE):
                    list_index.append(4)
                elif(sItem == DataItem.VOL):
                    list_index.append(5)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(6)
                else:
                    #incorrect value
                    raise ValueError ("Incorrect value for data_item %s"%sItem)
                
            if( self.source == DataSource.YAHOOold ):
                if (sItem == DataItem.OPEN):
                    list_index.append(1)
                elif (sItem == DataItem.HIGH):
                    list_index.append (2)
                elif (sItem ==DataItem.LOW):
                    list_index.append(3)
                elif (sItem == DataItem.CLOSE):
                    list_index.append(4)
                elif(sItem == DataItem.VOL):
                    list_index.append(5)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(6)
                else:
                    #incorrect value
                    raise ValueError ("Incorrect value for data_item %s"%sItem)

            if( self.source == DataSource.MLT or self.source == DataSource.YAHOO):
                if (sItem == DataItem.OPEN):
                    list_index.append(1)
                elif (sItem == DataItem.HIGH):
                    list_index.append (2)
                elif (sItem ==DataItem.LOW):
                    list_index.append(3)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(4)
                elif(sItem == DataItem.VOL):
                    list_index.append(5)
                elif (sItem == DataItem.CLOSE):
                    list_index.append(6)
                else:
                    #incorrect value
                    raise ValueError ("Incorrect value for data_item %s"%sItem)
                #end elif
        #end data_item loop

        #read in data for a stock
        symbol_ctr=-1
        for symbol in symbol_list:
            _file = None
            symbol_ctr = symbol_ctr + 1
            #print self.getPathOfFile(symbol)
            try:
                if (self.source == DataSource.CUSTOM) or (self.source == DataSource.MLT)or (self.source == DataSource.YAHOO):
                    file_path= self.getPathOfCSVFile(symbol);
                else:
                    file_path= self.getPathOfFile(symbol);
                
                ''' Get list of other files if we also want to include delisted '''
                if bIncDelist:
                    lsDelPaths = self.getPathOfFile( symbol, True )
                    if file_path == None and len(lsDelPaths) > 0:
                        print 'Found delisted paths:', lsDelPaths
                
                ''' If we don't have a file path continue... unless we have delisted paths '''
                if (type (file_path) != type ("random string")):
                    if bIncDelist == False or len(lsDelPaths) == 0:
                        continue; #File not found
                
                if not file_path == None: 
                    _file = open(file_path, "rb")
            except IOError:
                # If unable to read then continue. The value for this stock will be nan
                print _file
                continue;
                
            assert( not _file == None or bIncDelist == True )
            ''' Open the file only if we have a valid name, otherwise we need delisted data '''
            if _file != None:
                if (self.source==DataSource.CUSTOM) or (self.source==DataSource.YAHOO)or (self.source==DataSource.MLT):
                    creader = csv.reader(_file)
                    row=creader.next()
                    row=creader.next()
                    #row.pop(0)
                    for i, item in enumerate(row):
                        if i==0:
                            try:
                                date = dt.datetime.strptime(item, '%Y-%m-%d')
                                date = date.strftime('%Y%m%d')
                                row[i] = float(date)
                            except:
                                date = dt.datetime.strptime(item, '%m/%d/%y')
                                date = date.strftime('%Y%m%d')
                                row[i] = float(date)
                        else:
                            row[i]=float(item)
                    naData=np.array(row)
                    for row in creader:
                        for i, item in enumerate(row):
                            if i==0:
                                try:
                                    date = dt.datetime.strptime(item, '%Y-%m-%d')
                                    date = date.strftime('%Y%m%d')
                                    row[i] = float(date)
                                except:
                                    date = dt.datetime.strptime(item, '%m/%d/%y')
                                    date = date.strftime('%Y%m%d')
                                    row[i] = float(date)
                            else: 
                                row[i]=float(item)
                        naData=np.vstack([np.array(row),naData])
                else:
                    naData = pkl.load (_file)
                _file.close()
            else:
                naData = None
                
            ''' If we have delisted data, prepend to the current data '''
            if bIncDelist == True and len(lsDelPaths) > 0 and naData == None:
                for sFile in lsDelPaths[-1:]:
                    ''' Changed to only use NEWEST data since sometimes there is overlap (JAVA) '''
                    inFile = open( sFile, "rb" )
                    naPrepend = pkl.load( inFile )
                    inFile.close()
                    
                    if naData == None:
                        naData = naPrepend
                    else:
                        naData = np.vstack( (naPrepend, naData) )
                        
            #now remove all the columns except the timestamps and one data column
            if verbose:
                print self.getPathOfFile(symbol)
            
            ''' Fix 1 row case by reshaping '''
            if( naData.ndim == 1 ):
                naData = naData.reshape(1,-1)
                
            #print naData
            #print list_index
            ''' We open the file once, for each data item we need, fill out the array in all_stocks_data '''
            for lLabelNum, lLabelIndex in enumerate(list_index):
                
                ts_ctr = 0
                b_skip = True
                
                ''' select timestamps and the data column we want '''
                temp_np = naData[:,(0,lLabelIndex)]
                
                #print temp_np
                
                num_rows= temp_np.shape[0]

                
                symbol_ts_list = range(num_rows) # preallocate
                for i in range (0, num_rows):

                    timebase = temp_np[i][0]
                    timeyear = int(timebase/10000)
                    
                    # Quick hack to skip most of the data
                    # Note if we skip ALL the data, we still need to calculate
                    # last time, so we know nothing is valid later in the code
                    if timeyear < ts_list[0].year and i != num_rows - 1:
                        continue
                    elif b_skip == True:
                        ts_ctr = i
                        b_skip = False
                    
                    
                    timemonth = int((timebase-timeyear*10000)/100)
                    timeday = int((timebase-timeyear*10000-timemonth*100))
                    timehour = 16
    
                    #The earliest time it can generate a time for is platform dependent
                    symbol_ts_list[i]=dt.datetime(timeyear,timemonth,timeday,timehour) # To make the time 1600 hrs on the day previous to this midnight
                    
                #for ends
    
    
                #now we have only timestamps and one data column
                
                
                #Skip data from file which is before the first timestamp in ts_list
    
                while (ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr] < ts_list[0]):
                    ts_ctr=  ts_ctr+1
                    
                    #print "skipping initial data"
                    #while ends
                
                for time_stamp in ts_list:
                    
                    if (symbol_ts_list[-1] < time_stamp):
                        #The timestamp is after the last timestamp for which we have data. So we give up. Note that we don't have to fill in NaNs because that is 
                        #the default value.
                        break;
                    else:
                        while ((ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr]< time_stamp)):
                            ts_ctr = ts_ctr+1
                            #while ends
                        #else ends
                                            
                    #print "at time_stamp: " + str(time_stamp) + " and symbol_ts "  + str(symbol_ts_list[ts_ctr])
                    
                    if (time_stamp == symbol_ts_list[ts_ctr]):
                        #Data is present for this timestamp. So add to numpy array.
                        #print "    adding to numpy array"
                        if (temp_np.ndim > 1): #This if is needed because if a stock has data for 1 day only then the numpy array is 1-D rather than 2-D
                            all_stocks_data[lLabelNum][ts_list.index(time_stamp)][symbol_ctr] = temp_np [ts_ctr][1]
                        else:
                            all_stocks_data[lLabelNum][ts_list.index(time_stamp)][symbol_ctr] = temp_np [1]
                        #if ends
                        
                        ts_ctr = ts_ctr +1
                    
                #inner for ends
            #outer for ends
        #print all_stocks_data
        
        ldmReturn = [] # List of data matrixes to return
        for naDataLabel in all_stocks_data:
            ldmReturn.append( pa.DataFrame( naDataLabel, ts_list, symbol_list) )            

        
        ''' Contine to support single return type as a non-list '''
        if bStr:
            return ldmReturn[0]
        else:
            return ldmReturn            
        
        #get_data_hardread ends
