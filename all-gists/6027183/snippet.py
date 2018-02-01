#!/usr/bin/python

""" Download an IR remote signal from a Rigol DS1052E and
analyze it for a NEC protocol signal.

Ken Shirriff
http://righto.com
""" 
import array
import sys
import time
import visa

# Get the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
instruments = visa.get_instruments_list()
usb = filter(lambda x: 'USB' in x, instruments)
if len(usb) != 1:
    print 'Bad instrument list', instruments
    sys.exit(-1)
scope = visa.instrument(usb[0], timeout=20, chunk_size=1024000) # bigger timeout for long mem

# Oscilloscope can get confused if too many commands arrive too fast
def scopewrite(str):
    scope.write(str)
    time.sleep(.1)

# Set the scope the way we want it
scopewrite(':ACQ:MEMD LONG') # Long memory type
scopewrite(':CHAN1:COUP DC') # DC coupling
scopewrite(':CHAN1:DISP ON') # Channel 1 on
scopewrite(':CHAN2:DISP OFF') # Channel 1 off
scopewrite(':CHAN1:SCAL 1') # Channel 1 vertical scale 1 volts
scopewrite(':CHAN1:OFFS -2') # Channel 1 vertical offset 2 volts
scopewrite(':TIM:SCAL .01') # 10ms time interval
scopewrite(':TIM:OFFS .05') # Offset time 50 ms

scopewrite(':TRIG:EDGE:SOUR CHAN1') # Edge-trigger from channel 1
scopewrite(':TRIG:EDGE:SWE SING') # Single trigger
scopewrite(':TRIG:EDGE:COUP DC') # DC trigger coupling
scopewrite(':TRIG:EDGE:SLOP NEG') # Trigger on negative edge
scopewrite(':TRIG:EDGE:LEV 2.5') # Trigger at 2.5 volts

# Get the sample rate for processing the input data
sample_rate = scope.ask_for_values(':ACQ:SAMP?')[0]
while 1:
    scopewrite(":RUN")
    while scope.ask(':TRIG:STAT?') != 'STOP':
        time.sleep(.2)

    # Grab the raw data from channel 1, which will take about 10 seconds
    scopewrite(":STOP")
    scopewrite(":WAV:POIN:MODE RAW")
    rawdata = scope.ask(":WAV:DATA? CHAN1")

    # Convert data into high/low values, keeping in mind that rawdata is inverted
    # First 10 bytes are header
    data = array.array('B', rawdata[10:])
    data = map(lambda x: x < 128, data)

    # Decode an IR signal in NEC protocol
    # For an explanation, see
    # http://wiki.altium.com/display/ADOH/NEC+Infrared+Transmission+Protocol
    def decode():
        # Process data into list of milliseconds high, milliseconds low, milliseconds high, etc.
        regions = []
        state = data[0]
        pos = 0
        for i in range(1, len(data)):
            if data[i] != state:
                regions.append((i - pos) * 1000. / sample_rate)
                pos = i
                state = data[i]

        if len(regions) < 64 or data[0] != True:
            raise Exception('Wrong number of regions: %s' % regions)

        # Make sure the received length is within 30% of the expected length
        # Otherwise throw an exception
        def expect(received, expected):
            if received < .7 * expected or received > 1.3 * expected:
                raise Exception('Wanted length %f vs %f\n%s' % (received, expected, regions))

        # Process the header and 32 bits of data in the IR message
        result = 0
        expect(regions[1], 9) # 9 ms header mark
        expect(regions[2], 4.5) # 4.5ms header space
        for i in range(0, 32): # Loop over 32 bits
            expect(regions[3 + 2*i], .5625) # 562.5 microseconds mark
            if regions[4 + 2*i] > 1.000: # If more than 1 millisecond, must be a 1
                expect(regions[4 + 2*i], 1.6875) # 1.6875ms mark for 1 bit
                result = (result << 1) | 1
            else:
                expect(regions[4 + 2*i], .5625) # 562.5 us mark for 0 bit
                result = result << 1
        return result

    try:
        print '%x' % decode()
    except Exception, e:
        print 'Decode failed', e
