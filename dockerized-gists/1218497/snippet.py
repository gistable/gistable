import sys
import pika

# prerequisites are that you have RabbitMQ installed
# create a "darkmatter" named VirtualHost (VHOST)
#  rabbitmqctl.bat add_vhost darkmatter
# create a user APP_USER with associated APP_PASS word
#  rabbitmqctl add_user darkmatteradmin <password>
# give the APP_USER the necessary permissions
#  rabbitmqctl set_permissions -p darkmatter darkmatteradmin ".*"  ".*" ".*"
RABBITMQ_SERVER = "localhost"

EXCHANGE_DARKMATTER = "darkmatter-exchange"
VHOST_DARKMATTER = "darkmatter"
APP_USER = "your_rabbit_user_account"
APP_PASS = "your_rabbit_password"
STOP_PROCESSING_MESSAGE = "QRT"
FOLLOW_K0EMT_MESSAGE = "follow @k0emt on twitter! (that's a zero after the k)"

__author__ = 'k0emt'

class DarkMatterLogger:
	def connect_to_rabbit(self):
		credentials = pika.PlainCredentials(APP_USER, APP_PASS)
		conn_params = pika.ConnectionParameters(host=RABBITMQ_SERVER,
							virtual_host=VHOST_DARKMATTER,
							credentials=credentials)
		conn = pika.BlockingConnection(conn_params)
		self.channel = conn.channel()

	def initialize_exchange(self):
		self.channel.exchange_declare(exchange=EXCHANGE_DARKMATTER,
                                                  type="fanout",
                                                  passive=False,
                                                  durable=False,
                                                  auto_delete=False
                )
		
	def __init__(self):
		print "DM Logger init"
		self.connect_to_rabbit()
		self.initialize_exchange()
		
	def sendMessage(self, message):
		msg = message
		msg_props = pika.BasicProperties()
		msg_props.content_type = "text/plain"

		self.channel.basic_publish(body=msg,
                                           exchange=EXCHANGE_DARKMATTER,
                                           properties=msg_props,
                                           routing_key="")
		print "Message sent: ", message
	
	# if we receive a "quit" message, then stop processing
	def view(self):
		print "DML in viewer mode"
		
                ourChan = self.channel.queue_declare(exclusive=True)
                chan = self.channel
                
                chan.queue_bind(exchange=EXCHANGE_DARKMATTER,
                                        queue=ourChan.method.queue)

                # callback that runs when message arrives -- see basic_consume() below
                def msg_consumer(channel, method, header, body):
                                channel.basic_ack(delivery_tag=method.delivery_tag)
                                print body
                                if body == STOP_PROCESSING_MESSAGE:
                                                channel.basic_cancel(consumer_tag="DarkMatterViewer")
                                                channel.stop_consuming()
                        
                chan.basic_qos(prefetch_count=1)
                chan.basic_consume(msg_consumer)

                chan.start_consuming()

def main():
        # if the command line is given with the parameter send, then run this as a logger
        # no argument indicates to run the viewer
        #   c:\Python27\python.exe DarkMatterLogger.py send
        #   python DarkMatterLogger.py
        if len(sys.argv) > 1:
                if sys.argv[1] == "send":
                        dml = DarkMatterLogger()
                        dml.sendMessage("hola!")
                        dml.sendMessage("dos")
                        dml.sendMessage("tres")
                        dml.sendMessage(FOLLOW_K0EMT_MESSAGE)
                        dml.sendMessage(STOP_PROCESSING_MESSAGE)
        else:
                dmViewer = DarkMatterLogger()
                dmViewer.view()

main()
