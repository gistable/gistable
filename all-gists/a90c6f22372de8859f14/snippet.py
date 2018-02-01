#!/usr/bin/python

# A microcode assembler

import os
import os.path
import re
import collections

import IPython.Shell
ipsh = IPython.Shell.IPShellEmbed()

class Symbol(object):
    def __init__(self,s):
        self.str = intern(s)

def s(str_):
    return Symbol(str_)

class Microcode(object):

    def linenormalizer(self,instream):
        pending = []
        for a in instream:
            a = a.rstrip('\r\n').replace('\f','')
            
            try:
                a = a[:a.index(';')]
            except ValueError:
                pass
            a = a.strip(' \t')
            if a:
                pending.append(a)
                if not a.endswith(','):
                    yield "\n".join(pending)
                    pending = []
        if pending:
            yield "\n".join(pending)

    def parse(self,instream,processor):
        postre = r'[ \t]*([^ \t].*)?$'
        setre = re.compile(r'\.(?:DEFAULT|SET)/([^=]*)=(.*)$')
        fieldspec1 = re.compile(r'[^,<]+(?:<[^>]*>)?(?=,|$)')
        constraintRE = re.compile(r'^=([01*]*)' + postre, re.DOTALL)
        labelRE = re.compile(r'^([^ \t</=]+):' + postre, re.DOTALL)
        fielddefRE = re.compile(r'([^/]+)/=<([0-9]+)(?::([0-9]+))?>([+DFTP])?(?:,(.*))?')
        macroRE = re.compile(r'([^"]*[^" \t])[ \t]+"([^"]+)"$')
        fieldspec2 = re.compile(r'((?:[^\]\[/]|\[[^\]]+\])+)(?:/([^/\]\[]*[^/,\[\] \t]))?[ \t]*$')
        for x in self.linenormalizer(instream):
            # Various directives...
            if x.startswith('.'):
                d = True
                if x.startswith('.TOC'):
                    tocline = x[4:].strip(' \t').strip('"')
                    processor.toc(tocline)
                elif x.startswith('.BIN'):
                    processor.bin(True)
                elif x.startswith('.NOBIN'):
                    processor.bin(False)
                elif x.startswith('.DCODE'):
                    processor.dcode()
                elif x.startswith('.UCODE'):
                    processor.ucode()
                elif x.startswith('.DEFAULT'):
                    k,v = setre.match(x).groups()
                    processor.default(k,int(v))
                elif x.startswith('.SET'):
                    k,v = setre.match(x).groups()
                    processor.set(k,int(v))
                elif x.startswith('.ENDIF'):
                    processor.endif(x.split('/',1)[1])
                elif x.startswith('.IFNOT'):
                    processor.ifnot(x.split('/',1)[1])
                elif x.startswith('.IF'):
                    processor.if_(x.split('/',1)[1])
                elif x.startswith('.RAMFILE'):
                    line = fieldspec1.findall(x.replace('\n','').replace('\t','').split('/',1)[1])
                    processor.ramfile(line)
                elif x.startswith('.TITLE'):
                    processor.title(x[6:].strip(' \t').strip('"'))
                elif x.startswith('.WIDTH'):
                    processor.width(int(x.split('/')[1]))
                else:
                    d = False
                if d:
                    continue
            # not a directive
            if x.startswith('='):
                try:
                    a = constraintRE.match(x).groups()
                except:
                    raise Exception('Constraint: ' + x)
                processor.constraint(a[0])
                if a[1]:
                    x = a[1]
                else:
                    continue
            elif labelRE.match(x):
                a = labelRE.match(x).groups()
                processor.label(a[0])
                if a[1]:
                    x = a[1]
                else:
                    continue
            elif '/=' in x:
                # field def...
                a = fielddefRE.match(x).groups()
                assert a, "Bad fielddef?"
                processor.def_field(a[0],
                                      int(a[1]), int(a[2]) if a[2] else None,
                                      a[3],
                                      a[4])
                continue
            elif '=' in x:
                assert x.count('=') == 1
                sym,val = x.split('=')
                processor.def_sym(sym,val)
                continue
            elif '"' in x:
                try:
                    name,val = macroRE.match(x).groups()
                except AttributeError:
                    raise Exception('Macro: ' + x)
                processor.def_macro(name,val)
                continue

            l = []
            for i in x.replace('\n','').replace('\t','').split(','):
                #try:
                l.append(fieldspec2.match(i).groups())
                #except Exception, e:
                #    raise Exception('Fieldspec: ' + i + ">", e)
            processor.instruction(l)
                
        processor.finish()
        return processor

