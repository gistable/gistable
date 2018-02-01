import shodan.threatnet

# Configuration
API_KEY = "Please enter your API key here"

# Create the object that interfaces with the Threatnet API
tnet = shodan.threatnet.Threatnet(API_KEY)

# Get a stream of events and print them to stdout
for event in tnet.stream.events():
    print event
    
# For full information on what information events contain please visit:
# https://developer.shodan.io/api/event-specification