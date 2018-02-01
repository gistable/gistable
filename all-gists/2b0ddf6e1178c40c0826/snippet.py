import requests
import random
import xml.dom.minidom

'''
Simple script to simulate what needs to go in a Freewheel ad request
This example is for VMAP but what needs to be requested is similar on other response types e.g. FW Smart XML
To use Smart XML response just change the resp parameter to "xml"
'''

#nw
NETWORK = "375613"
#prof
# HbbTV Profile is MSN_AU_HBBTV_Live but currently doesn't have vast2 activated
PROFILE = "MSN_AU_ios_Live"
# base URL
SERVER = "http://5bb3d.v.fwmrm.net/ad/g/1?"

# caid
# shortform
#asset = "3657904242001"
# longform
asset = "3654502947001"
asset = "3649633236001"

# vdur
duration = "5000"
#csid
section = "jumpin_hbbtv_general"

resp = "vmap1" #;module=DemoPlayer"

slots = [0,589,1328,1500]

width = "1280"
height = "720"

# Generate random variables for the player
#pvm
pvrn = random.randint(0,100000000)
#vprn
vprn = random.randint(0,100000000)

# http://hub.freewheel.tv/display/techdocs/Capabilities+in+Ad+Request
flags = "+emcr+slcb+fbad"

'''
FW Example
http://demo.v.fwmrm.net/ad/g/1?flag=+emcr+slcb&nw=96749&prof=global-as3&csid=DemoSiteGroup.01&
caid=DemoVideoGroup.01&vdur=3000&resp=vast2&crtp=vast2s;module=DemoPlayer&feature=simpleAds;
slid=pre&tpos=0&ptgt=a&slau=preroll;slid=overlay&tpos=10&ptgt=a&slau=overlay;slid=display&ptgt=s&slau=display&w=728&h=90&flag=+cmpn;

'''

# Specify the UA which is also used by Freewheel for targeting
headers = {
           'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.103 Safari/537.36'
           }


def gen_slots_string(slots):
    slot_string = "feature=simpleAds;"
    count = 1
    for slot in slots:
        if slot == 0:
            # pre roll, not could also just force this on all ads
            slot_string += ";slid=pre&tpos=0&ptgt=a&slau=preroll&tpcl=PREROLL"
        else:
            pass
            slot_string += ";slid=mid" + str(count) + "&tpos=" + str(slot) + "&ptgt=a&tpcl=MIDROLL&cpsq=" + str(count)
            count += 1
    # Add the post roll
    slot_string += ";slid=post&tpos=" + str(count + 1) + "&ptgt=a&slau=postroll&tpcl=POSTROLL"
            
    return slot_string


# Build the ad tag url
slot_string = gen_slots_string(slots)
url = ("%snw=%s&prof=%s&csid=%s&caid=%s&vprn=%s&pvn=%s&resp=%s&flag=%s&%s&w=%s&h=%s" \
%  (SERVER, NETWORK, PROFILE, section, asset, vprn, pvm, resp, slot_string, flags, width, height))

print url
fwresp = requests.get(url, headers=headers)

xml = xml.dom.minidom.parseString(fwresp.text)
print xml.toprettyxml()
    