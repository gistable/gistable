import sys, time, datetime
from copy import copy, deepcopy
from collections import OrderedDict
import string
import math
import win32com.client
import traceback

# Sample code for accessing MSProject
# 2014 (C) Zohar Lorberbaum

debug = False

def proj2time(t):
    """Convert MSProject time to Python time"""
    return time.mktime(time.strptime(t.Format('%m/%d/%y %H:%M:%S'), '%m/%d/%y %H:%M:%S'))

def expectedProgress(start, finish, t=None):
    """Get expected percent progress given start, finish, and point t in time (in seconds since the Epoch).
    If t is not defined, use current time (now)."""
    s = proj2time(start)
    f = proj2time(finish)
    if not t: t = time.time()
    if t<=s:
        return 0
    elif t>f:
        return 100
    else:
        p = int( (t-s)/(f-s)*100.0 ) # linear task progress
        return p

def expectedWork(etotal, estart, efinish, t):
    """Get expected work progress given total work, start, finish, and point t in time (in seconds since the Epoch)."""
    if t<=estart:
        return 0.0
    elif t>efinish:
        return float(etotal)
    else:
        p = float(etotal)*(t-estart)/(efinish-estart) # linear task progress
        return p

def expectedWork2(etotal, estart, efinish, t):
    """Heuristic expected percent progress given start, finish, and point t in time (in seconds since the Epoch).
    If t is not defined, use current time (now)."""
    if t<=estart:
        return 0.0
    elif t>efinish:
        return float(etotal)
    else:
        a1 = 4.0
        a2 = 2.0
        a3 = -1.0
        c1 = 1.0
        c2 = 3.0
        c3 = 9.0
        f1 = 100.0*(t-estart)/(efinish-estart)
        f2 = math.sin(c1*math.pi*(t-estart)/(efinish-estart))
        f3 = f1-a1*f2
        f4 = math.sin(c2*math.pi*(t-estart)/(efinish-estart))
        f5 = f3-a2*f4
        f6 = math.sin(c3*math.pi*(t-estart)/(efinish-estart))
        f7 = f5-a3*f6
        f0 = 0.0-a1*f2-a2*f4-a3*f6
        p = float( etotal*f7/100.0 ) # variable task progress
        return p

class MSProject:
    """MSProject class."""
    def __init__(self):
        self.mpp = win32com.client.Dispatch("MSProject.Application")
        self.Project = None
        self._Tasks = None
        if debug: self.mpp.Visible = 1
        return

    def __call__(self):
        print 'MSProject call'
        return

    def __getattr__(self,attr):
        if attr == 'Tasks':
            #if not self.__dict__.has_key('_Tasks'):
            if not self._Tasks:
                if not self.__dict__.has_key('Project'):
                    print "You have to load a file first."
                    raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))
                else:
                    self._Tasks=Tasks(self.mpp, self.Project)
            return self._Tasks
        else:
            raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))

    def __repr__(self):
        return "MSProject class"

    def __dir__(self):
        d=['Tasks']
        d += self.__dict__.keys()
        d += self.__class__.__dict__.keys()
        return d

    def load(self, doc):
        """Load a given MSProject file."""
        try:
            self.mpp.FileOpen(doc)
            self.Project = self.mpp.ActiveProject
            return True
        except Exception, e:
            print "Error opening file",e
            return False

    def saveAndClose(self):
        """Close an open MSProject, saving changes."""
        if self.__dict__.has_key('Project'):
            self.mpp.FileSave()
        self.mpp.Quit()
        return

    def dump(self):
        """Dump file contents, for debugging purposes."""
        if not self.__dict__.has_key('Project'):
            print "No project file is open. Use 'open' command first."
            return False
        try:
            print "This project has ", str(self.Project.Tasks.Count), " Tasks"
            for i in range(1,self.Project.Tasks.Count+1):
                print i,
                try:
                    print self.Project.Tasks.Item(i).Name[:60].encode('ascii', 'ignore'),
                    print self.Project.Tasks.Item(i).Text1.encode('ascii', 'ignore'), # Custom field
                    print self.Project.Tasks.Item(i).ResourceNames.encode('ascii', 'ignore'),
                    print self.Project.Tasks.Item(i).Start,
                    print self.Project.Tasks.Item(i).Finish,
                    print self.Project.Tasks.Item(i).PercentWorkComplete,
                    print '%'
                except:
                    print 'Empty'
            return True
        except Exception, e:
            print "Error:", e
            return False


