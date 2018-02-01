from pykd import * 

kernel32 = module("kernel32")
ntdll = module("ntdll")

ip = 0

if is64bitSystem():
    ip = reg("rip")
else:
    ip = reg("eip")

while (
            (
                kernel32.begin() < ip
                and ip < kernel32.end()
            )
        or
            (
                ntdll.begin() < ip
                and ip < ntdll.end()
            )
      ):
    trace()