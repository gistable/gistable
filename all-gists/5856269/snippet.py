import blpapi
import datetime

class BbDownloader:
    def __init__(self):
        self.output_file = ""
        self.TICK_DATA = blpapi.Name("tickData")
        self.COND_CODE = blpapi.Name("conditionCodes")
        self.TICK_SIZE = blpapi.Name("size")
        self.TIME = blpapi.Name("time")
        self.TYPE = blpapi.Name("type")
        self.VALUE = blpapi.Name("value")
        self.RESPONSE_ERROR = blpapi.Name("responseError")
        self.CATEGORY = blpapi.Name("category")
        self.MESSAGE = blpapi.Name("message")
        self.SESSION_TERMINATED = blpapi.Name("SessionTerminated")
    
    
    def write_tick_data(self, output_filename, security, start_date, end_date):
        self.output_file = open(output_filename, "w")
        
        # Fill SessionOptions
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost("localhost")
        sessionOptions.setServerPort(8194)
        session = blpapi.Session(sessionOptions)
    
        # Start a Session
        if not session.start():
            print "Failed to start session."
            return
    
        try:
            # Open service to get historical data from
            if not session.openService("//blp/refdata"):
                print "Failed to open //blp/refdata"
                return
    
            self.sendIntradayTickRequest(session, security, start_date, end_date)
    
            # wait for events from session.
            self.eventLoop(session)
    
        finally:
            self.output_file.flush()
            session.stop()
            print "Finished"
    
    
    def sendIntradayTickRequest(self, session, security, start_date, end_date):
        refDataService = session.getService("//blp/refdata")
        request = refDataService.createRequest("IntradayTickRequest")
    
        # only one security/eventType per request
        request.set("security", security)
    
        # Add fields to request
        eventTypes = request.getElement("eventTypes")
        for event in ["ASK", "BID", "TRADE"]:
            eventTypes.appendValue(event)
    
        # All times are in GMT
        request.set("startDateTime", start_date)
        request.set("endDateTime", end_date)
        request.set("includeConditionCodes", True)
            
        print "Sending Request:", request
        session.sendRequest(request)


    def eventLoop(self, session):
        done = False
        while not done:
            # nextEvent() method below is called with a timeout to let
            # the program catch Ctrl-C between arrivals of new events
            event = session.nextEvent(500)
            if event.eventType() == blpapi.Event.PARTIAL_RESPONSE:
                self.processResponseEvent(event)
            elif event.eventType() == blpapi.Event.RESPONSE:
                self.processResponseEvent(event)
                done = True
            else:
                for msg in event:
                    if event.eventType() == blpapi.Event.SESSION_STATUS:
                        if msg.messageType() == self.SESSION_TERMINATED:
                            done = True

                        
    def processResponseEvent(self, event):
        for msg in event:
            if msg.hasElement(self.RESPONSE_ERROR):
                print msg.getElement(self.RESPONSE_ERROR)
                continue
            self.processMessage(msg)

        
    def processMessage(self, msg):
        data = msg.getElement(self.TICK_DATA).getElement(self.TICK_DATA)
        for item in data.values():
            time = item.getElementAsDatetime(self.TIME)
            timeString = item.getElementAsString(self.TIME)
            type = item.getElementAsString(self.TYPE)
            value = item.getElementAsFloat(self.VALUE)
            size = item.getElementAsInteger(self.TICK_SIZE)
            if item.hasElement(self.COND_CODE):
                cc = item.getElementAsString(self.COND_CODE)
            else:
                cc = ""
    
            line = format("%s\t%s\t%.3f\t\t%d\t%s\n" % (timeString, type, value, size, cc))
            self.output_file.write(line)


bbdl = BbDownloader()
bbdl.write_tick_data(output_filename="spx.txt", 
                    security="SPX INDEX", 
                    start_date="2013-06-24T00:00:00", 
                    end_date="2013-06-24T23:00:00")

