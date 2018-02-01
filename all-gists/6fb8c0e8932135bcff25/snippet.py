#!/usr/bin/env python
import npyscreen, curses

# Incorporates code
# from http://www.binarytides.com/python-socket-server-code-example/
# Socket server in python using select function
import socket, select

class MyTestApp(npyscreen.NPSAppManaged):
    # socket code
    def onStart(self):
	self.keypress_timeout_default = 1
        self.addForm("MAIN",       MainForm, name="Screen 1", color="IMPORTANT",)
        self.addForm("SECOND",     MainForm, name="Screen 2", color="WARNING",  )
	# socket code
    	self.CONNECTION_LIST = []    # list of socket clients
    	self.RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    	PORT = 5000

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this has no effect, why ?
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", PORT))
        self.server_socket.listen(10)
     
        # Add server socket to the list of readable connections
        self.CONNECTION_LIST.append(self.server_socket)

	self.sent=""
	self.received="Chat server started on port " + str(PORT)
	self.currentform = None


    def while_waiting(self):
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(self.CONNECTION_LIST,[],[],0.01)
 
        for sock in read_sockets:
             
            #New connection
            if sock == self.server_socket:
                # Handle the case in which there is a new connection recieved through self.server_socket
                sockfd, addr = self.server_socket.accept()
                self.CONNECTION_LIST.append(sockfd)
                self.received = "Client (%s, %s) connected" % addr
                 
                #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(self.RECV_BUFFER)
                    # echo back the client message
                    if data:
			response = 'OK ... ' + data
                        sock.send(response)
			self.sent = response
			self.received = data
                 
                 
                # client disconnected, so remove from socket list
                except:
                    #print "Client (%s, %s) is offline" % addr
                    sock.close()
                    self.CONNECTION_LIST.remove(sock)
                    continue
             

    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")
        
        self.server_socket.close()
    
    def change_form(self, name):
        self.switchForm(name)
        self.resetHistory()
    
class MainForm(npyscreen.ActionForm):
    def create(self):
	self.keypress_timeout_default = 1
        self.add(npyscreen.TitleText, name = "Text:", value= "Press ^T to change screens" )
        self.sentfield = self.add(npyscreen.TitleText, name = "Sent:", value="", editable=False )
        self.receivedfield = self.add(npyscreen.TitleText, name = "Received:", value="", editable=False )
        
        self.add_handlers({"^T": self.change_forms})

    def while_waiting(self):
	self.sentfield.value = self.parentApp.sent
	self.receivedfield.value = self.parentApp.received
	self.sentfield.display()
	self.receivedfield.display()

    def on_ok(self):
        # Exit the application if the OK button is pressed.
        self.parentApp.switchForm(None)

    def change_forms(self, *args, **keywords):
        if self.name == "Screen 1":
            change_to = "SECOND"
        else:
            change_to = "MAIN"

        # Tell the MyTestApp object to change forms.
        self.parentApp.change_form(change_to)

def main():
    TA = MyTestApp()
    TA.run()


if __name__ == '__main__':
    main()

      