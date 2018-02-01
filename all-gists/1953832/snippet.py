context.REQUEST.response.setHeader('Content-Type', 'text/plain')
print "digraph %s  {" % context.getId()
wf = context
state_to_trans = []
for state in wf.states.values():
    roles = state.getAvailableRoles()
    roles.sort()
    permtable = [ ['<FONT POINT-SIZE="10">%s</FONT>' % _ for _ in ['permission', 'acquired'] + roles ] ]
    for perm in state.getManagedPermissions():
        pinfo = state.getPermissionInfo(perm)
        row = [perm, pinfo['acquired'] and 'X' or '.']
        row += [_ in pinfo['roles'] and 'X' or '.' for _ in roles]
        permtable.append(row)
    table = '<TABLE BORDER="0"><TR><TD colspan="%s" bgcolor="lightgrey"><B>%s</B></TD></TR>\n' % (len(roles)+2, state.title or state.getId())
    cnt = 1
    for row in permtable:
        cnt += 1
        table += '<TR>'
        bgcolor = cnt % 2 and ' BGCOLOR="lightyellow"' or ''
        for cell in row:
            table += '<TD%s><FONT POINT-SIZE="10">%s</FONT></TD>' % (bgcolor, cell)
        table += '</TR>\n'
    table += '</TABLE>'
    print '%s [label=<%s> shape=Mrecord];' % (state.getId(), table)

    for trans in state.transitions:
        state_to_trans.append((state.getId(), trans))

for state, trans in state_to_trans:
    tob = wf.transitions[trans]
    table = '<TABLE BORDER="0" BGCOLOR="lightgrey"><TR><TD colspan="2">%s</TD></TR>\n' % tob.title
    proptable = [ ['id' , trans] ]
    cnt = 0
    for key, value in proptable:
        bgcolor = cnt % 2 and ' BGCOLOR="lightyellow"' or ''
        table += '<TR>'
        table += '<TD%s><FONT POINT-SIZE="10">%s:</FONT></TD>' % (bgcolor, key)
        table += '<TD%s ALIGN="LEFT"><FONT POINT-SIZE="10">%s</FONT></TD>' % (bgcolor, value)
        table += '</TR>\n'
    table += '</TABLE>'
    print '"%s" -> "%s" [label=<%s>, arrowhead=normal, arrowtail=inve];' % (state, tob.new_state_id, table)
print "}"
return printed
