#
#Example of how to use EasyMDB RS232
#Date June/2014
#Version 1.0.2
#Not warranty, for educational purposes
#Thinkchip

#V1.0.1
#dispense coin function
#Level coin changer added
#V1.0.2
#add Display MDB function

import serial
import time
import sys

#Global Variables
ser = 0
scaling = 0
scaling_bill = 0

#Functions for EasyMDB RS232
InitCoin = [0x02,0x01,0xff,0x02]
PollCoin = [0x02,0x03,0xff,0x04]
TubesCoin = [0x02,0x05,0xff,0x06]
ErrorCoin = [0x02,0x0a,0xff,0x0b]
InitBill = [0x03,0x01,0xff,0x03]
PollBill = [0x03,0x02,0xff,0x04]
StackerBill = [0x03,0x03,0xff,0x05]





#Function to init serial port
def init_serial():
    COM=10 #number of com port
    global ser
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = COM-1
    ser.timeout = 10 #10 seconds waiting for data
    ser.open()


    if ser.isOpen():
        print 'Open serial port: ' + ser.portstr



#function commands print
def main_console():
    print "Menu Commands EasyMDB RS232\r\n"
    print "For Init Coin Changer press \"1\" Key"
    print "For Poll Coin Changer press \"2\" Key"
    print "For Tubes Coin Changer press \"3\" Key"
    print "For Error Coin Changer press \"4\" Key"
    print "For Coin types accepted press \"5\" Key"
    print "For Pay Out press \"6\" Key"
    print "For Coin dispense press \"11\" Key"
    print "For Init Bill validator press \"7\" key"
    print "For Poll Bill validator press \"8\" key"
    print "For Stacker Bill validator press \"9\" key"
    print "For Bill accepted press \"10\" key"
    print "For display value press \"12\" key"
    print "Exit \"0\" Key"


#function init coin changer
def init_coin_changer():
    print "Start the communication with Coin Changer\r\n"
    print "Send command 0x02 0x01 0xff 0x02\r\n"
    ser.write(InitCoin)
    data = ser.read(52)#expect 52 bytes of information has model, version, scaling
                   #factor , etc
    
    level = ord(data[2])
    str(level)
    print "Level Coin Changer: ", level
    print "Manufacturer code"
    print data[3:5]
    print "Model Coin Changer"
    print data[6:17]
    print "Serial Number Coin Changer"
    print data[18:29] 
    scaling = ord(data[30])#scaling factor
    str(scaling)
    print "Scaling Factor : ", scaling
    decimal = ord(data[31])
    str(decimal)
    print "Decimal Places : ",decimal
    msb = ord(data[32])
    country = msb << 8
    lsb = ord(data[33])
    country = country | lsb
    str(country)
    print "Country Coin changer model :", country
    print "Coin type accepted:"
    coinaccepted = ord(data[34])
    str(coinaccepted)
    print "Coin type 1:",coinaccepted
    coinaccepted = ord(data[35])
    str(coinaccepted)
    print "Coin type 2:",coinaccepted
    coinaccepted = ord(data[36])
    str(coinaccepted)
    print "Coin type 3:",coinaccepted
    coinaccepted = ord(data[37])
    str(coinaccepted)
    print "Coin type 4:",coinaccepted
    coinaccepted = ord(data[38])
    str(coinaccepted)
    print "Coin type 5:",coinaccepted
    coinaccepted = ord(data[39])
    str(coinaccepted)
    print "Coin type 6:",coinaccepted
    
    
    
#function tubes coin changer
def tubes_coin():
    print "Send command tubes coin\r\n"
    print "0x02 0x05 0xff 0x06\r\n"
    ser.write (TubesCoin)
    data1 = ser.read(6)
    msb1 = ord(data1[2])
    lsb1 = ord(data1[3])
    totaltubes = msb1 << 8
    totaltubes = totaltubes | lsb1
    totaltubesreal = float(totaltubes/2.0)#this value for mexico supported
    print "Total Coin Tubes:" + '%.2f' %totaltubesreal
    
    
