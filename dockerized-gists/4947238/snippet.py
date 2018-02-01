import hotshot.stats
import sys
    
DEFAULT_LIMIT = 200

def profile(filename, limit=DEFAULT_LIMIT):
    print "loading profile stats for %s" % filename
    stats = hotshot.stats.load(filename)
    
    # normal stats
    stats.sort_stats('cumulative', 'calls').print_stats(limit)
    
    # stats.strip_dirs()  # this fails! bug in python http://bugs.python.org/issue7372
    # callers
    stats.print_callers(limit)
    #stats.strip_dirs().sort_stats('cumulative', 'calls').print_callers(limit)
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "please pass in a filename."
        sys.exit()
    filename = sys.argv[1] if len(sys.argv) > 1 else "myview-20110922T212250.prof"
    limit = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_LIMIT
    profile(filename, limit)