from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order

from random import randint
import time

def error_handler(msg):
    print ("Server Error: %s" % msg)

def reply_handler(msg):
    print ("Server Response: %s, %s" % (msg.typeName, msg))

# Globals suck; you should replace with a custom class in your production code.
time_received_next_valid_order_id = None # will be set as soon as we connect
next_valid_order_id = None # will be set as soon as we connect
def next_valid_order_id_handler(msg):
    global time_received_next_valid_order_id, next_valid_order_id
    next_valid_order_id = msg.orderId
    time_received_next_valid_order_id = time.time()

def make_contract(symbol, sec_type, exch, prim_exch, curr):
    Contract.m_symbol = symbol
    Contract.m_secType = sec_type
    Contract.m_exchange = exch
    Contract.m_primaryExch = prim_exch
    Contract.m_currency = curr
    return Contract

def get_next_valid_order_id(conn):
    """
    You must assign a unique order ID to each order you place. IB's servers
    keep track of the next available order ID you can use; this function
    requests that value from IB's servers, waits until IB sends a response,
    then returns the ID.
    """
    global time_received_next_valid_order_id, next_valid_order_id
    last_time = time_received_next_valid_order_id
    next_valid_order_id = conn.reqIds(1) # Always keep arg set to 1 (cruft)
    #Wait until IB sends the next valid ID
    while last_time == time_received_next_valid_order_id:
        time.sleep(0.01)
    return next_valid_order_id

def make_order(action, quantity, price = None):
    if price is not None:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        order.m_lmtPrice = price
    else:
        order = Order()
        order.m_orderType = 'MKT'
        order.m_totalQuantity = quantity
        order.m_action = action
    return order

if __name__ == "__main__":
    conn = Connection.create(port=7497, clientId=999)
    
    #Register handlers before connecting
    conn.register(error_handler, 'Error')
    conn.registerAll(reply_handler)
    conn.register(next_valid_order_id_handler, 'NextValidId')
    
    conn.connect()
    
    oid = get_next_valid_order_id(conn)
    cont = make_contract('TWTR', 'STK', 'SMART', 'SMART', 'USD')
    offer = make_order('BUY', 1, None)
    conn.placeOrder(oid, cont, offer)
    
    conn.disconnect()