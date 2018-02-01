import hashlib
import base64

hash = "05153F611B337A378F73F0D32D2C16D362D06BA5"
# print type(hash)
# print hash

sa1 = hash[:2]
sa2 = hash[-2:]

rs = hash.decode('hex')
rs2 = 'bc' + rs + 'torrent'
hs = hashlib.sha1()
hs.update(rs2)
sha1 = hs.hexdigest()

b32 = base64.b32encode(rs)

#print "salty:" + sa1 + sa2
print "http://bt.box.n0808.com/" + sa1 +"/" + sa2 + "/" + hash + ".torrent"
#print "sha1:" + sha1
#已失效
print "http://torrent-cache.bitcomet.org:36869/get_torrent?info_hash=" + hash + "&size=226920869&key=" + sha1
#print "b32:" + b32
print "http://magnet.vuze.com/magnetLookup?hash=" + b32