#!/usr/bin/env python


import sys, serial, time  #@UnresolvedImport

class XBeeConfig:

    def __init__( self, port = '', baud = 19200 ):
        self.err, self.__ser__ = '', None
        self.openSerial( port, baud )

    def openSerial( self, port, baud ):
        """ Try to open a serial port. """
        if self.__ser__:
            self.__ser__.close()
        self.err, self.__ser__ = '', None
        try:
            self.__ser__ = serial.Serial()
            self.__ser__.port = port
            self.__ser__.baudrate = baud
            self.__ser__.open()
        except Exception, msg: self.err = str( msg )
        return self.isOpen()

    def isOpen( self ):
        """ Is the serial port open? If not, see the err property. """
        return self.__ser__ and self.__ser__.isOpen()

    def configure( self, **kwargs ):

        print "Checking is port is open..."
        if not self.isOpen():
            print "Port not open: %s\n" % ( self.err, )
            return

        if self.commandMode():
            print "Entering command mode..."

            if kwargs.has_key( "speed" ):
                print "Setting baud rate..."
                if not self._setSpeed( kwargs["speed"] ):
                    print "Couldn't set baud rate."
            '''
            if kwargs.has_key( "channel" ):
                print "setting channel id"
                if not self._setChannelID( kwargs["channel"] ):
                    print "couldn't set channel id"'''

            if kwargs.has_key( "pan_id" ):
                print "Setting PAN ID..."
                if not self._setPanID( kwargs["pan_id"] ):
                    print "Couldn't set PAN ID."

            if kwargs.has_key( "destination" ):
                print "Setting destination..."
                if not self._setDest( kwargs["destination"] ):
                    print "Couldn't set destination."

            if kwargs.has_key( "node_id" ):
                print "Setting node ID..."
                if not self._setNodeID( kwargs["node_id"] ):
                    print "Couldn't set node ID."

            print "Saving changes..."
            if not self.writeAndExit():
                print "Write or exit failed."

            self.printConfig()
            print "Done configuration."
        else:
            print "Couldn't enter command mode."

    def printConfig( self ):
        if self.commandMode():
            self.serialSend( "ATID\r" )
            pan_id = self.getReply()
            self.serialSend( "ATMY\r" )
            node_id = self.getReply()
            self.serialSend( "ATBD\r" )
            baud = self.getReply()
            self.serialSend( "ATCH\r" )
            channel = self.getReply()
            self.serialSend( "ATDH\r" )
            atdh = self.getReply()
            self.serialSend( "ATDL\r" )
            atdl = self.getReply()
            print "------------------------"
            print "PAN ID:  %s" % ( pan_id, )
            print "Node ID: %s" % ( node_id, )
            print "Speed:   %s" % ( baud, )
            print "Channel: %s" % ( channel, )
            print "atdh: %s" % ( atdh, )
            print "atdl: %s" % ( atdl, )
            self.serialSend( "ATCN\r" )
            self.getOK()
            print "closing serial port."
            self.__ser__.close()
            print "------------------------"
        else:
            print "Couldn't enter command mode."

    def serialSend( self, msg ):
        """ Send a message to the serial port, if we can. """
        if self.isOpen():
            self.__ser__.write( msg )

    def commandMode( self ):
        """ Enter command mode to program the XBee. """
        self.wait( 1.1 )
        self.serialSend( "+++" )
        self.__ser__.flushInput()
        self.wait( 1.1 )
        return self.getOK()

    def _setPanID( self, id ):
        """ Set the network to which this node belongs. """
        self.serialSend( "ATID %s\r" % ( toHex( id ), ) )
        return self.getOK()
    '''
    def _setChannelID( self, id ):
        """Set the network channel """
        self.serialSend( "ATCH %s\r" % ( toHex( id ), ) )
        return self.getOK()
        '''

    def _setNodeID( self, id ):
        """ Set the ID of this node. """
        self.serialSend( "ATMY %s\r" % ( toHex( id ), ) )
        return self.getOK()

    def _setDest( self, dst ):
        """ Set the destination node. """
        self.serialSend( "ATDH 0\r" )
        if self.getOK():
            self.serialSend( "ATDL %s\r" % ( toHex( dst ), ) )
            return self.getOK()
        return 0

    def _setSpeed( self, speed ):
        """ Set the speed of the serial connection.
        0 = 1200 bps
        1 = 2400
        2 = 4800
        3 = 9600
        4 = 19200
        5 = 38400
        6 = 57600
        7 = 115200
        """
        self.serialSend( "ATBD %s\r" % ( speed, ) )
        return self.getOK()

    def writeAndExit( self ):
        """ Write changes and exit command mode. """
        self.serialSend( "ATWR\r" )
        ok = self.getOK()
        if not ok:
            print "Error saving settings."
        self.serialSend( "ATCN\r" )
        ok = self.getOK() and ok
        return ok

    def wait( self, secs ):
        """ Sleep for some number of seconds. """
        timeNow = time.time()
        timeEnd = timeNow + secs
        while timeNow < timeEnd:
            time.sleep( timeEnd - timeNow )
            timeNow = time.time()

    def getReply( self ):
        """ Get a CR terminated reply from the XBee. """
        done = 0
        reply = ''
        while ( self.__ser__.isOpen() and not done ):
            if self.__ser__.inWaiting() > 0:
                ch = self.__ser__.read()
                if ch == "\r":
                    done = 1
                else:
                    reply = reply + ch
        return reply

    def getOK( self ):
        """ Get the XBee reply and check that it was OK. """
        reply = self.getReply()
        return reply == 'OK'

    def close( self ):
        if self.isOpen():
            self.__ser__.close()

def toHex( num ):
    """ Turn a number into a hex string. """
    hx = hex( num ).lstrip( '0x' )
    if hx == '':
        hx = '0'
    return hx



if __name__ == '__main__':
    cfg = XBeeConfig( '/dev/tty.usbserial-A3000WRS', 19200 )

    # can also set destination "destination"
    settings = {"speed":4, "pan_id": 4000, "node_id": 2}
#    cfg.configure( **settings )
    cfg.printConfig()

    sys.exit()

#    if not len( sys.argv ) == 3:
#        print "NEED: pan_id and node_id"
#    else:
#        cfg.configure( int( sys.argv[1] ), int( sys.argv[2] ) )

