import string
import sys
import os
from collections import Counter
import win32com.client

# Sample code for accessing QualityCenter
# 2014 (C) Zohar Lorberbaum

debug = False

class QualityCenter(object):
    """QualityCenter module."""
    def __init__(self):
        """Initializing QualityCenter object does not require any input."""
        self._td = win32com.client.Dispatch("TDApiOle80.TDConnection.1")
        self._TSserver = 'QC URL'
        self._TDname = 'QC IP'
        self._username = 'QC Username'
        self._pwd = 'QC Password'

    def __call__(self):
        print 'QualityCenter call'
        return

    def __getattr__(self,attr):
        if attr == 'Requirements':
            if not self.__dict__.has_key('_Requirements'):
                self._Requirements=Requirements(self._td)
            return self._Requirements
        else:
            raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))

    def __repr__(self): 
        return "QualityCenter class"
    
    def __dir__(self):
        d=['Requirements']
        return d + self.__dict__.keys() + self.__class__.__dict__.keys()

    def connect(self, domain, project):
        """Connect and login to QC, to specified domain and project"""
        self._td.InitConnectionEx( "http://" + self._TSserver )
        self._td.ConnectProjectEx(domain, project, self._username, self._pwd)
        if debug: print self._td.Connected
        return self._td.Connected

    def disconnect(self):
        """ Disconnect and logout from QC """
        if not self.__dict__.has_key('_td'):
            print "Not connected\n"
            return True
        self._td.Disconnect()
        self._td.Logout()
        if debug: print not self._td.LoggedIn
        return not self._td.LoggedIn


