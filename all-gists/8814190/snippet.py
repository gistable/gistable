# Read from Rigol DS1000 scope
# version 1 
# 2013-12-27

import visa
import os, serial
import numpy as np
import pylab as plt
import time

class Scope:
    def __init__(self,address,timeOut=40,chunkSize=1024000):
        self.device = visa.instrument(address,timeout=timeOut,chunk_size=chunkSize)
        self.id = self.device.ask("*idn?")
        self.device.write(":key:lock disable")      # Allows the panel keys on the scope to be used
        self.device.write(":acquire:type normal")
        self.device.write(":acquire:memdepth long")
        self.device.write(":acquire:mode EQUAL_TIME")
        #self.device.write(":acquire:averages 16\n")

    def fastGet(self,channelNumber=1,verbose=False):
        voltscale = self.device.ask_for_values(":CHAN"+`channelNumber`+":SCAL?")[0]
        voltoffset = self.device.ask_for_values(":CHAN"+`channelNumber`+":OFFS?")[0]

        if verbose: 
            print "Voltage scale = ", voltscale, "Voltage offset = ", voltoffset

        samplingrate = self.device.ask_for_values(':ACQ:SAMP? CHANNEL'+`channelNumber`)[0]
        timePerDiv = self.device.ask_for_values(':TIM:SCAL? CHANNEL'+`channelNumber`)[0]
        
        rawdata = self.device.ask(":WAV:DATA? CHAN"+`channelNumber`)[10:]
        data_size = len(rawdata)
        
        if verbose: print 'Data size = ', data_size, "Sample rate = ", samplingrate
        
        data = np.frombuffer(rawdata, 'B')

        V = (240-data) * voltscale/25. - (voltoffset + voltscale*4.6)
        dt = timePerDiv/50.
        t = np.arange(0,len(V)*dt,dt)

        np.arange(len(data)) * 1./samplingrate

        if verbose: print data  
        return t, V


    def getWaveform(self,channelNumber=1,verbose=True):
        """Acquire 1 M samples from channel"""
        # Flush buffer
        self.device.write(":ACQ:MEMD LONG")
        self.device.write(":STOP")       
        self.device.write(":RUN")
        time.sleep(5)
        self.device.write(":STOP") 
        time.sleep(2)
        self.device.write(":STOP")       
        
        self.device.write(":WAVEFORM:POINTS:MODE RAW")
                
        voltscale = self.device.ask_for_values(":CHAN"+`channelNumber`+":SCAL?")[0]
        voltoffset = self.device.ask_for_values(":CHAN"+`channelNumber`+":OFFS?")[0]

        if verbose: 
            print "Voltage scale = ", voltscale, "Voltage offset = ", voltoffset
        
        samplingrate = self.device.ask_for_values(':ACQ:SAMP? CHANNEL'+`channelNumber`)[0]
        rawdata = self.device.ask(":WAV:DATA? CHAN"+`channelNumber`)[10:]
        data_size = len(rawdata)
        
        if verbose: 
            print 'Data size = ', data_size, "Sample rate = ", samplingrate
        
        data = np.frombuffer(rawdata, 'B')
        V = (240-data) * voltscale/25 - (voltoffset + voltscale*4.6)

        t = np.arange(len(data)) * 1./samplingrate

        if verbose: print data  
        return t, V
        

    def recordAverages(self):
        """Log the average voltages"""
        
        V1,V2 = np.array([]), np.array([])
        V = np.array([])
        t = np.array([])

        t0 = time.time()
        ti = time.time()
        tAcq = 2*3600                           # seconds

        while ti < (t0 + tAcq):
            try:
                self.device.write(":MEASURE:VAVERAGE? CH1")
                dataString = self.device.read()
                ti = time.time()
                Vi = float(dataString[:-1])
                time.sleep(1)
            except KeyboardInterrupt:
                print "Acquisition stopped."
                break

            print ti,Vi

            V = np.concatenate( (V,[Vi]) )
            t = np.concatenate( (t,[ti]) )

            if len(t)%100 == 0: I = V/1e6
            DataOut = np.column_stack( (t,I) )
            fileName = date.today().strftime("%y%m%d")+"-beamCurrent"+".log"
            np.savetxt(fileName,DataOut)
    
    def close(self):
        self.device.write("KEY:FORCE")
        self.device.close()