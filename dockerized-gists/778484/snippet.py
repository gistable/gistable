## turn a 2-d python matrix (list of lists) into a .csv file

## see also gist: 778481 to reverse the process

def writeMatrixCSV(mx, fname):
    ## mx is a 2-d python matrix
    ## fname is the desired output filename
    f = open(fname, 'w')
    for r in mx:
        tx = ''
        i = 0
        while i < (len(r)-1):
            tx += str(r[i])
            tx += ','
            i += 1
        try:    tx += str(r[(len(r)-1)])
        except: pass
        if tx == '':    pass
        else:   tx += '\n'
        f.write(tx)
    f.close()