def parseInt(x):
    base = 8
    if x.endswith('.'):
        x = x[:-1]
        base = 10
    elif '9' in x or '8' in x:
        base = 10
    return int(x,base)
    
class SexpProcessor(object):
    def __init__(self):
        self.data = []
        self.infield = False
        self.fieldvals = None
        self.cond = set()
    def addcond(self,lst):
        if self.cond:
            return [s('when'),list(cond),lst]
        else:
            return lst
    def p(self,*args):
        self.data.append(addcond(list(args)))
        self.infield = False
        self.fieldvals = False
    def toc(self,toc):
        self.p(s("toc"), toc)
    def set(self,var,val):
        self.p(s("set"),s(var),val)
    def def_field(self,name,l,r,mode,default):
        args = [s("field"),s(name),
                [s("range"),l,r]
                ]
        if mode == 'D':
            args.append([s('default'), int(default,8)])
        elif mode == 'F':
            args.append([s('default'), s(default)])
        elif mode == '+':
            assert default is None
            args.append([s('default'), s('+')])
        elif mode is None:
            assert default is None
        else:
            assert "Unknown mode " + mode
        self.data.append(args)
        self.infield = True
        self.fieldvals = None
    def def_sym(self,name,val):
        assert self.infield
        if not self.fieldvals:
            self.fieldvals = [s('fields')]
            assert self.data[-1][0].str == 'field'
            self.data[-1].append(self.fieldvals)
        self.fieldvals.append([s(name),parseInt(val)])
    def bin(self,binp):
        self.p(s('bin'),binp)
    def title(self,title):
        self.p(s('title'),title)
    def default(self,name,val):
        self.p(s('setdefault'),s(name),val)
    def width(self,val):
        self.p(s('width'),val)
    def ramfile(self,val):
        self.p(s('ramfile'),*val)
    def ifnot(self,val):
        pass

class SingleAssignmentList(list):
    def __init__(self,iter=[]):
        self.__items = set()
    def __setitem__(self,i,v):
        if i in self.__items:
            raise Exception("Not modifiable")
        self.__items.add(i)
        self[i] = v
            
    
