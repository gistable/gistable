def checkio(gr):
    r = gr
    r += ["".join(v) for v in zip(*gr)]
    r += [gr[0][0] + gr[1][1] + gr[2][2],
          gr[0][2] + gr[1][1] + gr[2][0]]

    o = r.count("OOO")
    x = r.count("XXX")
    
    if o and x:
        return "D"
    elif o:
        return "O"
    elif x:
        return "X"
    else:
        return "D"