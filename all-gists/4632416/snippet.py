"""
combine.py

alternate between two audiofiles, beat by beat

By Paul Lamere, 2013-01-25
"""
import echonest.audio as audio

usage = """
Usage: 
    python combine.py <input_filename> <input_filename2) <output_filename>

Example:
    python combine.py jc-bgb.mp3 glee-bgb.mp3 combined.mp3
"""

offset = 1
def main(input_filename1, input_filename2, output_filename):
    audiofile1 = audio.LocalAudioFile(input_filename1)
    audiofile2 = audio.LocalAudioFile(input_filename2)

    beats1 = audiofile1.analysis.beats
    beats2  = audiofile2.analysis.beats

    l = min([len(beats1), len(beats2)])

    collect = audio.AudioQuantumList()
    out = None
    for i in xrange(l):
        if i % 2 == 1:
            beat = beats1[i - offset]
            next = audio.getpieces(audiofile1, [beat])
        else:
            beat = beats2[i]
            next = audio.getpieces(audiofile2, [beat])
        if out == None:
            out = next
        else:
            out.append(next)

    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        input_filename1 = sys.argv[1]
        input_filename2 = sys.argv[2]
        output_filename = sys.argv[3]
    except:
        print usage
        sys.exit(-1)
    main(input_filename1, input_filename2, output_filename)