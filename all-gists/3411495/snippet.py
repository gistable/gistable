#Uploaded in response to query on psychopy list: https://groups.google.com/group/psychopy-users/browse_thread/thread/c65e453edf530f8
#asking for code to input a string. 
#Program flashes string on screen, and user tries to type it in. Supports backspace but no other editing special characters.
#Checks whether subject got it right
#Alex Holcombe alex.holcombe@sydney.edu.au  21 August 2012
#licensing: CC-BY whch means do whatever you want with it, with an attribution to the author. If you want permission to use it without 
#attribution, just contact me.

from psychopy import monitors, visual, event, data, logging, core, sound, gui
import psychopy.info
import numpy as np
from math import atan
from copy import deepcopy
import time
import sys, os

refreshRate=60
autopilot=False
subject='Hubert' 
if autopilot: subject='auto'
if os.path.isdir('.'+os.sep+'data'):
    dataDir='data'
else:
    print '"data" directory does not exist, so saving data in present working directory'
    dataDir='.'
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())

showRefreshMisses=True #flicker fixation at refresh rate, so visualize missed frames
feedback=True 
autoLogging=False

bgColor = [-1.,-1.,-1.] # [-1,-1,-1]
letterColor = [1.,1.,1.]
#letter size 2.5 deg
numLettersToPresent = 4
letterDurMs = 350 #23.6  
letterDurFrames = int( np.floor(letterDurMs / (1000./refreshRate)) )
trialDurFrames = letterDurFrames

widthPix=1024 #monitor width in pixels
heightPix=768 #monitor height in pixels
monitorwidth = 38.7 #Lizzie reports that they have an ultrawide screen of 51x29.  38.7 is what the width *would* be if they had a standard aspect ratio.   #monitor width in centimeters
fullscr=1; 
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
allowGUI = False

viewdist = 57.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
print 'pixelperdegree=',pixelperdegree

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'
myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
#HAVE TO CLOSE WINDOW, AND THEN OPEN IT AGAIN
 
#check screen refresh is what assuming it is ########################################################################
Hzs=list()
myWin.flip(); myWin.flip();myWin.flip();myWin.flip();
myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
for i in range(50):
    myWin.flip()
    Hzs.append( myWin.fps() )  #varies wildly on successive runs!
myWin.setRecordFrameIntervals(False)
# end testing of screen refresh########################################################################
Hzs = np.array( Hzs );     Hz= np.median(Hzs)
msPerFrame= 1000./Hz
refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
refreshRateWrong = abs( (np.median(Hzs)-refreshRate) / refreshRate) > .05
refreshMsg2 = ''
if refreshRateWrong:
    refreshMsg2 = ' BUT'
refreshMsg2 += ' program assumes refreshRate= ' + str(refreshRate)
refreshMsg3 = ' '
if refreshRateWrong:
   refreshMsg3=  ' which is off by more than 5% !!'
else:
   refreshMsg3= ' which is close enough for an RSVP experiment'

myWinRes = myWin.size

trialsPerCondition = 1 #default value

#set up output data file, log file,  copy of program code, and logging
fileName = dataDir+'/'+subject+'_'+timeAndDateStr
dataFile = open(fileName+'.txt', 'w')  # sys.stdout  
saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
logFname = fileName+'.log'
ppLogF = logging.LogFile(logFname, 
    filemode='w',#if you set this to 'a' it will append instead of overwriting
    level=logging.INFO)#errors, data and warnings will be sent to this logfile
logging.console.setLevel(logging.WARNING) #DEBUG means set the console to receive nearly all messges, INFO is for everything else, INFO, EXP, DATA, WARNING and ERROR 

runInfo = psychopy.info.RunTimeInfo(
    # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
    #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
    #version="<your experiment version info>",
    win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
    refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
    verbose=False, ## True means report on everything 
    userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
    #randomSeed='set:42', ## a way to record, and optionally set, a random seed of type str for making reproducible random sequences
        ## None -> default 
        ## 'time' will use experimentRuntime.epoch as the value for the seed, different value each time the script is run
        ##'set:time' --> seed value is set to experimentRuntime.epoch, and initialized: random.seed(info['randomSeed'])
        ##'set:42' --> set & initialize to str('42'), and will give the same sequence of random.random() for all runs of the script
    )
logging.info(runInfo)
logging.flush()

#create click sound for keyboard
try:
    click=sound.Sound('406__tictacshutup__click-1-d.wav')
except: #in case file missing, create inferiro click manually
    logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
    click=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)

stimList = []
possibleStrings = np.array([ 'HECK','ABCD','JUMP','RUMP','CAT','DUMPSTER' ]) # [4,10,16,22] used in Martini E2, group 2
maxNumRespsWanted = 0
for stim in possibleStrings: #calculate longest one
    maxNumRespsWanted = max(maxNumRespsWanted, len(stim))
    
