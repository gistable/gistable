# Based on code from Jose Sotelo
# Author: Kyle Kastner
# License: BSD 3-Clause
from __future__ import print_function
import os
import shutil
import subprocess
import stat

vctkdir = "/Tmp/kastner/vctk/VCTK-Corpus/"
if vctkdir[-1] != "/":
    vctkdir = vctkdir + "/"

# Convenience function to reuse the defined env
def pwrap(args, shell=False):
    p = subprocess.Popen(args, shell=shell, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    return p

# Print output
# http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
def execute(cmd, shell=False):
    popen = pwrap(cmd, shell=shell)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def pe(cmd, shell=False):
    """
    Print and execute command on system
    """
    for line in execute(cmd, shell=shell):
        print(line, end="")

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass  # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract audio and text features using speech synthesis toolkits including SPTK, HTS, HTK, and Merlin. Special thanks to Jose Sotelo and the Edinburgh Speech Synthesis team.",
                                     epilog="Example usage: python get_vctk_speakers.py -s American")
    parser.add_argument("--speaker_type", "-s",
                        help="Speaker type to extract from vctk",
                        required=True)
    args = parser.parse_args()
    speaker_match = args.speaker_type
    with open(vctkdir + 'speaker-info.txt') as f:
        speaker_data = f.readlines()

    valid_matches = ["American"]
    launchdir = os.getcwd()
    if speaker_match == "American":
        # get the ids, make the directory, chdir into it
        speakers = [x.split(' ')[0] for x in speaker_data if 'American' in x]
        # 315 has a lot of missing data.
        speakers = [x for x in speakers if x != '315']
        if not os.path.exists("vctk_American_speakers"):
            os.mkdir("vctk_American_speakers")
        os.chdir("vctk_American_speakers")
    else:
        raise AttributeError("Gave speaker_type=%s, but fetching speakers other than %s currently unsupported!" % (speaker_match, valid_matches))

    # be sure the switch argument changed to its own local dir
    assert launchdir != os.getcwd()

    if not os.path.exists("wav"):
        os.mkdir("wav")
    if not os.path.exists("txt"):
        os.mkdir("txt")

    # Common logic
    for sp in speakers:
        print("Copying data for %s" % sp)
        wavdir = vctkdir + "wav48/p%s" % sp
        txtdir = vctkdir + "txt/p%s" % sp
        copytree(wavdir, "wav")
        copytree(txtdir, "txt")
    from IPython import embed; embed()
    raise ValueError()
