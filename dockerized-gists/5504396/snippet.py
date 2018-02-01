import happybase, sys, os, string

# VARIABLES
# Output directory for CSV files
outputDir = "/mnt"
# HBase Thrift server to connect to. Leave blank for localhost
server = ""

# Connect to server
c = happybase.Connection(server)

# Get the full list of tables
tables = c.tables()

# For each table in the tables
for table in tables:
  # Open file to write to
  file = open(outputDir + "/" + table + ".csv", "w")

  t = c.table(table)

  print table + ": ",
  count = 0

  # For each row key
  for prefix in string.printable:
    try:
      for key, data in t.scan(row_prefix=prefix):
        # First key
        if count == 0:
          startRow = key

        # Each column
        for col in data:
          value = data[col]
          column = col[col.index(":")+1:]

          # Write row, column, value to file
          file.write("%s, %s, %s\n" % (key, column, value))
        count += 1
    except:
        os.system("hbase-daemon.sh restart thrift")
        c = happybase.Connection(server)
        t = c.table(table)
        continue

  # Last key
  endRow = key

  print "%s => %s, " % (startRow, endRow),
  print str(count)