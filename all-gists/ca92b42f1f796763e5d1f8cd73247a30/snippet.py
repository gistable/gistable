# -*- coding: utf-8 -*-  
  
""" 
Sample client script for PNF Software's JEB2. 
 
More samples are available on our website and within the scripts/ folder. 
 
Refer to SCRIPTS.TXT for more information. 
"""  
  
import string  
import re,collections  
from com.pnfsoftware.jeb.client.api import IScript  
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext  
from com.pnfsoftware.jeb.core import RuntimeProjectUtil  
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData  
from com.pnfsoftware.jeb.core.events import JebEvent, J  
from com.pnfsoftware.jeb.core.output import AbstractUnitRepresentation, UnitRepresentationAdapter  
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem  
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaStaticField, IJavaNewArray, IJavaConstant, IJavaCall, IJavaField, IJavaMethod, IJavaClass  
from com.pnfsoftware.jeb.core.actions import ActionTypeHierarchyData  
from com.pnfsoftware.jeb.core.actions import ActionRenameData  
from com.pnfsoftware.jeb.core.util import DecompilerHelper  
from com.pnfsoftware.jeb.core.output.text import ITextDocument  
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit  
from java.lang import Runnable
  
class JEB2AutoRenameByTypeInfo(IScript):  
  def run(self, ctx):
    ctx.executeAsync("Running name detection...", JEB2AutoRename(ctx))
    print('Done')

class JEB2AutoRename(Runnable):  
  def __init__(self, ctx):
    self.ctx = ctx
  def run(self):
    ctx = self.ctx  
    engctx = ctx.getEnginesContext()  
    if not engctx:  
      print('Back-end engines not initialized')  
      return  
  
    projects = engctx.getProjects()  
    if not projects:  
      print('There is no opened project')  
      return  
  
    # 逻辑开始  
    prj = projects[0]  
  
    self.codeUnit = RuntimeProjectUtil.findUnitsByType(prj, ICodeUnit, False)
    self.curIdx = 0  
    bcUnits = []
    for unit in self.codeUnit:
      classes = unit.getClasses()
      if classes and unit.getName().lower() == "bytecode":
        bcUnits.append(unit)
    targetUnit = bcUnits[0]
    units = RuntimeProjectUtil.findUnitsByType(prj, IJavaSourceUnit, False)
    self.targetUnit = targetUnit
    #print(targetUnit.getClass(javaclz.getSupertype().getSignature()))
        #this is a single classes.dex item

    fuckingClasses = []
    cnt = 0
    for clz in targetUnit.getClasses():
      #the name maybe renamed
      #print(clz.getSignature(False))#False is for original Name
      if isFuckingName(clz.getName(False)):
        determinedName = self.tryDetermineGoodName(clz)
        if determinedName is None:
          determinedName = genNameFromIdx(cnt)
        else:
          determinedName = genNameFromIdx(cnt) + determinedName.split('/')[-1][:-1]
        self.commenceRename(clz.getSignature(False), determinedName, 0)
        print("cnt is " + str(cnt) +  "determined name is " + str(determinedName))
        cnt += 1
      
    #rename all fields
    cnt = 0
    for field in targetUnit.getFields():
      if isFuckingName(field.getName(False)):
        #get field type(renamed Type)
        fieldType = field.getFieldType().getName(True)
        newName = genNameFromIdx(cnt) + fieldType
        self.commenceRename(field.getAddress(), newName, 1)
        print("cnt is " + str(cnt) +  "determined name is " + str(newName))
        cnt += 1
    
    #rename all functions
    cnt = 0
    for mtd in targetUnit.getMethods():
      if isFuckingName(mtd.getName(False)):
        print(mtd.getName(False))
        #get method arguments
        #new mtd name is paramTypeJoin
        newName = genNameFromIdx(cnt) + ''.join(map(lambda x: x.getName(True), mtd.getParameterTypes()))
        self.commenceRename(mtd.getAddress(), newName, 2)
        print("cnt is " + str(cnt) +  "determined name is " + str(newName))
        cnt += 1
        



  def commenceRename(self, originName, newName, isClass):
    if isClass == 0:
      clz = self.targetUnit.getClass(originName)
    elif isClass == 1:
      clz = self.targetUnit.getField(originName)
    else:
      clz = self.targetUnit.getMethod(originName)
    actCntx = ActionContext(self.targetUnit, Actions.RENAME, clz.getItemId(), clz.getAddress())  
    actData = ActionRenameData()  
    actData.setNewName(newName)  

    if(self.targetUnit.prepareExecution(actCntx, actData)):  
      # 执行重命名动作  
      try:  
        bRlt = self.targetUnit.executeAction(actCntx, actData)  
        if(not bRlt):  
          print(u'executeAction fail!')  
      except Exception,e:  
        print Exception,":",e

  def tryDetermineGoodName(self, clzElement):
    decomp = DecompilerHelper.getDecompiler(self.targetUnit)
    javaunit = decomp.decompile(clzElement.getAddress())
    clzElement = javaunit.getClassElement()

    if not isFuckingName(clzElement.getName()):
      return clzElement.getName()
    ssupers = clzElement.getImplementedInterfaces()
    supers = []
    supers.extend(ssupers)
    # do not directly append on returned list!

    superSig = clzElement.getSupertype().getSignature()
    supers.append(clzElement.getSupertype())

    for superItem in supers:
      sig = superItem.getSignature()
      if sig == "Ljava/lang/Object;":
        continue
      if not isFuckingName(sig):
        return sig
      resolvedType = self.targetUnit.getClass(sig)
      if resolvedType:
        #this is a concret class
        guessedName = self.tryDetermineGoodName(resolvedType)
        if guessedName:
          return guessedName
      else:
        #this is a SDK class
        return sig
    return None
    
def isFuckingName(s):
  if s.find('/') != -1:
    s = s.split('/')[-1][:-1]
  elif s[-1] == ';':
    s = s[1:-1]
  return set(list(s.lower())) == set(list('li'))

def genNameFromIdx(idx):
  ret = ''
  while idx / 26 != 0:
    ret += chr(ord('a') + idx % 26)
    idx = idx /26
  ret += chr(ord('a') + idx % 26)
  return ret