#!/usr/bin/env python
# requires pychromecast and probably python 2.7, sorry

import pychromecast
import argparse

def play_video(url, cast):
    if cast.media_controller.status.player_state == "PAUSED" or cast.media_controller.status.content_id == url:
        cast.media_controller.play()
    else:
        cast.play_media((url), "video/mp4")

def pause_video(cast):
    if cast.media_controller.status.supports_pause:
        cast.media_controller.pause()
    else:
        print "Cannot pause"

def stop_video(cast):
    cast.quit_app()

def main():
    casts = pychromecast.get_chromecasts_as_dict()
    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs="?", help="URL of media to play. Doesn't support local addresses yet.")
#    parser.add_argument("-p", "--pause", help="Pause playback", action='store_true')
    parser.add_argument("-s", "--stop", help="Stop playback", action='store_true')
    parser.add_argument("-d", "--device", help="Select device. List devices with -D")
    parser.add_argument("-D", "--devices", help="List devices", action='store_true')
    args = parser.parse_args()
    if args.devices:
        print ", ".join(casts.keys())
        return
    if args.device:
        cast = casts[args.device]
    else:
        cast = casts[casts.keys()[0]]
    if not args.stop:
        play_video(args.url, cast)
        return
#    elif args.pause:
#        pause_video(cast)
#        return
    elif args.stop:
        stop_video(cast)
        return

if __name__ == "__main__":
    main()