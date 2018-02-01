from leveldb import LevelDB as _LevelDB
def _DB(_=[]): return (_ or _.append(_LevelDB('.db')) or 1) and _[0]
def ZAP(): list(DLT(k) for k,v in RNG([]))
def DLT(k): _DB().Delete(':'.join(k))
def GET(k): return json.loads(_DB().Get(':'.join(k)))
def PUT(k,v): _DB().Put(':'.join(k),json.dumps(v))
def RNGP(pfx=''):return (((k.split(':'),json.loads(v)) for k,v in
                          _DB().RangeIter(pfx,pfx+'~~~')))
def RNG(k=[]): return RNGP(':'.join(k))
def DLT1P(del_pfx): return ( DLT( k ) for k,v in RNG(del_pfx) )
def DLTSP(pfx_itr): return ( DLT1P(pfx) for pfx in pfx_itr )
def DUMP(pfx=''): return (((k,v) for k,v in _DB().RangeIter(pfx,pfx+'~~~')))