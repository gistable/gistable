def foo(s_, i_ = 0):
	strLen = len(s_)
	if strLen == 0:
		return False
	if i_ < 0:
		return False
	if i_ == (strLen / 2 - 1):
		return s_[i_] == s_[strLen - 1 - i_]
	return (s_[i_] == s_[strLen - 1 - i_] and foo(s_, i_ + 1))

if __name__ == "__main__":
	s = 'madam'
	print foo(s)