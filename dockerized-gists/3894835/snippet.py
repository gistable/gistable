def unserialize_session(val):
    if not val:
        return
    session = {}
    groups = re.split("([a-zA-Z0-9_]+)\|", val)
    if len(groups) > 2:
        groups = groups[1:]
        groups = map(None, *([iter(groups)] * 2))
    
        for i in range(len(groups)):
            session[groups[i][0]] = phpserialize.loads(groups[i][1])
    return session