# Based on code from Jose Sotelo
# Author: Kyle Kastner
# License: BSD 3-Clause
from __future__ import print_function
import os
import shutil
import subprocess
import stat

def get_wav_text(subdir, master_transcript=None):
    # master transcript check is to correct messed up text -> wav mapping in
    # certain dirs :|
    if subdir[-1] != "/":
        subdir += "/"
    files = os.listdir(subdir)
    wav_files = [subdir + f for f in files if ".wav" in f]
    # backup .txt files also in dir with ~???
    txt_files = [f for f in files if ".txt" in f and ".txt~" not in f]
    if len(txt_files) < 1:
        # use the backup file for certain people... :|
        txt_files = [f for f in files if ".txt" in f]
    assert len(txt_files) == 1
    txt_file = txt_files[0]
    with open(subdir + txt_file, "r") as f:
        lines = f.readlines()

    # remove weird (2) and (3) thing
    lines = [l.strip().replace("(2)", "`") for l in lines]
    lines = [l.strip().replace("(3)", "```") for l in lines]

    # sorted
    """
    for fi in wav_files:
        # nasty edge case when one file has double underscore "__"
        int(fi.split("/")[-1].split(".")[0].split("_")[-1])
    """
    wav_files = sorted(wav_files, key=lambda x: int(x.split("/")[-1].split(".")[0].split("_")[-1]))

    # Force a lookup for the one with a blank line...
    lines = [l for l in lines if len(l) > 0]

    if len(wav_files) == len(lines):
        return wav_files, lines
    else:
        with open(master_transcript, "r") as f:
            ll = f.readlines();

        speaker_name = str(txt_file[:-4])
        master_names = [lil.strip().split(">")[-1].split("(")[1].split(")")[0] for lil in ll]
        master_lines = [lil.strip().split(">")[1][1:].split("<")[0][:-1] for lil in ll]
        master_lines = [l.strip().replace("(2)", "`") for l in master_lines]
        master_lines = [l.strip().replace("(3)", "```") for l in master_lines]
        name_to_line = {k: v for k, v in zip(master_names, master_lines)}

        match_lines = []
        missing_indices = []
        for n, w in enumerate(wav_files):
            try:
                match_lines.append(name_to_line[w.split("/")[-1].split(".")[0]])
            except KeyError:
                print("No matching text for key %s" % w)
                missing_indices.append(n)
        new_wav_files = [w for n, w in enumerate(wav_files)
                         if n not in missing_indices]
        wav_files = new_wav_files
        return wav_files, match_lines


def write_out_wav_text(wav_paths, text_lines, tag=None):
    if not os.path.exists("wav"):
        os.mkdir("wav")
    if not os.path.exists("txt"):
        os.mkdir("txt")
    assert len(wav_paths) == len(text_lines)
    for wf, tx in zip(wav_paths, text_lines):
        wav_name = wf.split("/")[-1]
        txt_name = wav_name.split(".")[0] + ".txt"
        if tag is not None:
            wav_save = "wav/" + str(tag) + "_" + wav_name
            txt_save = "txt/" + str(tag) + "_" + txt_name
        else:
            wav_save = "wav/" + wav_name
            txt_save = "txt/" + txt_name
        shutil.copy2(wf, wav_save)
        with open(txt_save, "w") as f:
            f.write(tx)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract audio and text to correct directory structure.",
                                     epilog="Example usage: python get_bangla_speakers.py")
    wdir = os.getcwd()
    out_dir = "bangla_speakers"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    os.chdir(out_dir)

    basedir = "/Tmp/kastner"
    if basedir[-1] != "/":
        basedir += "/"

    bangla_base_dir = basedir + "bangla_speech/"
    bangla_main_dir = bangla_base_dir + "SHRUTI-Bangla Speech Corpus/"

    master_transcript = bangla_main_dir + "etc/shruti_train.transcription"

    wav_main_dir = bangla_main_dir + "WAV/"
    wav_male_dir = wav_main_dir + "MALE/"
    wav_male_subdirs = os.listdir(wav_male_dir)

    for subdir in wav_male_subdirs:
        print("Writing out male %s..." % subdir)
        full_subdir = wav_male_dir + subdir
        wav_paths, text_lines = get_wav_text(full_subdir, master_transcript)
        write_out_wav_text(wav_paths, text_lines, tag="%s_%s" % ("male", subdir))

    wav_female_dir = wav_main_dir + "FEMALE/"
    wav_female_subdirs = os.listdir(wav_female_dir)

    for subdir in wav_female_subdirs:
        print("Writing out female %s..." % subdir)
        full_subdir = wav_female_dir + subdir
        wav_paths, text_lines = get_wav_text(full_subdir, master_transcript)
        write_out_wav_text(wav_paths, text_lines, tag="%s_%s" % ("female", subdir))