class AddressAllocator(object):
    __slots__ = ("alloced","pc","mask","constraint",
                 'rmap','labels','modemap',
                 'target_mode','cur_mode','ino','size',
                 'sequential')
    MODE_ABS = 1
    MODE_EQ = 2
    MODE_UNC = 3
    def __init__(self,size):
        self.sequential = False
        self.alloced = [False] * size
        self.rmap = [None] * size
        self.modemap = [None] * size
        self.pc = None
        self.size = size
        self.constraint = None
        self.target_mode = 0
        self.cur_mode = -1
        self.labels = {}
        self.ino = 0
    def statel(self):
        return (self.pc,self.target_mode,self.cur_mode,self.ino,(len(self.constraint) if self.constraint else 0))
    def i_insn(self,args):
        #if self.target_mode == 2:
        #    ipsh(header='i_insn')
        #assert self.pc > -1 or self.target_mode == 1 or self.ino < 19,self.statel()
        #print self.target_mode,self.ino,args
        if self.ino == 1800:
            print "1:", 
        if self.should_process_p(self.ino):
            if self.ino == 1800:
                print "a", self.constraint, self.pc
            self.rmap[self.ino] = self.pc
            if self.cur_mode != self.MODE_ABS:
                assert not self.alloced[self.pc],(self.statel() + (args,))
            self.alloced[self.pc] = True
        else:
            assert self.target_mode != self.MODE_UNC or self.rmap[self.ino] is not None, (self.statel() + (args,))
        if self.constraint:
            self.pc = self.constraint.pop(0)
            #self.pc = self.constraint.nextafter(self.pc)
            self.ino += 1
            return
        self.pc = None # pc not known anymore. In unconstrained mode, the first case will cover this. Otherwise. we filled the block.
        self.ino += 1
         
    def c_clear(self):
        self.constraint = None
        self.pc = None

    def c_pos(self,pos):
        self.cur_mode = self.MODE_ABS
        self.constraint = None
        self.pc = pos

    def _match_pattern(self,pattern,mask,val):
        return (pattern & mask) == (val & mask)
    def gen_possibilities(self,mask):
        possibilities = [0]
        while mask != 0:
            bit = mask & -mask # LSB
            mask = mask & (mask-1)
            possibilities.extend([a | bit for a in possibilities])
        return possibilities
    def s_label(self,lbl):
        self.labels[lbl] = self.ino
    def c_pattern(self,pat):
        if self.target_mode != self.MODE_EQ:
            return
        #if self.target_mode != self.MODE_EQ:
        #    self.cur_mode = self.MODE_EQ
        #    return
        def testmask(mask,pattern):
            fullmask = self.size - 1
            res = sorted(a | (mask & pattern)
                         for a in self.gen_possibilities(fullmask & ~mask))
            if self.target_mode != self.MODE_EQ:
                self.constraint = res
                return True
            for x in res:
                if self.alloced[x]:
                    return False
            self.constraint = res
            return True
        y = 0
        n = 0
        dc = self.size - 1
        for i,x in enumerate(reversed(pat)):
            if x == '0':
                n |= 2**i
            elif x == '1':
                y |= 2 **i
        dc ^= n | y
        if self.constraint is not None and self.pc is not None:
            if self._match_pattern(y,y|n,self.pc):
                return
            while self.constraint:
                if self._match_pattern(y,y|n,self.constraint[0]):
                    self.pc = self.constraint.pop(0)
                    return
                else:
                    self.constraint.pop(0)
            else:
                raise Exception("Failed to allocate")
        self.cur_mode = self.MODE_EQ
        for x in sorted(a|y for a in self.gen_possibilities(dc)):
            if testmask(y|dc, x):
                self.pc = self.constraint.pop(0)
                return
        raise Exception("Could not allocate!")
    def should_process_p(self,ino):
        """ino is the insn number or tag name.

        Return true if it should be processed, false otherwise

        Side effects: If pc not known, and unconstrained, find free loc"""
        if self.rmap[ino] is not None:
            return False
        if self.pc is not None:
            return True
        if self.target_mode != self.MODE_UNC:
            return False
        if self.sequential and ino > 0 and self.rmap[ino - 1] is not None and not self.alloced[self.rmap[ino - 1] + 1]:
            self.pc = self.rmap[ino - 1] + 1
            return True
        for pc in range(0,self.size):
            if not self.alloced[pc]:
                #self.next_pc = pc - 1
                self.pc = pc
                self.constraint = None
                return True
        else:
            raise Exception("No more room")
    def next(self):
        raise Exception()
        #if self.cur_mode != self.target_mode:
        #    return False
        v = self.pc
        if self.cur_mode == self.MODE_UNC:
            if not self.alloced[self.pc]:
                return self.pc
            v = (v + 1) % self.size
            while v != self.pc:
                if not self.alloced[v]:
                    return v
                v = (v + 1) % self.size
            else:
                return -1
                raise Exception("Could not place instruction")
        elif self.constraint:
            if not self.constraint:
                self.cur_mode = self.MODE_UNC
                return self.next()
            v = self.constraint.pop(0)
            #if not self.constraint:
            #    self.cur_mode = self.MODE_UNC
                
            return v
        elif self.cur_mode == self.MODE_ABS:
            self.cur_mode = self.MODE_UNC
            return self.next()
        else:
            raise Exception('wat')
        
