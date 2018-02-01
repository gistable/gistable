import sys
import pexpect

def setpassword(read_write_password, read_only_password=None):
    p = pexpect.spawn("vncpasswd")
    # Uncomment the next line if you want to see the standard output
    #p.logfile = sys.stdout

    if read_write_password:
        print ("Setting read-write password")
        p.expect("Password:")
        p.sendline(read_write_password)
        p.expect("Verify:")
        p.sendline(read_write_password)

    if read_only_password:
        print ("Setting read-only password")
        p.expect("view-only password (y/n)?")
        p.sendline("y")

        p.expect("Password:")
        p.sendline(read_only_password)
        p.expect("Verify:")
        p.sendline(read_only_password)
        p.sendline()
    else:
        p.expect("view-only password (y/n)?")
        p.sendline("n")
        p.sendline()

if __name__ == '__main__':
    #TODO/FIXME: Use an arg parsing library here
    if len(sys.argv) == 1:
        print ("Usage: vncpasswd.py <read-write-password> [<read-only-password>]")
        sys.exit(1)
    
    rw_password = sys.argv[1]
    if len(sys.argv) == 3:
        r_password = sys.argv[2]
    else:
        r_password = None
    
    setpassword (rw_password, r_password)
