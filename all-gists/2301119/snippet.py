import time
import datetime
import visa
import numpy as np

class YokogawaWT1600(visa.GpibInstrument):
  __GPIB_ADDRESS = 2
  
  def __init__(self, reset=True):
    visa.GpibInstrument.__init__(self, self.__GPIB_ADDRESS, timeout=3)
    if reset:
      self.resetDefault()

  def resetDefault(self):
    def setupMeasurements(measurements):
      num = range(1, len(measurements) + 1)
      for n, m in zip(num, measurements):
        s = "item{0} {1},1".format(n, m) #item{0} {1},1 | item{0} {1},2
        yield s

    print "Resetting the Yokogawa WT1600..."
    measureItems = ["URMS", "IRMS", "S", "P", "LAMBda", "WH", "AH", "TIME"]
    self.write("*RST")
    time.sleep(5)
    self.write("*CLS")
    self.ask("*IDN?")
    s = [":rate 1",
         ":input:voltage:range:element1 300", #element1 300   | element2 300
         ":input:current:range:element1 500MA", #element1 500MA | element2 10A
         ":display:numeric:normal:iamount {0}".format(len(measureItems)),
         ";".join(setupMeasurements(measureItems)),
         ":numeric:normal:number {0}".format(len(measureItems)),
         ";".join(setupMeasurements(measureItems)),
         ":store:memory:initialize",
         ":store:direction memory",
                "interval 0,0,0",
                "item numeric",
                "smode integrate",
                "mode store",
                "numeric:normal:all off",
                               "element1 on", #element1 on | element2 on
                               ";".join(["{0} ON".format(m) for m in measureItems])]
    self.write(";".join(s))

  def queryMeasurements(self):
    """Returns a list of 8 measurements seen on the preset display:
       URMS, IRMS, S, P, LAMBda, WH, AH, TIME
    """
    values = self.ask(":numeric:normal:value?")
    values = values.split(',')
    data = [float(i) for i in values]
    return data

  def getIntegrateState(self):
    return self.ask(":integrate:state? 1")

  def startIntegrator(self):
    """Returns integrator startTime.
    """
    if self.getIntegrateState() != "RES": self.resetIntegrator()
    print "\nStarting integrator...\n"
    self.write(":integrate:independent OFF; start")
    integrateStartTime = time.time()
    if self.getIntegrateState() == "STAR": print "Integrator has started."
    return integrateStartTime

  def stopIntegrator(self):
    if self.getIntegrateState() == "STAR":
      print "\nStopping integrator...\n"
      self.write(":integrate:stop")
      time.sleep(1)
    state = self.getIntegrateState()
    if state == "STOP": print "Integrator has stopped."
    elif state == "RES": print "Integrator has reset."

  def resetIntegrator(self):
    if self.getIntegrateState() != "STOP": self.stopIntegrator()
    print "\nResetting integrator...\n"
    self.write(":integrate:reset")
    if self.getIntegrateState() == "RES": print "Integrator has reset."

  def storeReady(self, duration):
    """duration is in minutes
    """
    storeCount = duration * 60 # based on 1s update rate
    def convertDuration(duration):
      duration = float(duration)
      h = s = 0
      m = duration
      if duration > 59:
        h = duration / 60
        m = (h - int(h)) * 60
      return "{0:02},{1:02},{2:02}".format(int(h), int(m), s)
    self.stopIntegrator()
    self.resetIntegrator()
    s = [":store:memory:initialize",
         ":store:count {0}".format(storeCount),
         ":integrate:timer {0}".format(convertDuration(duration)),
         ":store:mode store",
         ":store:start"]
    self.write(";".join(s))

  def recallMemory(self):
    self.resetIntegrator()
    self.write(":store:mode recall")
    dataCount = int(self.ask_for_values(":store:count?").pop())
    for n in range(1, dataCount + 1):
      self.write(":store:recall {0}".format(n))
      data = self.queryMeasurements()

      TIME         = "{0:>10.3f}".format(data[7])
      VOLTAGE      = "{0}".format(data[0]) if not np.isinf(data[0]) else "Out of range"
      CURRENT      = "{0}".format(data[1]) if not np.isinf(data[1]) else "Out of range"
      APPARENT_PWR = "{0}".format(data[2]) if not np.isinf(data[2]) else "Out of range"
      TRUE_PWR     = "{0}".format(data[3]) if not np.isinf(data[3]) else "Out of range"
      PF           = "{0}".format(data[4]) if not np.isinf(data[4]) else "Out of range"
      WATT_HR      = "{0}".format(data[5]) if not np.isinf(data[5]) else "Out of range"
      AMP_HR       = "{0}\n".format(data[6]) if not np.isinf(data[6]) else "Out of range"

      s = [TIME, VOLTAGE, CURRENT, APPARENT_PWR, TRUE_PWR, PF, WATT_HR, AMP_HR]
      s = ",".join(s)
      yield s
    self.write(":store:mode store")