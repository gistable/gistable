def extract_base_data(d, t):
 l = []
 for k,v in d.iteritems():
  if type(v) is not t:
   l+=extract_base_data(v)
  else:
 l+=v
 return l