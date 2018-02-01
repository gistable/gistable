import gdata.youtube
import gdata.youtube.service


# Dependencies:
# - Python==2.7
# - gdata==2.0.18
# - google-api-python-client==1.2


yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True


# Can be left blank and be set on input
playlist_uri = "http://gdata.youtube.com/feeds/api/playlists/F835FEAB20A328D9"

if playlist_uri == "":
    playlist_uri = str(input("Playlist URI: "))


playlist_songs = []
playlist_video_feed = yt_service.GetYouTubePlaylistVideoFeed(playlist_uri)
for playlist_video_entry in playlist_video_feed.entry:
    playlist_songs.append(playlist_video_entry.title.text)


f = open("playlist.txt", "w")
for entry in playlist_songs:
    f.write(entry + "\n");
f.close()