class AssemblyState(object):
    __slots__ = ("macros","fields","insns", #"stateless"
                 "size","name","code",
                 "labels",
                 "cur_field", #Because of the interface
                 )
    FieldSpec = collections.namedtuple('FieldSpec','name range default values')
    def __init__(self,size,name):
        self.macros = {}
        self.fields = {}
        self.code = [None] * size
        self.insns = []
        self.size = size
        self.name = name
        self.cur_field = None
    def def_field(self,name,(l,r),default):
        assert name not in self.fields
        f = self.FieldSpec(name=name,
                           range=(l,r),
                           default=default,
                           values={})
        self.fields[name] = f
        self.cur_field = f
    def def_sym(self,name,val):
        try:
            assert self.cur_field is not None
            assert name not in self.cur_field.values
        except:
            print self.cur_field.name, name
            raise
        self.cur_field.values[name] = val
    def def_macro(self,name,body):
        self.macros[name] = body
    def instruction(self,args):
        self.insns.append( ('i_insn',args) )
    def constraint(self,constraint):
        if constraint == '':
            self.insns.append( ('c_clear',))
        else:
            self.insns.append( ('c_pattern',constraint) )
    def label(self,name):
        #print self.name, name
        if type(name) is int:
            self.insns.append( ('c_pos', name) )
        else:
            if name == 'TENLP':
                print "Here!"
            self.insns.append( ('s_label',name) )

    def runscript(self,script,processor,v=False):
        for x in script:
            if v:
                print x
            getattr(processor,x[0])(*x[1:])
    def assign_addresses(self):
        a = AddressAllocator(self.size)
        if self.name[0].lower() == 'd':
            a.sequential = True
        mi = 0
        for tmode in (a.MODE_ABS,a.MODE_EQ,a.MODE_UNC):
            a.ino = 0
            a.cur_mode = a.MODE_UNC
            a.target_mode = tmode
            self.runscript(self.insns,a)
            mi = a.ino - 1
        assert None not in a.rmap[:mi+1],a.rmap[:mi+1]
        self.labels = {}
        for k,v in a.labels.iteritems():
            self.labels[k] = a.rmap[v]
        if self.name[0].upper() == 'U':
            print self.labels['TENLP']
        self.runscript(self.insns,PostMapper(a.rmap,self.code,self.name))
        
    def load_labels(self,ldict):
        self.fields['J'].values.update(ldict)
    def assemble(self):
        pass
    def finish(self):
        self.assign_addresses()
        self.assemble()
        
class PostMapper(object):
    __slots__ = ("rmap","data","ino",'chr')
    
    def __init__(self,rmap,data,name):
        self.rmap = rmap
        self.data = data
        self.ino = 0
        self.chr = name[0].upper()
    def statel(self):
        return (self.rmap[self.ino],self.ino)
    def i_insn(self,args):
        pos = self.rmap[self.ino]
        assert self.data[pos] is None, self.statel()
        self.data[pos] = (args,self.rmap[(self.ino + 1) % len(self.rmap)])
        #print self.chr, self.ino, oct(pos).zfill(4), args
        print "@", self.chr, oct(pos).lstrip('0').zfill(4) + ",", self.ino, ",", args
        self.ino += 1
    def c_clear(self):
        pass
    def c_pos(self,p):
        pass
    def c_pattern(self,p):
        pass
    def s_label(self,l):
        pass
        

