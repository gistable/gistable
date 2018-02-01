import arcpy
def pprint_fields(table):
    """ pretty print table's fields and their properties """
    def _print(l):
        print("".join(["{:>12}".format(i) for i in l]))
    atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
            'editable', 'isNullable', 'length', 'precision',
            'required', 'scale',]
    _print(atts)
    for f in arcpy.ListFields(table):
        _print(["{:>12}".format(getattr(f, i)) for i in atts])