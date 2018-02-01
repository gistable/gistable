# Usage of this file:
# This code is intended for use in the iOS python interpreter named 'Pythonista'.
# When looking at a page on the torrentz.eu search engine for a torrent result from Mobile Safari
# you can click on a bookmarklet (mentioned below) and it will cause the following:
# - Search results for the page are scraped
# - Torrent sites are visited for direct download links for the .torrent file
# - A .torrent file is downloaded
# - The .torrent file trackers are updated to include the scraped trackers listed on torrentz.eu
# - The .torrent file is re-uploaded to your Dropbox account (for an on-demand HTTP source)
# - The direct download link for the modified .torrent file is passed via RPC to a Transmission torrent server
# - The torrent is added for download (suspended / not started)

# The bookmarklet:
# Create a bookmark in Safari - for anything, named something meaningful like 'DL Torrentz'
# Edit the bookmark, and change the URL to:
# javascript:(function()%7Bif(document.location.href.indexOf('http')===0)document.location.href='pythonista://transtor/transtor?action=run&argv='+document.location.href;%7D)();

# This file is stored under a folder you'll create called 'transtor' in Pythonista
# When the folder is properly populated, it will contain the following:
# - transtor.py
# - bencode.py - This file, and BTL.py, are from: https://pypi.python.org/pypi/BitTorrent-bencode
# - BTL.py
# - 'dropboxnew' folder (see note below)

import requests, re, sys, bencode, tempfile, json, console

# The dropbox module that's included with Pythonista is out of date.
# You can bring in the pure python updated official module under a folder called 'pythonnew'
# If you need an easy way to upload files into / out of Pythonista, here's a one-file
# WebDAV server: https://github.com/pudquick/TinyWebDav/blob/FirstVersion/webdav.py

import dropboxnew as dropbox

# View documentation here on getting a dropbox access token: https://www.dropbox.com/developers/core/start/python
dropbox_access_token = u'YOUR_APP_ACCESS_TOKEN_HERE'
dropbox_client = dropbox.client.DropboxClient(dropbox_access_token)
rpc_url = "http://your.transmission.web.server:9091/transmission/rpc/"

def transfer_torrent(a_url):
    t_hash = a_url.split('/')[-1]
    t_html = requests.get(a_url).content
    # Announce list for trackers
    announce_id = re.findall(r'href=.([^>]+)["\']', t_html.split('This lists all the active trackers',1)[1].split('compatible list here',1)[0])[0].split('announcelist_',1)[-1]
    announce_url = 'http://torrentz.eu/announcelist_%s' % announce_id
    alt_trackers = requests.get(announce_url).content
    alt_trackers = [x.strip() for x in alt_trackers.split('\n') if x.strip()]
    # Slice out the downloads
    downloads = t_html.split('<div class="download">', 1)[-1].split('<div class="trackers">', 1)[0]
    downloads = [x for x in downloads.split('<dl><dt>')[1:] if '<dd>Sponsored Link</dd>' not in x]
    downloads = [re.findall('^.+(http://[^"\']+)', x)[0] for x in downloads]
    # Filter out sites that don't give obvious direct links to .torrent files
    site_blacklist = set(['www.torrenthound.com', 'www.houndmirror.com', 'www.torrentreactor.net', 'www.limetorrents.com', 'www.monova.org', 'www.torrentcrazy.com'])
    downloads = [x for x in downloads if re.findall('//([^/]+)',x)[0] not in site_blacklist]
    # Limit it to just 10 sites to visit
    downloads = downloads[:10]
    # Need some formulas
    # Try a generic link extraction, should be enough - we just need *a* torrent
    torrent_files = set()
    for a_site in downloads:
        print "> Getting:", a_site
        a_site_html = requests.get(a_site).content
        torrent_files.update(set([x for x in re.findall(r'<a [^>]*href=["\'](http:[^"\'>]+\.torrent[^"\'>]*)["\']', a_site_html) if t_hash in x.lower()]))   
    torrent_files = sorted(torrent_files)    
    # Filter out malware downloads
    malware_blacklist = set(['clickdownloader.com'])
    torrent_files = [x for x in torrent_files if re.findall('//[^/]*?([^/.]+[.][^/.]+)/', x)[0] not in malware_blacklist]
    # Keep only URLs for domains 'known good' to direct download so far
    site_whitelist = set(['torcache.net'])
    whitelist_torrent_files = [x for x in torrent_files if re.findall('//([^/]+)',x)[0] in site_whitelist]
    # Check if we have at least one good URL
    if not whitelist_torrent_files:
        print "Error: No whitelisted download locations found"
        print "Downloads:", torrent_files.__repr__()
        print "Sites:", downloads.__repr__()
        return
    # We're only here if we have at least one confirmed direct downloadable .torrent URL
    target_tor = whitelist_torrent_files[0]
    print '\n*** Downloading .torrent:', target_tor
    # Get the contents of the .torrent file
    print '*** Modifying .torrent ...'
    bcode = requests.get(target_tor).content
    bdict = bencode.bdecode(bcode)
    # Get the announce-list - should be a list of lists
    b_announce = bdict.get('announce-list', [])
    # Need to flatten the list and inject our own alt_trackers, using that trick
    b_announce = [y for x in b_announce for y in x]
    # Combine in our alt_trackers and reset to unique and sorted
    b_announce = sorted(set(b_announce + alt_trackers))
    # Split and re-set with udp:// URLs first - and filter out non-sense urls, potentially
    http_t, udp_t = [x for x in b_announce if x.lower().startswith('http://')],[x for x in b_announce if x.lower().startswith('udp://')]
    b_announce = udp_t + http_t
    # Refashion into list wrapped items
    b_announce = [[x] for x in b_announce]
    # Set the announce-list to the new value
    bdict['announce-list'] = b_announce
    # Form a newly encoded torrent file
    new_torrent = bencode.bencode(bdict)
    # Save the output to a tempfile
    temp_tor = tempfile.TemporaryFile()
    temp_tor.write(new_torrent)
    temp_tor.seek(0)
    # Upload the file to Dropbox
    print '*** Uploading .torrent:', t_hash + '.torrent'
    response = dropbox_client.put_file('/%s.torrent' % t_hash, temp_tor)
    # Release the tempfile
    temp_tor.close()
    # Get the sharing URL
    print '*** Getting share link ...'
    share_info = dropbox_client.share('/%s.torrent' % t_hash, short_url=False)
    share_url = share_info['url']
    # Fake download it at least once so Dropbox is famliar with our IP address (probably unnecessary)
    _ = requests.get(share_url).content[0:0]
    # Update the URL to include the direct download action
    share_url += '?dl=1'
    # Now to send this URL onto the web interface ...
    rpc_id = requests.get(rpc_url).headers['x-transmission-session-id']
    headers = {'Content-Type':'application/json','Accept':'*/*','X-Requested-With':'XMLHttpRequest', 'X-Transmission-Session-Id': rpc_id}
    payload = {'method': 'torrent-add', 'arguments': {'filename': share_url}}
    print '*** Transferring to Transmission ...'
    r_upload = requests.post(rpc_url, data=json.dumps(payload), headers=headers)
    r_response = json.loads(r_upload.content)
    print r_response.__repr__()
    print "DONE !"

def main():
    a_url = None
    if (len(sys.argv) > 0):
        try:
            a_url = sys.argv[1]
        except Exception:
            a_url = None
    if not a_url:
        print repr(sys.argv)
        return
    console.clear()
    transfer_torrent(a_url)
    # transfer_torrent("http://torrentz.eu/torrent_hash_here")

if __name__ == '__main__':
    main()