class Requirements(object):
    """Object to hold Requirements in QualityCenter.
    Accept360 S/N is the key to access the requirement."""
    def __init__(self, td):
        self.td = td
        return
    
    def __call__(self, *args, **kargs):
        if kargs:
            if kargs.has_key('SN'):
                if self.__dict__.has_key('_Requirements'):
                    if self._Requirements.has_key(kargs['SN']):
                        return self._Requirements[kargs['SN']]
            else:
                print 'No requirements were retreived from server yet.\nPlease perform a parsed query.'
                return None
        elif args:
            if self.__dict__.has_key('_Requirements'):
                if len(args)>0:
                    for arg in args:
                        if arg[:2]=='SN':
                            if self._Requirements.has_key(arg[2:]):
                                return self._Requirements[arg[2:]]
                        else:
                            if self._Requirements.has_key(arg):
                                return self._Requirements[arg]
                        print str(arg) + ' was not found'
                    return None
            else:
                print 'Please load requirements from server first.'
                return None
        else:
            if not self.__dict__.has_key('_Requirements'):
                self.getCoverage()
            return self._Requirements

    def __getattr__(self,attr):
        if attr == 'Requirements':
            if not self.__dict__.has_key('_Requirements'):
                self.getCoverage()
            return self._Requirements
        elif self.__dict__.has_key(attr):
            return self.__dict__[attr]
        elif self.__dict__.has_key('_Requirements'):
            if len(attr)>2:
                if attr[:2]=='SN':
                    if self._Requirements.has_key(attr[2:]):
                        return self._Requirements[attr[2:]]
                else:
                    if self._Requirements.has_key(attr):
                        return self._Requirements[attr]
            for req in self.rList:
                if not req.IsFolder: # Ignore requirement folders (they do not have S/N)
                    SN = req.Field('RQ_USER_03') # This is the custom field where we currently store Accept360 S/N
                    if SN == attr:
                        return req
        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))

    def __getitem__(self,attr):
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]
        elif self.__dict__.has_key('_Requirements'):
            if len(attr)>2:
                if attr[:2]=='SN':
                    if self._Requirements.has_key(attr[2:]):
                        return self._Requirements[attr[2:]]
                else:
                    if self._Requirements.has_key(attr):
                        return self._Requirements[attr]
            for req in self.rList:
                if not req.IsFolder: # Ignore requirement folders (they do not have S/N)
                    SN = req.Field('RQ_USER_03') # This is the custom field where we currently store Accept360 S/N
                    if SN == attr:
                        return req
            return str(attr) + ' was not found'
        else:
            raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))

    def __repr__(self):
        if self.__dict__.has_key('_Requirements'):
            return 'Requirements: '+str(self._Requirements.keys())
        else:
            return 'No requirements were retreived from server yet.\nPlease perform a parsed query.'
    
    def __dir__(self):
        l=list()
        if self.__dict__.has_key('_Requirements'):
            for k in self._Requirements.keys():
                l.append('SN'+string.join(str(k).split(),''))
        return l + self.__dict__.keys() + self.__class__.__dict__.keys()

    def get(self):
        "Returns a list with all requirement objects"
        self.rFact = self.td.ReqFactory
        self.rList = self.rFact.NewList('')
        return self.rList
        
    def getCoverage(self):
        "Get test coverage for all requirements in the project that have Accept360 SN filled in."
        self.get()
        self._Requirements = dict() # Stores all requirements to be returned from this function
        for req in self.rList:
            if debug: print req.ID,
            if not req.IsFolder: # Ignore requirement folders (they do not have S/N)
                SN = req.Field('RQ_USER_03') # This is the custom field where we currently store Accept360 S/N
                NAME = req.Name.encode('ascii', 'ignore') # Requirement name
                if not SN: # Skip requirements that have no S/N
                    if debug:
                        print repr(SN),'\t',
                        print NAME[:64],'\t'
                else:
                    if debug: print SN.encode('ascii', 'ignore'),'\t',
                    if debug: print NAME[:64],'\t',
                    cnt = Counter()
                    if not req.HasCoverage: # Check if requirement has test coverage
                        if debug: print     
                    else:
                        cvr = req.GetCoverageTestConfigs()
                        if debug: print repr(cvr)
                        for c in cvr:
                            cnt[str(c.ExecStatus)] += 1
                        if debug: print cnt,
                    # Handle cases where there are multiple serial numbers listed
                    sns=SN.split(',')
                    for s in sns:
                        sn=string.join(s.split(),'')
                        if not self._Requirements.has_key(sn):
                            self._Requirements[sn] = dict()
                            self._Requirements[sn]['TestCoverageDetails'] = Counter()
                            self._Requirements[sn]['TestCoverage'] = dict()
                            self._Requirements[sn]['Name'] = NAME
                            self._Requirements[sn]['ID'] = req.ID
                            self._Requirements[sn]['Tester'] = list()
                        self._Requirements[sn]['TestCoverageDetails'] += cnt
                    if debug: print
        
        # Calculate percent complete for all collected requirements
        if debug: print '\n----------------------------------------\n'
        for sn in self._Requirements.keys():
            if debug: print sn,
            self._Requirements[sn]['TestCoverage']['Total'] = 0
            self._Requirements[sn]['TestCoverage']['Progress'] = 0
            for t in self._Requirements[sn]['TestCoverageDetails'].keys():
                #if t not in ['N/A']:  # This would ignore N/A tests from the total - not for now since this could apply to only part of the scope
                self._Requirements[sn]['TestCoverage']['Total'] += self._Requirements[sn]['TestCoverageDetails'][t]
                if t in ['Passed', 'Failed']:
                    self._Requirements[sn]['TestCoverage']['Progress'] += self._Requirements[sn]['TestCoverageDetails'][t]
            if self._Requirements[sn]['TestCoverage']['Total'] == 0:
                self._Requirements[sn]['TestCoverage']['%Complete'] = 0.0
            else:
                self._Requirements[sn]['TestCoverage']['%Complete'] = \
                    int( 100.0*self._Requirements[sn]['TestCoverage']['Progress']/self._Requirements[sn]['TestCoverage']['Total'] )
            if debug: print self._Requirements[sn]['TestCoverage']
        return self._Requirements

    def __setitem__(self, key, values):
        """Example: a.Tasks['26123']={'codeComplete':37.0}"""
        if not self.__dict__.has_key('_Requirements'):
            print 'No QualityCenter Project was loaded and parsed yet.\nPlease load requirements from QualityCenter first.'
            return None
        elif type(values)!=type(dict()):
            print 'Requirement updated fields should be in a form of a dictionary.\nPossible keys are:',
            print self._msfields
            return None
        elif len(key)>2:
            if key[:2]=='SN':
                if self._Requirements.has_key(key[2:]):
                    return self._update(key[2:], values)
            elif self._Requirements.has_key(key):
                return self._update(key, values)
            else:
                for req in self.rList:
                    if not req.IsFolder: # Ignore requirement folders (they do not have S/N)
                        SN = req.Field('RQ_USER_03') # This is the custom field where we currently store Accept360 S/N
                        if SN == key:
                            return self._update(key, values)
            print str(key) + ' was not found'
        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, key))

    def _update(self, key, values):
        updt = True
        found = False
        for req in self.rList:
            if not req.IsFolder: # Ignore requirement folders (they do not have S/N)
                SN = req.Field('RQ_USER_03') # This is the custom field where we currently store Accept360 S/N
                if SN:
                    if SN == key:
                        for k, v in values.iteritems():
                            if k=='Name':
                                req.Name=str(v)
                            if k=='Tester':
                                req.SetField("RQ_USER_02", str(v))
                            else:
                                raise KeyError("Unknown or unsupported QualityCenter field: %s" % k)
                        req.Post()
                        found = True
                        #self.getCoverage()
                    elif SN.split(',').count(key)>0:
                        print '\n*** Code does not hanlde update of tasks with multiple Accept360 requirements, unless list of tasks exactly match.'
                        print '*** Skipping update of requirment '+str(key)+'.'
                        updt = False
        self.getCoverage()
        return updt & found

    def findReqID(self, reqName):
        """Return QC requirement ID for given requirement name."""
        self.get()
        for req in self.rList:
            if req.Name == reqName:
                return req.ID
        return


    def addRequirement(self, parentName, RequirementName, SN='', Tester='', TypeId='Testing', *args, **kargs):
        """Add a new requirement, given name and parent name, with optional TypeID and with optional fields configuration as a dictionaty)."""
        rf = self.td.ReqFactory
        prid = self.findReqID(parentName)
        if not prid:
            raise KeyError("Parent requirement not found: %s" % parentName)
        nr = rf.AddItem(None)
        nr.ParentId = prid
        #Clean Requirement name from unsupported characters: The characters \\/:"?\'<>|*% are not allowed.
        clnReq = RequirementName.replace('\\','-').replace('/','-').replace(':','-').replace('"','').replace('?',' ').replace("'",'').replace('<',' ').replace('>',' ').replace('|',' ').replace('*',' ').replace('%',' ')
        nr.Name = clnReq
        nr.TypeId = TypeId
        nr.SetField('RQ_USER_02', str(Tester))
        nr.SetField('RQ_USER_03', str(SN))
        for k in kargs:
            nr.__setattr__(str(k), str(kargs[k]))
        nr.Post()
        return nr.ID
