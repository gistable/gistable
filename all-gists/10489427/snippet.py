"""
Code for a music video where sheet music is
scrolled transparently on my hands playing the
piano. See that effect here:

https://www.youtube.com/watch?v=V2XCJNZjm4w

"""

from moviepy.editor import *
from moviepy.video.tools.drawing import color_gradient


# === THE SOUND - FROM A MICROPHONE

audio = AudioFileClip("./pianowav2.wav")
audio_shifted = CompositeAudioClip([audio.set_start(.55)])



# === MY HANDS PLAYING THE PIANO

# layered semi-transparent mask

piano = ( VideoFileClip("./limehouse_me.mp4")
           .subclip(0.5, 36)
           .set_audio(audio_shifted)
           .set_mask(mask))

W,H = piano.size

mask = ImageClip(color_gradient(piano.size,
                 p1=[0,0], p2=[0, 2*H/3],
                col1=1.0, col2=0), ismask=True)

piano = piano.set_mask(mask)



# === THE SHEET-MUSIC, WITH A SCROLLING EFFECT

sheet = ( ImageClip("./final.png")
           .fx( vfx.scroll,h= 1.5*H, y_speed=43)
           .set_duration(piano_s.duration)
           .fx( vfx.freeze_at_start, .5)
           .resize(width=W))



# === PIANO AND SHEET MUSIC PUT TOGETHER

piano_sheet = ( CompositeVideoClip(
                   [sheet, piano], size=[W,H])
                .set_duration(piano_s.duration)
                .fx( vfx.freeze_at_start, .5)
                .audio_fadeout(5)
                .fadein(1).fadeout(5))



# === PANELS AT THE END

licence = (TextClip("This video is licenced under a\n"
                   "Creative Commons Attribution 3.0 "
                   "Unported License.\n"
                   "The sheet music is free, and freely available.\n"
                   "© A. de Lamarmotte, 2014",
                   color="white", bg_color="black",
                   font="Amiri-Bold", fontsize=22,
                   size= [W,H])
           .set_duration(4)
           .fadein(1).fadeout(1))

made_with_moviepy = ( ImageClip('logo_white.png')
                      .resize(width=0.6*W)
                      .on_color(size= [W,H],
                                pos=('center',H/5))
                      .set_duration(4)
                      .fadein(1).fadeout(1))



# === FINAL COMPOSITION

final = concatenate([piano_sheet, licence, made_with_moviepy])

final.to_videofile('final.mp4', fps=24, bitrate="6000k",
                    audio_bitrate='500k')