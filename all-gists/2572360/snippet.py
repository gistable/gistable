#! /usr/bin/python
import os, re, sys

# Split pg_dump files to schema/type file hierarchy
# Use with files produced by pg_dump -s

#TODO: Identify dropped objects and delete from tree

# Detect object header lines
re_obj = re.compile(r'-- Name: ([-\w\s\.]+)(?:\([-\w\s\[\],]*\))?; Type: ([-\w\s]+); Schema: ([-\w]+); Owner: ([-\w]*)(?:; Tablespace: )?([-\w]*)\n', flags=re.IGNORECASE)

if len(sys.argv) < 2:
    print 'Usage: pg_schema_split infile [outdir]'
    sys.exit()

infile = sys.argv[1]
outdir = os.path.split(sys.argv[0][0])
if len(sys.argv) > 2 : outdir = sys.argv[2]

name, type, schema, owner, tablespace = ['']*5
sql = ''

for line in open(infile,'r').readlines():
    obj = re_obj.match(line)
    if obj:
        ot = re_obj.search(line).group(2)
        if ot not in ('COMMENT', 'SEQUENCE OWNED BY'):  # Keep these in parent script
            if schema != 'pg_catalog' and name > '':
                if schema == '-': schema = 'public'
                type = type.replace(' ','_').lower()

                #print 'Name: %s; Type: %s; Schema: %s; Owner: %s; Tablespace: %s' % (name, type, schema, owner, tablespace or '(default)')
                print 'Schema: %s; Type: %s; Name: %s' % (schema, type, name)

                sqlpath = os.path.join(outdir, schema, type)
                if not os.path.exists(sqlpath):
                    print '*** mkdir %s' % sqlpath
                    os.makedirs(sqlpath)
                sqlf = os.path.join(sqlpath, '%s.sql' % name)

                sql = sql.replace('\n\n','\n')  # Cleanup line spacing
                open(sqlf,'w').write(sql.strip())

            name, type, schema, owner, tablespace = re_obj.search(line).groups()
            sql = ''
    elif line.strip() != '--':  # Skip empty comment lines
        sql += line
