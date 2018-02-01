def GetIVRank(sessionid, symbol, useRank=True, debug=False):
    #this returns an dictionary with the key as date, and the value as the raw IV
    iv = GetImpliedVolatility(sessionid, symbol, debug=debug)
    keys = iv.keys()
    if len(keys)== 0:
        return -1
    
    
    keys.sort()
    highest = 0.0
    lowest  = 100.0
    try:
        latestiv = iv[keys[-1]]
    except:
        return -1
    if debug: print "%d datapoints" % len(keys)
    
    if useRank:
      above = 0
      below = 0
      for k in keys:
        if iv[k] > latestiv:
          above = above + 1
        else:
          below = below + 1
      if debug: print "%d above, %d below" % (above, below)
      return int(100.0*float(below)/float(len(keys)))
        
    
    thisiv = iv[keys[0]]
    last   = thisiv
    for k in keys:
        lastlast = last
        last = thisiv
        thisiv = iv[k]
        if debug:
            print k, thisiv
        if thisiv < 0 or abs(thisiv-last) > 1.0:
            if debug: print "Throwing out value"
            thisiv = lastlast
            last   = lastlast
            continue
        if thisiv > highest:
            if debug: print "New high"
            highest = thisiv
        if thisiv < lowest:
            if debug: print "New low"
            lowest = thisiv
    if debug:
      print "highest: %f lowest %f latest: %f" % (highest, lowest, latestiv)
      print iv[keys[-1]]
    ivrank = (latestiv - lowest) / (highest - lowest)
    return int(ivrank*100.0)