class Tasks(object):
    """Class to hold task lines in MSProject.
    Access to items is via Accept360 S/N."""
    def __init__(self, mpp, Project):
        self.mpp = mpp
        self.Project = Project
        self._Tasks = None
        self._RFQAs = None
        self._compoundTask = None
        self._unknowns = None
        self._msfields = ['Name', 'Resources', 'Start', 'Finish', 'PercentWorkComplete', 'Priority', 'ReleaseName']
        return

    def __repr__(self):
        if self._Tasks:
            return 'Requirements: '+str(self._Tasks.keys())
        else:
            return 'Please load a file and get tasks first.'

    def __dir__(self):
        l = self.__class__.__dict__.keys() + self.__dict__.keys()
        if self._Tasks:
            for k in self._Tasks.keys():
                l.append('SN'+str(k))
            l.remove('_Tasks')
        return l

    def __call__(self, *args, **kargs):
        if kargs:
            if kargs.has_key('SN'):
                if self._Tasks:
                    if self._Tasks.has_key(kargs['SN']):
                        return self._Tasks[kargs['SN']]
            else:
                print 'No requirements were retreived from server yet.\nPlease perform a parsed query.'
                return None
        elif args:
            if self._Tasks:
                if len(args)>0:
                    for arg in args:
                        if arg[:2]=='SN':
                            if self._Tasks.has_key(arg[2:]):
                                return self._Tasks[arg[2:]]
                        else:
                            if self._Tasks.has_key(arg):
                                return self._Tasks[arg]
                        print str(arg) + ' was not found'
                    return None
            else:
                print 'Please load a file and get tasks first.'
                return None
        else:
            if not self._Tasks:
                self.getTasks()
            return self._Tasks

    def __getattr__(self,attr):
        if attr == 'Tasks':
            if not self._Tasks:
                self.getTasks()
            return self._Tasks
        elif self.__dict__.has_key(attr):
            return self.__dict__[attr]
        elif self._Tasks:
            if len(attr)>2:
                if attr[:2]=='SN':
                    if self._Tasks.has_key(attr[2:]):
                        return self._Tasks[attr[2:]]
                else:
                    if self._Tasks.has_key(attr):
                        return self._Tasks[attr]
            if attr in self._compoundTask.keys():
                return self._compoundTask[attr]['id']
        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))

    def __getitem__(self, attr):
        if attr == 'Tasks':
            if not self._Tasks:
                self.getTasks()
            return self._Tasks
        elif self.__dict__.has_key(attr):
            return self.__dict__[attr]
        elif self._Tasks:
            if len(attr)>2:
                if attr[:2]=='SN':
                    if self._Tasks.has_key(attr[2:]):
                        return self._Tasks[attr[2:]]
                else:
                    if self._Tasks.has_key(attr):
                        return self._Tasks[attr]
            if attr in self._compoundTask.keys():
                return self._compoundTask[attr]['id']
            return str(attr) + ' was not found'
        else:
            raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))


    def getTasks(self):
        """Return all tasks that have a value in the 'Accept360 S/N' field and have a resource assigned."""
        self._Tasks = dict()
        self._RFQAs = dict()
        self._compoundTask = dict()
        self._unknowns = dict()
        if not self.__dict__.has_key('Project'):
            print "No project file is open. Use 'open' command first."
            return False
        # Get all MSProject tasks: for duplicate 'Accept360' fields - update Start, End, Resource, PercentWorkComplete accordingly
        try:
            for i in range(1,self.Project.Tasks.Count+1):
                try:
                    task = False
                    rfqa = False
                    Py = self.Project.Tasks.Item(i).Text4 # Helper column to allow ignoring lines.
                    if Py.lower()!='ignore':
                        SN = self.Project.Tasks.Item(i).Text1 # A custom column to store unique task S/N 
                        Priority = self.Project.Tasks.Item(i).Text2 # A custom column to store task priority 
                        ReleaseName = self.Project.Tasks.Item(i).Text3 # A custom column to store release name 
                        QCDB = self.Project.Tasks.Item(i).Text5 # A custom column to store test results database name  
                        QCRel = self.Project.Tasks.Item(i).Text6 # A custom column to store test results path 
                        if not SN: continue # skip items w/o serial number
                        if str(SN)=='': continue # skip items w/o serial number
                        sns = SN.split(',') # handle comma separated multiple serial numbers
                        for s in sns:
                            sn = str(s)
                            if self.Project.Tasks.Item(i).ResourceNames!=None and str(self.Project.Tasks.Item(i).ResourceNames)!='': # skip tasks with no resource - most likely an RFQA or not interesting
                                if proj2time(self.Project.Tasks.Item(i).Finish)-proj2time(self.Project.Tasks.Item(i).Start)>0.0: # skip zero duration tasks
                                    task = True
                                    if not self._Tasks.has_key(sn): # new task S/N
                                        self._Tasks[sn]=dict()
                                        self._Tasks[sn]['Name'] = str(self.Project.Tasks.Item(i).Name.encode('ascii', 'ignore'))
                                        self._Tasks[sn]['Priority'] = str(Priority.encode('ascii', 'ignore'))
                                        self._Tasks[sn]['ReleaseName'] = str(ReleaseName.encode('ascii', 'ignore'))
                                        self._Tasks[sn]['QCDB'] = str(QCDB.encode('ascii', 'ignore'))
                                        self._Tasks[sn]['QCRelease'] = str(QCRel.encode('ascii', 'ignore'))
                                        self._Tasks[sn]['Resources'] = list()
                                        for resr in self.Project.Tasks.Item(i).ResourceNames.split(','): # handle multiple testers on the same task
                                            self._Tasks[sn]['Resources'].append(str(resr.encode('ascii', 'ignore')))
                                        self._Tasks[sn]['id'] = list()
                                        self._Tasks[sn]['id'].append(i)
                                        self._Tasks[sn]['outline'] = list()
                                        self._Tasks[sn]['outline'].append(self.Project.Tasks.Item(i).OutlineNumber)
                                        self._Tasks[sn]['Start'] = proj2time(self.Project.Tasks.Item(i).Start)
                                        self._Tasks[sn]['Finish'] = proj2time(self.Project.Tasks.Item(i).Finish)
                                        self._Tasks[sn]['PercentWorkCompleteList'] = list()
                                        self._Tasks[sn]['PercentWorkCompleteList'].append(int(self.Project.Tasks.Item(i).PercentWorkComplete))
                                    else: # update existing task S/N
                                        for resr in self.Project.Tasks.Item(i).ResourceNames.split(','): # handle multiple testers on the same task
                                            if not str(resr) in self._Tasks[sn]['Resources']:
                                                self._Tasks[sn]['Resources'].append(str(resr.encode('ascii', 'ignore')))
                                        if self._Tasks[sn]['Start'] > proj2time(self.Project.Tasks.Item(i).Start):
                                            self._Tasks[sn]['Start'] = proj2time(self.Project.Tasks.Item(i).Start)
                                        if self._Tasks[sn]['Finish'] < proj2time(self.Project.Tasks.Item(i).Finish):
                                            self._Tasks[sn]['Finish'] = proj2time(self.Project.Tasks.Item(i).Finish)
                                        self._Tasks[sn]['PercentWorkCompleteList'].append(int(self.Project.Tasks.Item(i).PercentWorkComplete))
                                        if self._Tasks[sn]['id'].count(i)==0:
                                            self._Tasks[sn]['id'].append(i)
                                        if self._Tasks[sn]['outline'].count(self.Project.Tasks.Item(i).OutlineNumber)==0:
                                            self._Tasks[sn]['outline'].append(self.Project.Tasks.Item(i).OutlineNumber)                                            
                            else: # no resource - might be an RFQA item
                                #if proj2time(self.Project.Tasks.Item(i).Finish)-proj2time(self.Project.Tasks.Item(i).Start)==0.0: # zero duration - better chance for being an RFQA item
                                if self.Project.Tasks.Item(i).PredecessorTasks.Count == 0: # no predecessors - even better chance for being an RFQA item
                                    if self.Project.Tasks.Item(i).OutlineChildren.Count == 0: # no subtasks - even better chance for being an RFQA item
                                        rfqa = True
                                        if not self._RFQAs.has_key(sn): # new RFQA S/N
                                            self._RFQAs[sn]=dict()
                                        # keep updating with lowest items on the tasks list, as these are likely to be RFQA items
                                        self._RFQAs[sn]['Name'] = str(self.Project.Tasks.Item(i).Name.encode('ascii', 'ignore'))
                                        self._RFQAs[sn]['Start'] = proj2time(self.Project.Tasks.Item(i).Start)
                                        self._RFQAs[sn]['Finish'] = proj2time(self.Project.Tasks.Item(i).Finish)
                                        self._RFQAs[sn]['Priority'] = str(Priority.encode('ascii', 'ignore'))
                                        self._RFQAs[sn]['ReleaseName'] = str(ReleaseName.encode('ascii', 'ignore'))
                                        self._RFQAs[sn]['id'] = list()
                                        self._RFQAs[sn]['id'].append(i)
                    if len(sns)>1: # keep a list of all lines that have multiple SNs
                        if not SN in self._compoundTask.keys():
                            self._compoundTask[SN]=list()
                        self._compoundTask[SN].append(i)
                    if not task and not rfqa: # keep a list of all tasks with serial number that were not handled as a task nor as an RFQA
                        if not SN in self._unknowns.keys():
                            self._unknowns[SN]=list()
                        self._unknowns[SN].append(i)
                except AttributeError:
                    continue # empty line in the file
            # compute average %complete for duplicated tasks
            for sn in self._Tasks.keys():
                tot = 0
                for p in self._Tasks[sn]['PercentWorkCompleteList']:
                    tot += p
                self._Tasks[sn]['PercentWorkComplete'] = int(tot/len(self._Tasks[sn]['PercentWorkCompleteList']))
            return self._Tasks
        except Exception, details:
            err = time.asctime()
            err += ' Error in ' + traceback.extract_stack()[-1][2] + ' :\n'
            err += ' ' + str(details)
            err += traceback.format_tb(sys.exc_info()[2])[0]
            print "Error:", err
            return self._Tasks


    def __setitem__(self, key, values):
        "Example: m.Tasks['26123']={'codeComplete':37.0}"
        if not self._Tasks:
            print 'No MSProject file was loaded and parsed yet.\nPlease load a file and get tasks first.'
            return None
        elif type(values)!=type(dict()):
            print 'Task updated fields should be in a form of a dictionary.\nPossible keys are:',
            print self._msfields
            return None
        elif len(key)>2:
            if key[:2]=='SN':
                if self._Tasks.has_key(key[2:]):
                    return self._update(key[2:], values)
            elif self._Tasks.has_key(key):
                return self._update(key, values)
            else:
                for i in range(1,self.Project.Tasks.Count+1):
                    try:
                        SN = self.Project.Tasks.Item(i).Text1 # This is the custom column where we currently store Accept360 S/N
                        if SN == key:
                            return self._update(key, values)
                    except AttributeError:
                        continue # empty line in the file
            print str(key) + ' was not found'
        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, key))

    def updateTask(self, key, values):
        "Example: m.updateTask('26123', {'codeComplete':37.0})"
        if not self._Tasks:
            print 'No MSProject file was loaded and parsed yet.\nPlease load a file and get tasks first.'
            return None
        elif type(values)!=type(dict()):
            print 'Task updated fields should be in a form of a dictionary.\nPossible keys are:',
            print self._msfields
            return None
        elif len(key)>2:
            if key[:2]=='SN':
                if self._Tasks.has_key(key[2:]):
                    return self._update(key[2:], values)
            elif self._Tasks.has_key(key):
                return self._update(key, values)
            else:
                for i in range(1,self.Project.Tasks.Count+1):
                    try:
                        SN = self.Project.Tasks.Item(i).Text1 # This is the custom column where we currently store Accept360 S/N
                        if SN == key:
                            return self._update(key, values)
                    except AttributeError:
                        continue # empty line in the file
            print str(key) + ' was not found'
        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, key))

    def updateRFQA(self, key, values):
        "Example: m.updateRFQA('26123', {'Finish': '2012/1/2'})"
        if not self._RFQAs:
            print 'No MSProject file was loaded and parsed yet.\nPlease load a file and get tasks first.'
            return None
        elif type(values)!=type(dict()):
            print 'Task updated fields should be in a form of a dictionary.\nPossible keys are:',
            print self._msfields
            return None
        elif len(key)>2:
            if key[:2]=='SN':
                if self._RFQAs.has_key(key[2:]):
                    return self._updateRFQA(key[2:], values)
            elif self._RFQAs.has_key(key):
                return self._updateRFQA(key, values)
            print str(key) + ' was not found'
        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, key))

    def _update(self, key, values):
        updt = True
        found = False
        for i in self._Tasks[key]['id']:
            for k, v in values.iteritems():
                if not k in self._msfields:
                    raise KeyError("Unknown or unsupported MSProject field: %s" % k)
                if debug: print 'updating:', i, k, v
                if not k in ['Priority', 'ReleaseName']:
                    setattr(self.Project.Tasks.Item(i), k, v)
                elif k == 'Priority':
                    setattr(self.Project.Tasks.Item(i), 'Text2', v)
                elif k == 'ReleaseName':
                    setattr(self.Project.Tasks.Item(i), 'Text3', v)
                else:
                    updt = False # we should never get here
                found = True
                if debug: print '\t>updated task at line:', i-1
        return updt & found

    def _updateRFQA(self, key, values):
        updt = True
        found = False
        for i in self._RFQAs[key]['id']:
            for k, v in values.iteritems():
                if not k in self._msfields:
                    raise KeyError("Unknown or unsupported MSProject field: %s" % k)
                if debug: print 'updating:', i, k, v
                if not k in ['Priority', 'ReleaseName']:
                    setattr(self.Project.Tasks.Item(i), k, v)
                elif k == 'Priority':
                    setattr(self.Project.Tasks.Item(i), 'Text2', v)
                elif k == 'ReleaseName':
                    setattr(self.Project.Tasks.Item(i), 'Text3', v)
                else:
                    updt = False # we should never get here, probably better to raise exception
                found = True
        return updt & found

    def updateProgressPerResource(self, acceptSN, resource, PercentWorkComplete):
        """Update task progress for a given S/N and resource."""
        updt = True
        found = False
        for i in self._Tasks[acceptSN]['id']:
            if self.Project.Tasks.Item(i).ResourceNames == resource:
                setattr(self.Project.Tasks.Item(i), 'PercentWorkComplete', PercentWorkComplete)
                found = True
                if debug: print '\t>updated task at line:', i-1
        return updt & found

    def updateRFQADate(self, acceptSN, newDate, resetStart=False):
        """Update task RFQA date.
        By default RFQA start(=original) time is left untouched."""
        updt = True
        found = False
        for i in self._RFQAs[acceptSN]['id']:
            setattr(self.Project.Tasks.Item(i), 'Finish', datetime.datetime.strptime(newDate, '%Y/%m/%d'))
            if resetStart:
                setattr(self.Project.Tasks.Item(i), 'Start', datetime.datetime.strptime(newDate, '%Y/%m/%d'))
            found = True
            if debug: print '\t>updated RFQA at line:', i-1
        return updt & found

    def findRange(self, taskName, startID=1):
        """Return the ID range of subtasks of a given task name or task SN. Only the first task of that name is handled."""
        parentID = None
        for i in range(startID, self.Project.Tasks.Count+1):
            if self.Project.Tasks.Item(i):
                if self.Project.Tasks.Item(i).Name == str(taskName) or self.Project.Tasks.Item(i).Text1 == str(taskName):
                    parentID = i
                    parentLevel = self.Project.Tasks.Item(i).OutlineNumber + '.'
                    break # we deal only with the first item found
        if not parentID:
            raise AttributeError("MSProject file has no task '%s'" % str(taskName))
        startID = parentID+1
        endID = parentID
        for i in range(startID, self.Project.Tasks.Count+1):
            if self.Project.Tasks.Item(i):
                if self.Project.Tasks.Item(i).OutlineNumber[0:len(parentLevel)] == parentLevel:
                    endID = i
                else:
                    break # no point to continue further
        if endID<startID:
            startID = parentID
            #print '*** No sub-tasks were found'
        return startID, endID


    def findSubRange(self, taskID):
        """Return the ID range of subtasks of a given task ID."""
        parentLevel = self.Project.Tasks.Item(taskID).OutlineNumber + '.'
        parentID = taskID
        startID = parentID+1
        endID = parentID
        for i in range(startID, self.Project.Tasks.Count+1):
            if self.Project.Tasks.Item(i):
                if self.Project.Tasks.Item(i).OutlineNumber[0:len(parentLevel)] == parentLevel:
                    endID = i
                else:
                    break # no point to continue further
        if endID<startID:
            startID = parentID
            #print '*** No sub-tasks were found'
        return startID, endID


    def buildAnalysisTree(self, task):
        """Create 2 trees of all analysis items, including their sub-tasks and information (start, end, progress).
        First tree is a dict with all AN keys. 2nd tree is a dict with all (py) categories.
        Code assumes that all subtasks of an AN item are of the same category"""
        tree = OrderedDict()
        cats = dict()
        trange = self.findRange(task)
        for i in range(trange[0]-1,trange[1]):
            sn = self.Project.Tasks.Item(i).Text1 # S/N column
            py = self.Project.Tasks.Item(i).Text4 # py column
            if sn.upper()[:3]=='AN-' and py.lower()!='ignore': # or i==(trange[0]-1):
                tree[sn]=dict()
                tree[sn]['subrange'] = self.findRange(sn, i)
                tree[sn]['start'] = proj2time(self.Project.Tasks.Item(i).Start)
                tree[sn]['finish'] = proj2time(self.Project.Tasks.Item(i).Finish)
                tree[sn]['category'] = py
                tree[sn]['totalWork'] = 0
                tree[sn]['actualWork'] = 0
                tree[sn]['percentWorkComplete'] = list()
                tree[sn]['subTasks'] = dict()
                if not py in cats:
                    cats[py]=dict()
                    cats[py]['subrange'] = list()
                    cats[py]['AN'] = list()
                    cats[py]['totalWork'] = 0
                    cats[py]['actualWork'] = 0
                    cats[py]['percentWorkComplete'] = list()
                    cats[py]['subTasks'] = dict()
                    cats[py]['start'] = proj2time(self.Project.Tasks.Item(i).Start)
                    cats[py]['finish'] = proj2time(self.Project.Tasks.Item(i).Finish)
                cats[py]['AN'].append(sn)
                if cats[py]['start']<proj2time(self.Project.Tasks.Item(i).Start):
                    cats[py]['start'] = proj2time(self.Project.Tasks.Item(i).Start)
                if proj2time(self.Project.Tasks.Item(i).Finish)>cats[py]['finish']:
                    cats[py]['finish'] = proj2time(self.Project.Tasks.Item(i).Finish)
                for j in range(tree[sn]['subrange'][0],tree[sn]['subrange'][1]+1):
                    if (self.Project.Tasks.Item(j).Text1 or self.Project.Tasks.Item(j).ResourceNames) and self.Project.Tasks.Item(j).Text4.lower()!='ignore':
                        rsn = string.join(self.Project.Tasks.Item(j).ResourceNames.split(','),'')
                        #s = self.findRange(self.Project.Tasks.Item(j).Text1, j)
                        s = self.findSubRange(j)
                        if s[0]==s[1]: # Work only on items that do not have sub-tasks
                            sns = str(self.Project.Tasks.Item(j).Text1)+'_'+str(rsn)+'_'+str(j)
                            tree[sn]['subTasks'][sns]=dict()
                            tree[sn]['subTasks'][sns]['start'] = proj2time(self.Project.Tasks.Item(j).Start)
                            tree[sn]['subTasks'][sns]['finish'] = proj2time(self.Project.Tasks.Item(j).Finish)
                            tree[sn]['subTasks'][sns]['work'] = self.Project.Tasks.Item(j).Work
                            tree[sn]['subTasks'][sns]['actual'] = self.Project.Tasks.Item(j).ActualWork
                            tree[sn]['subTasks'][sns]['percent'] = self.Project.Tasks.Item(j).PercentWorkComplete
                            tree[sn]['subTasks'][sns]['category'] = py
                            if tree[sn]['subTasks'][sns]['start']<tree[sn]['start']:
                                tree[sn]['start'] = tree[sn]['subTasks'][sns]['start']
                            if tree[sn]['subTasks'][sns]['finish']>tree[sn]['finish']:
                                tree[sn]['finish'] = tree[sn]['subTasks'][sns]['finish']
                            tree[sn]['totalWork'] += tree[sn]['subTasks'][sns]['work']
                            tree[sn]['actualWork'] += tree[sn]['subTasks'][sns]['actual']
                            tree[sn]['percentWorkComplete'].append(int(tree[sn]['subTasks'][sns]['percent']))
                            cats[py]['subTasks'][sns]=dict()
                            cats[py]['subTasks'][sns]['start'] = proj2time(self.Project.Tasks.Item(j).Start)
                            cats[py]['subTasks'][sns]['finish'] = proj2time(self.Project.Tasks.Item(j).Finish)
                            cats[py]['subTasks'][sns]['work'] = self.Project.Tasks.Item(j).Work
                            cats[py]['subTasks'][sns]['actual'] = self.Project.Tasks.Item(j).ActualWork
                            cats[py]['subTasks'][sns]['percent'] = self.Project.Tasks.Item(j).PercentWorkComplete
                            cats[py]['subTasks'][sns]['AN'] = sn
                            if cats[py]['subTasks'][sns]['start']<cats[py]['start']:
                                cats[py]['start'] = cats[py]['subTasks'][sns]['start']
                            if cats[py]['subTasks'][sns]['finish']>cats[py]['finish']:
                                cats[py]['finish'] = cats[py]['subTasks'][sns]['finish']
                            cats[py]['totalWork'] += cats[py]['subTasks'][sns]['work']
                            cats[py]['actualWork'] += cats[py]['subTasks'][sns]['actual']
                            cats[py]['percentWorkComplete'].append(int(cats[py]['subTasks'][sns]['percent']))
        return tree, cats


    def findDeadline(self, taskID):
        """Find deadline attribute for a give task."""
        try:
            pyt = self.Project.Tasks.Item(taskID).Deadline.Format('%Y/%m/%d')
        except AttributeError:
            pyt = self.Project.Tasks.Item(taskID).Finish.Format('%Y/%m/%d')
        pyp = self.Project.Tasks.Item(taskID).PercentWorkComplete
        pyo = self.Project.Tasks.Item(taskID).OutlineNumber
        pyol = len(pyo.split('.'))
        return pyt, pyp, pyol
