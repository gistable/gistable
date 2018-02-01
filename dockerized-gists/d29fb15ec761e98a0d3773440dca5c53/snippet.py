# script to extract music from a pico-8
# requires exporting sounds from the pico-8 first!
# run as: python extract-music.py mygame.p8 sound%d.wav music%d.wav
# by eevee, do what you like with this code
from __future__ import print_function
import argparse
import struct
import wave


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cartfile', help='path to the cartridge file (.p8)')
    parser.add_argument('soundfiles', help='pattern you used to export from the PICO-8, e.g. sound%%d.wav')
    parser.add_argument('musicfiles', help='pattern for saving music tracks to, e.g. music%%d.wav')
    args = parser.parse_args()

    print("reading music definitions")
    musicdefs = []
    with open(args.cartfile) as f:
        for line in f:
            if line.strip() == '__music__':
                break
        else:
            raise ValueError("can't find music marker in cartridge!")

        for n, line in enumerate(f):
            line = line.strip()
            if not line:
                break

            rbits, rtracks = line.split()
            bits = int(rbits, 16)
            tracks = []
            for t in range(4):
                track = int(rtracks[t*2:t*2+2], 16)
                if track & 64:
                    continue
                tracks.append(track)
            musicdefs.append((bits, tracks))

            #print(n, 'F' if bits & 1 else '-', 'B' if bits & 2 else '-', 'S' if bits & 4 else '-', *["{:02d}".format(track) if enabled else '--' for (enabled, track) in tracks])

    print("reading sound files")
    sound_samples = []
    params = None
    for n in range(64):
        with wave.open(args.soundfiles.replace('%d', str(n)), 'rb') as wav:
            params = wav.getparams()
            assert params.sampwidth == 2
            assert params.framerate == 22050
            sound_samples.append(struct.unpack(
                "<{}h".format(params.nframes),
                wav.readframes(params.nframes),
            ))

    print("mixing music tracks")
    track_samples = {}
    for m, (bits, tracks) in enumerate(musicdefs):
        if not tracks:
            continue

        # TODO how does this work if one of the shorter streams doesn't divide evenly into the longest?
        nframes = max(len(sound_samples[t]) for t in tracks)
        frames = []
        for n in range(nframes):
            sample = sum(
                sound_samples[t][n % len(sound_samples[t])]
                for t in tracks)
            frames.append(sample)

        # Ensure the sounds are loopable without a pop (a discontinuity) by
        # lerping the last 61 samples (1/3 of a note at maximum speed) to
        # zero.  This turns out to be exactly what the PICO-8 does, which I
        # discovered entirely on accident, but the PICO-8 only does it at
        # the beginning of an exported sound and not at the end.  (Since
        # this track is just the sum of multiple sounds, we shouldn't have
        # to worry about the beginning.)
        crossfade_range = 61
        for i in range(crossfade_range):
            t = i / crossfade_range
            frames[i - crossfade_range] = round((1 - t) * frames[i - crossfade_range])

        track_samples[m] = struct.pack("<{}h".format(nframes), *frames)

        # For debugging, you can also write out the individual tracks
        #with wave.open("track{}.wav".format(m), 'wb') as outwav:
        #    outwav.setparams(params)
        #    outwav.writeframes(track_samples[m])

    it = iter(enumerate(musicdefs))
    while True:
        first = None
        these_tracks = []
        curloop = None
        for m, (bits, tracks) in it:
            if not tracks:
                # TODO unclear what should happen here exactly
                continue
            these_tracks.append(m)
            if bits & 1:
                curloop = []
            if curloop is not None:
                curloop.append(m)
            if bits & 2:
                # loop back
                break
            if bits & 4:
                # stop
                curloop = []
                break

        if not these_tracks:
            break

        if curloop:
            these_tracks.extend(curloop)
            these_tracks.extend(curloop)
            # TODO probably would be better to just ask for a minimum total length
            if these_tracks[0] == 28:
                these_tracks.extend(curloop)
                these_tracks.extend(curloop)
                these_tracks.extend(curloop)
                these_tracks.extend(curloop)

        musicfile = args.musicfiles.replace('%d', str(these_tracks[0]))
        print("writing", musicfile)
        with wave.open(musicfile, 'wb') as outwav:
            outwav.setparams(params)
            for m in these_tracks:
                outwav.writeframes(track_samples[m])

    print("done!")


if __name__ == '__main__':
    main()