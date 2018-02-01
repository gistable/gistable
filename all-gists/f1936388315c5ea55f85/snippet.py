# Automatically find XOR/SHL/SHR routines from an executable
# Uses IDAW (text IDA)
# @bbaskin - brian @ thebaskins.com
# While other, more powerful scripts like FindCrypt find known
# algorithms this is used to find custom encoding or modified
# encryption routines

""" 
Script results:
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
sub_402E51	shr	eax, 1
sub_402E51	xor	eax, 0EDB88320h
sub_402E51	shr	eax, 1
sub_402E51	shr	eax, 8
sub_402E51	xor	eax, dword_4161C0[ebx*4]
sub_402EBB	xor	edx, edi
sub_402EBB	shr	eax, 8
sub_402EBB	xor	eax, dword_4161C0[edx*4]
sub_402EBB	shr	edi, 3
sub_402EBB	xor	eax, [ecx]
sub_402EBB	shr	ebx, 10h
sub_402EBB	shr	edx, 18h
sub_402EBB	xor	edx, dword_4175C0[ebx*4]
sub_402EBB	shr	ebx, 8
sub_402EBB	xor	edx, dword_4179C0[ebx*4]
sub_402EBB	xor	edx, dword_4165C0[ebx*4]
sub_402EBB	xor	edx, dword_4169C0[ebx*4]
sub_402EBB	xor	edx, dword_416DC0[ebx*4]
sub_402EBB	xor	edx, dword_4161C0[ebx*4]
sub_402EBB	xor	edx, dword_417DC0[eax*4]
sub_402EBB	xor	edx, edi
sub_402EBB	shr	eax, 8
sub_402EBB	xor	eax, dword_4161C0[edx*4]
"""

from argparse import ArgumentParser
import os
import subprocess
import sys
#IDA_EXE = 'C:\Program Files (x86)\IDA 6.95\idaw.exe'
#IDA_EXE = 'C:\Program Files\IDA 7.0\idat.exe'
IDA_EXE = 'C:\Program Files\IDA 7.0\idat64.exe'
IDA_ARGS = ' -A -B '
IDA_CMD = '"%s" %s' % (IDA_EXE, IDA_ARGS)
#sep = '\t'  # Use for IDA 6
sep = '    ' # Use for IDA 7

def file_exists(fname):
    """
    Determine if a file exists

    Arguments:
        fname: path to a file
    Results:
        boolean value if file exists
    """
    return os.path.exists(fname) and os.access(fname, os.X_OK)

    
def CreateASM(exefile, exefile_asm):
    """
    Use IDA Pro text (idaw) to create an ASM dump of the PE file

    Arguments:
        exefile: path to PE file
        exefile_asm: output ASM file
    """
    print '[*] Creating %s' % (exefile_asm)
    cmdline = IDA_CMD + exefile
    result = subprocess.Popen(cmdline)
    result.wait()

    if not file_exists(exefile_asm):
        print('\n\n' + '-=' * 20 + '-')
        print('[!] Could not find ASM file: {}'.format(exefile_asm))
        print('[!] If the following is shown above, adjust DOS screen buffer height to < 300:')
        print('>>> Fatal error: the window is too high (max 300 rows)!')
    quit()


        
def ScanASM(data, find_shifts):
    """
    Process ASM data to find XOR/SHL/SHR
    
    Arguments:
        data: contents of ASM file
    """
    
    print 'Script results:'
    print '-=' * 20 + '-'
    # Unknown_Sub is for when IDA could not identify initial subroutines
    currentsub = 'Unknown_Sub'

    for line in data:
        if line.startswith('sub_'):
            currentsub = line.split()[0]
        if 'xor' + sep in line:
            items = line.split()
            if items[1].strip(",") != items[2]:
                print currentsub + '\t' + line.strip()
        if find_shifts:
            if 'shl' + sep in line or 'shr' + sep in line:
                print currentsub + '\t' + line.strip()

def main():
    if not file_exists(IDA_EXE):
        print('Cannot find IDA: {}'.format(IDA_EXE))
        quit()

    parser = ArgumentParser()
    parser.add_argument('exefile')
    parser.add_argument('-s', help='Display shift operations', required=False, action='store_true')
    args = parser.parse_args()

    if not args.exefile:
        print('[!] Specify executable to scan on the command line')
        quit()
    else:
        exefile = args.exefile
    
    exefile_asm = os.path.splitext(exefile)[0] + '.asm'
    if not file_exists(exefile_asm):
        CreateASM(exefile, exefile_asm)
    else:
        print('[*] ASM file already found: {}'.format(exefile_asm))

    data = open(exefile_asm, 'r').readlines()
    find_shifts = True if args.s else False
    ScanASM(data, find_shifts)
            
if __name__ == '__main__':
    main()