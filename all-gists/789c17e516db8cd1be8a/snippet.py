#!/usr/bin/python2
# coding: utf-8

import re, datetime, random, mido, sys, time

data = {}

def split(seq):
    for i in range(len(seq) - 2):
        yield tuple(seq[i:i+3])

def process(notes):
    for note in split(notes):
        key = note[:2]
        value = note[2]
        data[key] = data.get(key, []) + [value]

def get_next_note(seq):
    notes = tuple(gen_notes(seq[-2:]))
    return random.choice(data.get(notes, []))

mnotes = {}
def get_or_create_note(*args):
    mnotes[args] = mnotes.get(args, mido.Message("note_on", note=args[0], velocity=args[1], time=args[2]))
    return mnotes[args]

def gen_notes(notes):
    for note in notes:
        yield get_or_create_note(note.note, note.velocity, note.time)


if __name__ == "__main__":
    midi = mido.MidiFile(sys.argv[1])
    notes = [note for note in midi.get_messages() if "note_" in note.type]
    new_notes = gen_notes(notes)
    process(list(new_notes))

    out = mido.open_output(mido.get_output_names()[1]) # HARDCODED FOR MY MIDI DEVICE
    onote = notes[4]
    note = notes[5]
    while True:
        time.sleep(note.time/200.0)
        new_note = get_next_note((onote, note))
        out.send(new_note)
        print new_note
        onote = note
        note = new_note