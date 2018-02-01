import os, os.path, shutil, errno
import datetime

# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

BAND_FOLDER = "c:\\users\\cameron\\downloads\\the band folder"
INPUT_PATH = os.path.join(BAND_FOLDER, "raw")
OUTPUT_PATH = "c:\\users\\cameron\\dropbox\\demos"
PROJECT_PATH = os.path.join(OUTPUT_PATH, "template.rpp")
REAPER_PATH = "c:\\Program Files (x86)\\REAPER\\reaper.exe"

# IMPORTANT: this must match the RENDER_FILE variable in template.rpp
COMMON_OUTPUT_PATH = "c:\\rendertemp.mp3"

RPR_Main_openProject(PROJECT_PATH)

roomTrack = RPR_GetTrack(0, 0)
snareTomTrack = RPR_GetTrack(0, 1)
kickTrack = RPR_GetTrack(0, 2)

# files are named 4CH\d{3}[IM].wav
files = [] # tuples, i.e. [("003", mfile, ifile), ("004", mfile, ifile), ...]
for i in range(1000):

    num = str(i).zfill(3) # e.g. 7 --> "007"
    mfile = os.path.join(INPUT_PATH, "4CH" + num + "M.wav")
    ifile = os.path.join(INPUT_PATH, "4CH" + num + "I.wav")
    
    if os.path.exists(mfile) and os.path.exists(ifile):
        files.append((num, mfile, ifile))              

# configure our output path
datedir = datetime.date.today().strftime("%a %b %d %Y")
demo_dir = os.path.join(OUTPUT_PATH, datedir)
mkdir_p(demo_dir)

def rewind():
    RPR_SetEditCurPos(0, False, False)

def setActiveTrack(track):
    """ set an exclusively-selected track """
    for i in range(RPR_GetNumTracks()):
        RPR_SetTrackSelected(RPR_GetTrack(0, i), 0)
    RPR_SetTrackSelected(track, 1)

def clearTrack(track):
    for i in reversed(range(RPR_GetTrackNumMediaItems(track))):
        RPR_DeleteTrackMediaItem(track, RPR_GetTrackMediaItem(track, i))

def setTrackAsFile(f, track):        
    """ add the file to the start of a given track, remove all other media items """
    clearTrack(track)
    rewind()
    setActiveTrack(track)
    RPR_InsertMedia(f, 0) # 0 = create a media item too

def findTrackItem(track, n):
    count = RPR_CountMediaItems(0)
    found_index = 0    
    for i in range(count):
        item = RPR_GetMediaItem(0, i)
        item_track = RPR_GetMediaItem_Track(item)
        if item_track == track:
            if found_index == n:
                return item
            found_index += 1
    return None                          
    
# go through each pair of recording files and render them
for num, roomFile, externalFile in files:
    	
    setTrackAsFile(roomFile, roomTrack)

    setTrackAsFile(externalFile, snareTomTrack)
    snareTomItem = findTrackItem(snareTomTrack, 0)
    snareTomTake = RPR_GetMediaItemTake(snareTomItem, 0)
    RPR_SetMediaItemTakeInfo_Value(snareTomTake, "I_CHANMODE", 3) # 3 = left only

    setTrackAsFile(externalFile, kickTrack)
    kickItem = findTrackItem(kickTrack, 0)
    kickTake = RPR_GetMediaItemTake(kickItem, 0)    
    RPR_SetMediaItemTakeInfo_Value(kickTake, "I_CHANMODE", 4) # 4 = right only    

    # save the project
    RPR_Main_OnCommand(40026, 0)

    # render the file by calling reaper on the command line
    import subprocess   
    subprocess.check_output([REAPER_PATH, "-renderproject", PROJECT_PATH])
    
    # move to where we want the file    
    final_path = os.path.join(demo_dir, num + ".mp3")
    shutil.move(COMMON_OUTPUT_PATH, final_path)

    