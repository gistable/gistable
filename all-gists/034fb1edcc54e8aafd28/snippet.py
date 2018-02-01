def ago(elapsed):
	o = []
	
	for unit, size in [("yr",365*24*60*60),("mo",30*24*60*60),("wk",7*24*60*60),("d",24*60*60),("hr",60*60),("min",60),("sec",1)]:
		if size > elapsed: continue
		
		total = int(elapsed / size)
		elapsed = elapsed % size
		
		o.append(str(total) + unit)
	
	return ", ".join(o[0:2]) + " ago"

# usage:
import time
ago(time.time() - post_timestamp) # returns, for example, "1yr, 2mo ago"