for stim in possibleStrings:  #set up the  trial conditions in the experiment
        stimList.append( {'stim':stim} )
        
trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method

logging.info( 'numtrials=' + str(trials.nTotal) + ' and each trialDurFrames='+str(trialDurFrames)+' or '+str(trialDurFrames*(1000./refreshRate))+ \
               ' ms' )
print ' numtrials=', trials.nTotal; 

def numberToLetter(number): #0 = A, 25 = Z
    #if it's not really a letter, return @
    #if type(number) != type(5) and type(number) != type(np.array([3])[0]): #not an integer or numpy.int32
    #    return ('@')
    if number < 0 or number > 25:
        return ('@')
    else: #it's probably a letter
        try:
            return chr( ord('A')+number )
        except:
            return('@')

def letterToNumber(letter): #A = 0, Z = 25
    #if it's not really a letter, return -999
    #HOW CAN I GENERICALLY TEST FOR LENGTH. EVEN IN CASE OF A NUMBER THAT' SNOT PART OF AN ARRAY?
    try:
        #if len(letter) > 1:
        #    return (-999)
        if letter < 'A' or letter > 'Z':
            return (-999)
        else: #it's a letter
            return ord(letter)-ord('A')
    except:
        return (-999)


#print header for data file
print >>dataFile, 'trialnum\tsubject\ttask\t',
for i in range(maxNumRespsWanted):
   dataFile.write('answer'+str(i)+'\t')
   dataFile.write('response'+str(i)+'\t')
   dataFile.write('correct'+str(i)+'\t')
print >>dataFile, 'timingBlips'
#end of header

def collectResponses(passThisTrial,numRespsWanted,responses,responsesAutopilot,expStop,responseDebug=False): 
    respStr = ''
    responses=[]
    numResponses = 0
    while numResponses < numRespsWanted and not expStop:
        #print 'numResponses=', numResponses #debugOFF
        noResponseYet=True
        thisResponse = ''
        while noResponseYet: #collect one response
               respPromptText.draw()
               #respStr= 'Y'
               #print 'respStr = ', respStr, ' type=',type(respStr) #debugOFF
               respText.setText(respStr)
               respText.draw()
               myWin.flip()
               for key in event.getKeys():       #check if pressed abort-type key
                      key = key.upper()
                      thisResponse = key
                      if key in ['ESCAPE']:
                          expStop = True
                          noResponseYet = False
                      if key in ['BACKSPACE']:
                          if len(responses) >0:
                                responses.pop()
                                numResponses -= 1
                                #refresh text to draw
                                respStr = ''.join(responses) #converts list of characters (responses) into string
                      if key in ['SPACE']: #observer opting out because think they moved their eyes
                          passThisTrial = True
                          noResponseYet = False
                      if key in ['A', 'C', 'B', 'E', 'D', 'G', 'F', 'I', 'H', 'K', 'J', 'M', 'L', 'O', 'N', 'Q', 'P', 'S', 'R', 'U', 'T', 'W', 'V', 'Y', 'X', 'Z']:
                          noResponseYet = False
               if autopilot:
                   noResponseYet=False
        #click to provide feedback that response collected. Eventually, draw on screen
        click.play()
        if thisResponse or autopilot:
            responses.append(thisResponse)
            numResponses += 1 #not just using len(responses) because want to work even when autopilot, where thisResponse is null
        respStr = ''.join(responses) #converts list of characters (responses) into string
        #print 'responses=',responses,' respStr = ', respStr #debugOFF
        respText.setText(respStr); respText.draw(); myWin.flip() #draw again, otherwise won't draw the last key
        
    responsesAutopilot = np.array(   numRespsWanted*list([letterToNumber('A')])        )
    responses=np.array( responses )
    #print 'responses=', responses,' responsesAutopilot=', responsesAutopilot #debugOFF
    return passThisTrial,responses,responsesAutopilot,expStop
# ###### #End of function definition that collects responses!!!! #####################################
#############################################################################################################################
respText = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=.16,units='norm',autoLog=autoLogging)
respPromptText = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
strStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
strStim.setHeight( 2.5 ) #Martini letters were 2.5deg high