#function poll coin
def poll_coin():
    i=0
    global scaling
    while (i<30):
        print "Poll coin every 1 second"
        print "Send 0x02,0x03,0xff,0x04"
        ser.write(PollCoin)
        data2 = ser.read(10)
        msb2 = ord(data2[2])
        lsb2 = ord(data2[3])
        cash = msb2 << 8
        cash = cash | lsb2
        #for take the real value of coin inserted, need to divide between
        #scaling factor, but not always is that and observe the best operation
        if cash>1 :
            cashreal= float(cash/scaling)
            print "Coin inserted:" + '%.2f' %cashreal
        else:
            print "Coin inserted : 0"
        #coin routing
        routing = ord(data2[4])
        if routing == 0:
            print "Cash Box routing coin"

        elif routing == 1:
            print "Tubes routing coin"

        elif routing == 2:
            print "Not used"

        elif routing == 3:
            print "Reject coin"
        else :
            print "nothing coin routing"

        msb2 = ord(data2[5])
        lsb2 = ord(data2[6])
        coindispensed = msb2 << 8
        coindispensed = coindispensed | lsb2

        realcoindispensed = float(coindispensed/2.0)

        print "Coin dispensed: " + '%.2f' %realcoindispensed

        coinerror = ord(data2[7])
        str(coinerror)
        print "Error coin number: ",coinerror
        print "\r\n"
        
        i = i + 1
        time.sleep(1)

#function for payout
def pay_out_coin():
    print "Select the amount that you want to dispense"
    amount_string = raw_input()
    amount_string = int(amount_string)
    msb4 = amount_string >> 8
    lsb4 = amount_string & 0x00ff
    checksum = 0x02+0x07+msb4+lsb4+0xff
    checksum = checksum & 0x00ff
    
    PayOutString = [0x02,0x07,msb4,lsb4,0xff,checksum]
    ser.write(PayOutString)
    data5 = ser.read(5)
    alert = ord(data5[2])
    if alert == 1:
        print "OK payout"
    else:
        print "Fail payout"

#function for error coin general
def error_coin():
    print "Error coin general"
    print "Send 0x02,0x0a,0xff,0x0b"
    ser.write(ErrorCoin)
    data6 = ser.read(6)
    msb6 = ord(data6[2])
    lsb6 = ord(data6[3])
    error = msb6 << 8
    error = error | lsb6
    str(error)
    print "Error coin changer: ",error

#function coin accepted
def coin_accepted():
    print "Coin type accepted"
    print "For enable all coins press \"1\" and disable \"0\" "
    key = raw_input()
    key = int(key)
    if key == 1:
        print "Enable all coins"
        print "Send 0x02,0x08,0xff,0xff,0xff,0xff,0xff,checksum"
        checksum2 = 0x02 + 0x08 + 0xff + 0xff + 0xff + 0xff + 0xff
        checksum2 = checksum2 & 0x00ff
        CoinAccepted = [0x02,0x08,0xff,0xff,0xff,0xff,0xff,checksum2]
        ser.write(CoinAccepted)
        data7 = ser.read(5)
        alert = ord(data7[2])
        if alert == 1:
            print "OK coin accepted"
        else:
            print "Fail coin accepted"
    elif key == 0:        
        print "Disable all coins"
        print "Send 0x02,0x08,0x00,0x00,0x00,0x00,0xff,checksum"
        checksum2 = 0x02 + 0x08 + 0x00 + 0x00 + 0x00 + 0x00 + 0xff
        checksum2 = checksum2 & 0x00ff
        CoinAccepted = [0x02,0x08,0x00,0x00,0x00,0x00,0xff,checksum2]
        ser.write(CoinAccepted)
        data7 = ser.read(5)
        alert = ord(data7[2])
        if alert == 1:
            print "OK coin accepted"
        else:
            print "Fail coin accepted"

#function Dispense coin
def coin_dispense():
    print "Coin dispense"
    print "Select Coin Type to dispense,range 0 to 15 value only"
    key = raw_input()
    key = int(key)
    cointype = key
    print "Select number coins to dispense,range 0 to 15 value only"
    key = raw_input()
    key = int(key)
    numbercoin = key
    checksum = 0x02 + 0x0b + cointype + numbercoin + 0xff
    checksum = checksum & 0x00ff
    DispenseCoin = [0x02,0x0b,numbercoin,cointype,0xff,checksum]
    ser.write(DispenseCoin)
    print "Sending coin dispense"
    data = ser.read(5)
    response = ord(data[2])
    if response == 1:
        print "OK coin dispense"
    else:
        print "Fail coin dispense"
        
    
    
            