NEXT_INSN = object()
class AssemblingProcessor(object):
    UCODE = 1
    DCODE = 2
    
    def __init__(self,AssemblyState = AssemblyState):
        self.vars = {}
        self.defaults = {}
        self.conditions = {}
        self.ucode_ = AssemblyState(2048,"ucode")
        self.dcode_ = AssemblyState(512,"dcode")
        self.destination = self.ucode_
        self.setvars = set()
        self.unsetvars = set()
        self.output_enable = True
        self.shouldCompile = True
        self.shortcut = False
    def toc(self,entry):
        print " -- " + entry
    def title(self,title):
        print " --------------- " + title + " -------------- "

    def setvar(self,var,val,default=False):
        assert val in (0,1), "val: " + repr(val)
        val = bool(val)
        if default:
            self.defaults[var] = val
            if var in self.vars:
                return
        else:
            self.vars[var] = val
        vset = set([var])
        if val:
            self.setvars |= vset
            self.unsetvars -= vset
        else:
            self.setvars -= vset
            self.unsetvars |= vset
        self._check_cond()
        
    def default(self,var,val):
        self.setvar(var,val,default=True)
    def set(self,var,val):
        self.setvar(var,val,default=False)
    def _check_cond(self,force=True):
        #print self.vars
        #print map(sorted, [self.setvars, self.unsetvars, self.vars.keys(),self.defaults.keys()])
        assert (self.setvars | self.unsetvars) == (set(self.vars.keys()) | set(self.defaults.keys()))
        assert not (self.setvars & self.unsetvars)
        if self.shouldCompile and not force:
            self.shortcut = True
            return
        self.shortcut = False
        for k,v in self.conditions.iteritems():
            if k in (self.unsetvars if v else self.setvars):
                self.shouldCompile = False
                break
        else:
            self.shouldCompile = True
        return self.shouldCompile
                
    def if_(self,var):
        #assert var not in self.conditions
        self.conditions[var] = True
        self._check_cond()
    def ifnot(self,var):
        #assert var not in self.conditions
        self.conditions[var] = False
        self._check_cond()
    def endif(self,var):
        assert var in self.conditions
        del self.conditions[var]
        self._check_cond(False)

    def def_field(self,name,l,r,mode,default):
        if not self.shouldCompile:
            return
        if r is None:
            r = l
        if mode == 'D':
            d = parseInt(default)
        elif mode == 'F':
            d = intern(default)
        elif mode == '+':
            d = NEXT_INSN
        elif mode is None:
            d = None
            assert default is None
        else:
            assert "Mode '%s' not understood"%(mode)
        self.destination.def_field(name,(l,r),default)
    def def_sym(self,name,val):
        if not self.shouldCompile:
            return
        self.destination.def_sym(name,parseInt(val))
    def def_macro(self,name,body):
        if self.shouldCompile:
            self.destination.def_macro(name,body)
    def bin(self,enable):
        self.output_enable = enable
    def width(self,w):
        self.bitwidth = w
    def ramfile(self,args):
        self.ramfilefmt = args
    def ucode(self):
        self.destination = self.ucode_
    def dcode(self):
        self.destination = self.dcode_
    def label(self,pos):
        try:
            pos = int(pos,8)
        except ValueError:
            pass
        if pos == 'TENLP':
            print "Here!", self.shouldCompile, self.vars
        if self.shouldCompile:
            self.destination.label(pos)
    def instruction(self,args):
        if self.shouldCompile:
            #print "%s %s"%(self.destination.name[0], str(args))
            self.destination.instruction(args)
    def constraint(self,constraint):
        if self.shouldCompile:
            self.destination.constraint(constraint)
    def finish(self):
        self.ucode_.finish()
        self.dcode_.load_labels(self.ucode_.labels)
        print "DCODE:     -----------------------------"
        self.dcode_.finish()

class CountingProcessor(object):
    def __init__(self):
        self._counts = {}
    def getc(self):
        return self._counts
    def __getattr__(self,item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            def foo(*args):
                self._counts.setdefault(item,list()).append(args)
            return foo


class Multiset(collections.MutableSet,collections.Mapping):
    def __init__(self,iterable=[]):
        self.__items = {}
        for x in iterable:
            self.add(x)
        pass
    def discard(self,val):
        if val in self.__items:
            self.__items[val] -= 1
            if self.__items[val] == 0:
                del self.__items[val]
    def __getitem__(self,key):
        return self.__items[key]
    def __iter__(self):
        return iter(self.__items)
    def __len__(self):
        return len(self.__items)
    def add(self,val):
        self.__items[val] = self.__items.get(val,0) + 1
    def str(self):
        return str(self.__items)
class Datacounter(object):
    def __init__(self,**specs):
        """Each spec should be a dictionary of (label -> test).  The
           test is called as test(value,label). If it returns true,
           that is considered a match.

           """

files = ["its.16","ks10.47","simple.42","flt.5","extend.4","inout.50","itspag.98","pagef.10"]
instr = []
def loadf(path="/home/thequux/projects/qs10/micro.in/"):
    global instr
    instr = []
    for x in files:
        instr.append('.TITLE\t" >>>>>>>> %s <<<<<<<<<<"\n' %x)
        instr.extend(file(os.path.join(path,x),"r"))


if __name__ == '__main__':
    loadf()
    Microcode().parse(instr,AssemblingProcessor())