from pippi import dsp
from pippi import tune

def play(ctl):
    midi = ctl.get('midi')
    midi.setOffset(111)
    pw = midi.get(1, low=0.01, high=1)

    scale = [1, 2, 3, 6, 9]
    scale = tune.fromdegrees(scale, octave = midi.geti(4, low=0, high=4))

    freq = dsp.randchoose(scale)

    length = dsp.stf(midi.get(2, low=0.1, high=8) * dsp.rand(0.5, 1.5))
    wf = dsp.wavetable('sine2pi')
    win = dsp.wavetable('sine')
    mod = [ dsp.rand(0, 1) for m in range(1000) ]
    modr = midi.get(5, low=0, high=0.3)
    modf = midi.get(6, low=0.001, high=10)
    amp = midi.get(3, low=0, high=1)

    out = dsp.pulsar(freq, length, pw, wf, win, mod, modr, modf, amp)

    out = dsp.env(out, dsp.randchoose(['sine', 'tri']))
    out = dsp.pan(out, dsp.rand())

    return out