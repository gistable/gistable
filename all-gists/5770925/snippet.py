def zipdict(names, values):
    return dict(zip(names, values))

def unzipdict(mydict):
    list1 = mydict.keys()
    list2 = mydict.values()
    return list1, list2