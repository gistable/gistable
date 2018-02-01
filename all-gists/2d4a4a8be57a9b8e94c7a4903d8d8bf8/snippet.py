from requests import Session  # pip install requests
from signalr import Connection  # pip install signalr-client

def handle_received(**kwargs):
    print('received', kwargs)

def print_error(error):
    print('error: ', error)

    
def main():
    with Session() as session:
        connection = Connection("https://www.bittrex.com/signalR/", session)
        chat = connection.register_hub('corehub')
        connection.start()

        connection.received += handle_received
        connection.error += print_error

        for market in ["BTC-MEME", "BTC-ANS"]:
            chat.server.invoke('SubscribeToExchangeDeltas', market)
            chat.server.invoke('QueryExchangeState', market)

        while True:
            connection.wait(1)

if __name__ == "__main__":
    main()
