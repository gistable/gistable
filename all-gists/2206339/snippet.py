def buildPAMS(mun, blk, lot, qua=None):
    """Returns a PAMS Pin from three or four cadastre fields."""
    if (qua == None) or (qua == ''):
        return "%s_%s_%s" % (mun, blk, lot)
    else:
        return "%s_%s_%s_%s" % (mun, blk, lot, qua)