#function bill validator
def bill_init():
    global scaling_bill
    
    print "Bill init command"
    print "Send 0x03,0x01,0xff,0x03"
    ser.write(InitBill)
    databill = ser.read(52)
    print "Manufacturer code"
    print databill[2:4]
    print "Model bill validator"
    print databill[5:16]
    print "Serial Number bill validator"
    print databill[17:28]
    
    escrow = ord(databill[29])
    str(escrow)
    print "Escrow bill validator: ",escrow
    decimalplacesbill = ord(databill[30])
    str(decimalplacesbill)
    print "Decimal places: ",decimalplacesbill
    msb = ord(databill[31])
    lsb = ord(databill[32])
    scaling_bill = msb << 8
    scaling_bill = scaling_bill | lsb
    str(scaling_bill)
    print "Scaling factor for Bill validator: ",scaling_bill
    msb = ord(databill[33])
    lsb = ord(databill[34])
    stackercap = msb << 8
    stackercap = stackercap | lsb
    str(stackercap)
    print "Stacker capacity: ",stackercap

    billtype = ord(databill[35])
    str(billtype)
    print "Bill type 1:",billtype
    
    billtype = ord(databill[36])
    str(billtype)
    print "Bill type 2:",billtype
    
    billtype = ord(databill[37])
    str(billtype)
    print "Bill type 3:",billtype
    
    billtype = ord(databill[38])
    str(billtype)
    print "Bill type 4:",billtype

#function Poll Bill
def poll_bill():
    i=0
    global scaling_bill
    while (i<30):#times that will poll
        print "Poll bill every 1 second"
        print "Send 0x03,0x02,0xff,0x04"
        ser.write(PollBill)
        databill = ser.read(7)
        msb = ord(databill[2])
        lsb = ord(databill[3])
        bills = msb << 8
        bills = bills | lsb
        #For take the real value of bill inserted, we need to divide between
        #scaling factor, but not always is the same mathematical operation
        if bills>1 :
            billsreal= float(bills*10.0)
            print "Bills inserted:" + '%.2f' %billsreal
        else:
            print "Bills inserted : 0"
        
        bills_error = ord(databill[4])
        str(bills_error)
        print "Error bills: ",bills_error
        print "\r\n"
        
        i = i + 1
        time.sleep(1)

#function stacker bill
def stacker_bill():
    print "Stacker bill function"
    print "Send 0x03,0x03,0xff,0x05"
    ser.write(StackerBill)
    databill = ser.read(6)
    msb = ord(databill[2])
    lsb = ord(databill[3])

    numberbills = msb << 8
    numberbills = numberbills | lsb
    str(numberbills)
    print "Numbers bills in stacker: ",numberbills

#function bills accepted
def bills_accepted():
    print "Bills accepted command"
    print "Press \"1\" for enable all bills or \"0\" for disable"
    key = raw_input()
    key = int(key)

    if key == 1:
        print "Enable bills command"
        print "Send 0x03,0x04,0xff,0xff,0xff,checksum"
        checksum = 0x03 + 0x04 + 0xff + 0xff + 0xff
        checksum = checksum & 0x00ff
        BillAccepted = [0x03,0x04,0xff,0xff,0xff,checksum]
        ser.write(BillAccepted)
        databill = ser.read(5)
        alert = ord(databill[2])
        if alert == 1:
            print "OK bill accepted"
        else:
            print "Fail bill accepted"
    elif key == 0:
        print "Disable bills command"
        print "Send 0x03,0x04,0x00,0x00,0xff,checksum"
        checksum = 0x03 + 0x04 + 0x00 + 0x00 + 0xff
        checksum = checksum & 0x00ff
        BillAccepted = [0x03,0x04,0x00,0x00,0xff,checksum]
        ser.write(BillAccepted)
        databill = ser.read(5)
        alert = ord(databill[2])
        if alert == 1:
            print "OK bill accepted"
        else:
            print "Fail bill accepted"
    
    
#function display value
def display_value():
    print "Display value cash"
    print "Enter value between 0 and 9999"
    key = raw_input()
    key = int(key)
    print "Send value"
    msb = key >> 8
    lsb = key & 0x00ff
    checksum = 0x04+0x01+msb+lsb+0xff
    checksum = checksum & 0x00ff
    
    display_val = [0x04,0x01,msb,lsb,0xff,checksum]
    ser.write(display_val)
    data = ser.read(4)
    print "Ok display"

init_serial()#call function that init serial port



while 1:

    if ser.isOpen():
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput()#flush output buffer, aborting current output              
    
    main_console()
    command = raw_input("Please select a command\r\n")
    command = int(command)
    
    if command == 1:
        init_coin_changer()
    elif command == 2:
        poll_coin()
    elif command == 3:
        tubes_coin()
    elif command == 0:
        ser.close()
        sys.exit()
    elif command == 6:
        pay_out_coin()
    elif command == 4:
        error_coin()
    elif command == 5:
        coin_accepted()
    elif command == 7:
        bill_init()
    elif command == 8:
        poll_bill()
    elif command == 9:
        stacker_bill()
    elif command == 10:
        bills_accepted()
    elif command == 11:
        coin_dispense()
    elif command == 12:
        display_value()
    
    
        