trialClock = core.Clock()
nDone=0; numTrialsCorrect=0; expStop=False; framesSaved=0
while nDone < trials.nTotal and expStop==False:
    thisTrial = trials.next()
    strToDisplay = thisTrial['stim'] #connect to letter sequence or delete letter sequence
    strStim.setText( strToDisplay )
    correctAnswer = strToDisplay

    preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I have consistent timing blip first time that draw ringInnerR for phantom contours
    for stim in preDrawStimToGreasePipeline:
        stim.draw()
    myWin.flip(); myWin.flip()
    #end preparation of stimuli
    
    core.wait(.1);
    trialClock.reset()
    fixatnPeriodMin = 0.3
    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+fixatnPeriodMin)   *refreshRate)  #random interval between 800ms and 1.3s (changed when Fahed ran outer ring ident)
    ts = list(); #to store time of each drawing, to check whether skipped frames
    for i in range(fixatnPeriodFrames+20):  #prestim fixation interval
        myWin.flip()  #end fixation interval
    t0=trialClock.getTime();
    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
        strStim.draw()
        myWin.flip()
        
    t=trialClock.getTime()-t0;  ts.append(t);
    #end of big stimulus loop
    myWin.setRecordFrameIntervals(False);
    #check for timing problems
    interframeIntervs = np.diff(ts)*1000
    #print '   interframe intervs were ',around(interframeIntervs,1) #DEBUGOFF
    frameTimeTolerance=.3 #proportion longer than refreshRate that will not count as a miss
    longFrameLimit = np.round(1000/refreshRate*(1.0+frameTimeTolerance),2)
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded 150% of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0 :
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                logging.error( 'trialnum='+str(nDone)+' '+longFramesStr )
                flankingAlso=list()
                for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                    if idx-1>=0:  flankingAlso.append(idx-1)
                    else: flankingAlso.append(np.NaN)
                    flankingAlso.append(idx)
                    if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                    else: flankingAlso.append(np.NaN)
                flankingAlso = np.array(flankingAlso)
                flankingAlso = flankingAlso[np.negative(np.isnan(flankingAlso))]  #remove nan values
                flankingAlso=flankingAlso.astype(np.integer) #cast as integers, so can use as subscripts
                logging.error( 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) )  )
    #end timing check
    passThisTrial=False
    respPromptText.setText('Type the string')
 
    responseDebug=False
    responses = list(); responsesAutopilot = list(); passThisTrial=False
    numRespsWanted = len(correctAnswer)
    passThisTrial,responses,responsesAutopilot,expStop = \
                  collectResponses(passThisTrial,numRespsWanted,responses,responsesAutopilot,expStop,responseDebug)  #collect responses!!!!!!!!!
    #############################################################################################
    core.wait(.1)
    #Handle response, calculate whether correct, ########################################
    if expStop:
        responses =np.array([-999])  #because otherwise responses can't be turned into array if have partial response
    if autopilot or passThisTrial:
        responses = responsesAutopilot;  #print 'assigning responses to responsesAutopilot, = ', responsesAutopilot
    
    eachCorrect = np.zeros( len(correctAnswer) )    
    print 'correctAnswer=',correctAnswer, '    responses = ',responses
    
    if expStop:
        pass
    else:
        for i in range(len(correctAnswer)):
            if correctAnswer[i] == responses[i]:
                eachCorrect[i] = 1
            # logging.warn('Response was not present in the stimulus stream')

        print 'eachCorrect = ',eachCorrect
        print 'overall correct=',eachCorrect.all()
    
        #header start  'trialnum\tsubject\ttask\t'
        print >>dataFile, nDone,'\t',subject,'\t',
        for i in range(len(correctAnswer)):
            print >>dataFile, eachCorrect[i] , '\t',    #correct0, correct1, etc
        print >>dataFile, eachCorrect.all()
        #timingBlips
        print >>dataFile, numCasesInterframeLong
    
        numTrialsCorrect += eachCorrect.all() #so count -1 as 0
        #numRightWrongEachSpeedIdent[ speedIdx, (numColorsCorrectlyIdentified==3) ] +=1
        if feedback:
            high = sound.Sound('G',octave=5, sampleRate=6000, secs=.3, bits=8)
            low = sound.Sound('F',octave=4, sampleRate=6000, secs=.3, bits=8)
            high.setVolume(0.9)
            low.setVolume(0.9)
            if eachCorrect.all():
                high.play()
            elif passThisTrial:
                high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08, bits=8)
                for i in range(2): 
                    high.play();  low.play(); 
            else: #incorrect
                low.play()
        nDone+=1
    
    dataFile.flush(); logging.flush()
    #print 'nDone=', nDone,' trials.thisN=',trials.thisN,' trials.nTotal=',trials.nTotal
    core.wait(.2); time.sleep(.2)
    #end trials loop
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())
msg = 'finishing at '+timeAndDateStr
print msg;  logging.info(msg)
if expStop:
    msg = 'user aborted experiment on keypress with trials nDone='+ str(nDone) + ' of ' + str(trials.nTotal+1)
    print msg; logging.error(msg)

proportnCorrectMsg = '%corr= ',numTrialsCorrect*1.0/nDone*100., '% of ',nDone,' trials'
print '%corr= ',numTrialsCorrect*1.0/nDone*100., '% of ',nDone,' trials'
   #print 'breakdown by speed: ',
   #print numRightWrongEachSpeedOrder[:,1] / ( numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1])   
#contents = dataFile.getvalue(); print contents
#contents = logF.getvalue(); print contents
logging.flush(); dataFile.close()
