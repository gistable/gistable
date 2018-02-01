"""
Example of iterating Bach Chorales and getting individual voice parts
In this case, want specifically 4 voice pieces only
Also transpose to key of C (major or minor depending on piece)
Also shows how to write out all the xml as midi
"""
# Author: Kyle Kastner
# License: BSD 3-Clause
# Based on StackOverflow answer
# http://stackoverflow.com/questions/36647054/music21-getting-all-notes-with-durations
# midi writing modified from tests inside music21
from music21 import corpus, interval, pitch
import time
import numpy as np
import os


def write_midi(pitch_block, duration_block, outfile="out.mid",
               qpm_multiplier=1024, tempo_multiplier=1.0):
    # Assumes any element with
    from music21.midi import MidiTrack, MidiFile, MidiEvent, DeltaTime
    # duration, pitch, velocity

    qpm_mult = qpm_multiplier
    all_mt = []

    for i in range(pitch_block.shape[0]):
        mt = MidiTrack(1)
        t = 0
        t_last = 0
        pitch_slice = pitch_block[i, :]
        duration_slice = duration_block[i, :]
        beat_slice = list((qpm_mult * duration_slice).astype("int32"))
        pitch_slice = list(pitch_slice.astype("int32"))
        for d, p in zip(beat_slice, pitch_slice):
            if (p == -1) or (d == -1):
                # bypass
                continue
            dt = DeltaTime(mt)
            dt.time = t - t_last
            mt.events.append(dt)

            me = MidiEvent(mt)
            me.type = "NOTE_ON"
            me.channel = 1
            me.time = None
            me.pitch = p
            me.velocity = 90
            mt.events.append(me)

            # add note off / velocity zero message
            dt = DeltaTime(mt)
            dt.time = d
            # add to track events
            mt.events.append(dt)

            me = MidiEvent(mt)
            me.type = "NOTE_ON"
            me.channel = 1
            me.time = None
            me.pitch = p
            me.velocity = 0
            mt.events.append(me)
            t_last = t + d
            t += d

        # add end of track
        dt = DeltaTime(mt)
        dt.time = 0
        mt.events.append(dt)

        me = MidiEvent(mt)
        me.type = "END_OF_TRACK"
        me.channel = 1
        me.data = ''
        mt.events.append(me)
        all_mt.append(mt)

    mf = MidiFile()
    mf.ticksPerQuarterNote = int(tempo_multiplier * qpm_mult)
    for mt in all_mt:
        mf.tracks.append(mt)

    mf.open(outfile, 'wb')
    mf.write()
    mf.close()


start = time.time()
all_bach_paths = corpus.getComposer('bach')
print("Total number of Bach pieces to process from music21: %i" % len(all_bach_paths))
skipped = 0
processed = 0
n_major = 0
n_minor = 0
all_major = []
all_minor = []
for it, p_bach in enumerate(all_bach_paths):
    if "riemenschneider" in p_bach:
        # skip certain files we don't care about
        skipped += 1
        continue
    p = corpus.parse(p_bach)
    if len(p.parts) != 4:
        print("Skipping file %i, %s due to undesired voice count..." % (it, p_bach))
        skipped += 1
        continue
    print("Processing %i, %s ..." % (it, p_bach))

    k = p.analyze('key')
    print("Original key: %s" % k)
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    p = p.transpose(i)
    k = p.analyze('key')
    print("Transposed key: %s" % k)
    if 'major' in k.name:
        n_major += 1
    elif 'minor' in k.name:
        n_minor += 1
    else:
        raise ValueError('Unknown key %s' % k.name)

    try:
        parts = []
        parts_times = []
        for i, pi in enumerate(p.parts):
            part = []
            part_time = []
            for n in pi.stream().flat.notesAndRests:
                if n.isRest:
                    part.append(0)
                else:
                    part.append(n.midi)
                part_time.append(n.duration.quarterLength)
            parts.append(part)
            parts_times.append(part_time)

        # Create a "block" of events and times
        cumulative_times = map(lambda x: list(np.cumsum(x)), parts_times)
        event_points = sorted(list(set(sum(cumulative_times, []))))
        maxlen = max(map(len, cumulative_times))
        # -1 marks invalid / unused
        part_block = np.zeros((len(p.parts), maxlen)).astype("int32") - 1
        ctime_block = np.zeros((len(p.parts), maxlen)).astype("float32") - 1
        time_block = np.zeros((len(p.parts), maxlen)).astype("float32") - 1
        # create numpy array for easier indexing
        for i in range(len(parts)):
            part_block[i, :len(parts[i])] = parts[i]
            ctime_block[i, :len(cumulative_times[i])] = cumulative_times[i]
            time_block[i, :len(parts_times[i])] = parts_times[i]

        event_block = np.zeros((len(p.parts), len(event_points))) - 1
        etime_block = np.zeros((len(p.parts), len(event_points))) - 1
        for i, e in enumerate(event_points):
            idx = zip(*np.where(ctime_block == e))
            for ix in idx:
                event_block[ix[0], i] = part_block[ix[0], ix[1]]
                etime_block[ix[0], i] = time_block[ix[0], ix[1]]

        bach_name = "_".join(p_bach.split(os.sep)[-1].split(".")[:-1])
        midi_outfile = bach_name + ".mid"
        write_midi(event_block, etime_block,
                   outfile="midifiles/" + midi_outfile,
                   tempo_multiplier=1.0)
        # Grouping
        processed += 1
    except AttributeError:
        skipped += 1
        # Edge case for Chord error? Should be flat container but some piece is different
        continue

stop = time.time()
print("Total skipped count: %i" % skipped)
print("Total processed count: %i" % processed)
print("Total major: %i" % n_major)
print("Total minor: %i" % n_minor)
print("Total processing time (seconds): %f" % (stop - start))
