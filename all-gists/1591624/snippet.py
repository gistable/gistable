import string, sys, os

tt = string.maketrans(string.punctuation,'_'*len(string.punctuation))

for fname in sys.argv[1:]:
	hname = os.path.split(fname)[-1].upper().translate(tt)
	head_str = '#ifndef ' + hname + '\n#define ' + hname+'\n'
	tail_str = '\n#endif //' + hname + '\n'

	dt = file(fname).read()
	head_is = (dt.strip().find(head_str.strip()) >= 0)
	if head_is:
		head_str = ''
	tail_is = (dt.strip().find(tail_str.strip()) >= 0)
	if tail_is:
		tail_str = ''
	

	if not head_is or not tail_is:
		file(fname,'wt').write(head_str + dt + tail_str )
