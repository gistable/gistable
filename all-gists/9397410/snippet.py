from execute import execute, Retcode

def dd(ifile, ofile, bs, count=None, seek=None):
    """
    Wrapper for the GNU dd command.
    
    Inputs:
        ifile (str): Input file
        ofile (str): Output file
        bs    (str): Block size
        count (str): Number of blocks to copy
        seek  (str): Seek x blocks
    Outputs:
        time (float): Duration
        tput (float): Throughput in MiB/s
        iops (float): IOPS
    """
    # Execute dd command
    cmd = "dd if=%s of=%s bs=%s" % (ifile, ofile, bs)
    if count is not None:
        cmd = " ".join([cmd, "count=%s" % count])
    if seek is not None:
        cmd = " ".join([cmd, "seek=%s" % seek])
    try:
        retcode, output = execute(cmd)
    except:
        raise
    else:
        if retcode:
            raise Retcode(output)
    
    # Split lines into fields
    records_in, records_out, summary = output.split("\n")

    # Parse for record counts
    # If we run out of disk space requested vs actual will vary
    s = re.search(r"^([0-9]*)\+.*", records_in)
    records_in = int(s.group(1))
    s = re.search(r"^([0-9]*)\+.*", records_out)
    records_out = int(s.group(1))

    # There is no reason the record counts should not match but if they
    # do raise an exception because it will effect calculations.
    if records_in != records_out:
        raise Exception('records mismatch')

    # Parse for the byte total and time
    s = re.search(r"^([0-9]*).*([0-9]+\.[0-9]+) s", summary)
    size = int(s.group(1))
    time = float(s.group(2))
    
    # Calculate throughput in Mib, i.e. base 2
    # Note that dd returns base 10 calcaulation
    tput = size / time / 1024**2 

    # Calculate IOPS
    iops = records_in / time
    
    return time, tput, iops