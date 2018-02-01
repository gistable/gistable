#!/usr/bin/python

import sys, subprocess, getopt, os, json

def main(argv):
    script_name = os.path.basename(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "sw:h:q:", ["help", "solid-color", "width=", "height=", "samples="])
    except getopt.GetoptError as err:
        error(err)
        usage(script_name, False)
        return 2
        
    width = 1280
    height = 480
    samples = 2
    solid_color = False

    for opt, arg in opts:
        if opt == "--help":
            usage(script_name, True)
            return 0
        elif opt in ("-s", "--solid-color"):
            solid_color = True
        elif opt in ("-w", "--width"):
            width = int(arg)
            if width < 1:
                errror("Invalid width")
                return 2
        elif opt in ("-h", "--height"):
            height = int(arg)
            if height < 1:
                errror("Invalid height")
                return 2
        elif opt in ("-q", "--samples"):
            samples = float(arg)
            if samples < 0:
                errror("Invalid sample count")
                return 2
        else:
            error("Unrecognized option: " + opt)
            return 2
            
    if len(args) < 1:
        usage(script_name, False)
        return 1
        
    input_file = args[0]
    output_file = ""
    
    if len(args) > 1:
        output_file = args[1]
    else:
        output_file = os.path.splitext(input_file)[0] + ".png"
    
    # probe input file with FFprobe
    ffprobe_args = []
    ffprobe_args.append('ffprobe')
    
    # suppress version/build info
    ffprobe_args.append('-v')
    ffprobe_args.append('quiet')
    
    # output in JSON
    ffprobe_args.append('-print_format')
    ffprobe_args.append('json')
    
    # show format and stream info
    ffprobe_args.append('-show_format')
    ffprobe_args.append('-show_streams')
    
    # only select the first video stream
    ffprobe_args.append('-select_streams')
    ffprobe_args.append('v:0')
    
    # set input file
    ffprobe_args.append(input_file)
    
    # get FFprobe output
    ffprobe_output = b''
    
    try:
        ffprobe_output = subprocess.check_output(ffprobe_args)
    except subprocess.CalledProcessError as err:
        error("Can't probe input file!", err)
        return 2
        
    ffprobe_json = json.loads(str(ffprobe_output, "utf-8"))

    # find number of frames of the first video stream
    num_frames = 0
    
    if len(ffprobe_json['streams']) == 0:
        error("No video streams found in input file!")
        return 2
    
    format = ffprobe_json['format']
    stream = ffprobe_json['streams'][0]
    
    if 'nb_frames' in stream and int(stream['nb_frames']) > 0:
        num_frames = int(stream['nb_frames'])
    elif 'duration' in format and 'r_frame_rate' in stream:
        warning("Guessing number of frames from duration!")
        
        if stream['r_frame_rate'].find('/') != -1:
            fps_parts = stream['r_frame_rate'].split('/')
            num_frames = int(float(format['duration']) * (float(fps_parts[0]) / float(fps_parts[1])))
        else:
            num_frames = int(float(format['duration']) * float(stream['r_frame_rate']))
    else:
        error("Can't determine number of frames!")
        return 2
    
    # calculate frame step
    step = int(round(num_frames / width / samples))
    #print(step, num_frames, width)

    ffmpeg_args = []
    ffmpeg_args.append('ffmpeg')
    
    # set input file
    ffmpeg_args.append('-i')
    ffmpeg_args.append(input_file)
    
    # disable audio tracks
    ffmpeg_args.append('-an')
    
    # set filter
    ffmpeg_filter = ""
    
    # step = 1 is dangerous, but may be required for very short videos. In those cases,
    # there's no need for the select filter
    if step > 1:
        ffmpeg_filter = "select=not(mod(n\,{})),setpts=N/(FRAME_RATE*TB),".format(step)
    
    # squeeze frames down to 1xheight or 1x1 for solid coloring
    ffmpeg_filter += "scale=1:{}".format(1 if solid_color else height)
    
    ffmpeg_args.append('-filter:v')
    ffmpeg_args.append(ffmpeg_filter)
    
    # send images to pipe
    ffmpeg_args.append('-f')
    ffmpeg_args.append('image2pipe')
    
    # use ppm as image format
    ffmpeg_args.append('-c:v')
    ffmpeg_args.append('ppm')
    
    # use pipe as output file
    ffmpeg_args.append('-')
    
    convert_resize = "{}x{}!".format(width, height)
    
    convert_args = []
    convert_args.append('convert')
    
    # append all images from the pipe to one image
    convert_args.append('(')
    convert_args.append('+append')
    convert_args.append('-')
    convert_args.append(')')
    
    # resize final image
    convert_args.append('-resize')
    convert_args.append(convert_resize)
    
    # write to output file
    convert_args.append(output_file)
    
    print("Sampling video...")
    
    try:
        # start processes and wait for them to finish
        ffmpeg = subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE)
        convert = subprocess.Popen(convert_args, stdin=ffmpeg.stdout)
        
        ffmpeg.wait()
        
        print("Generating movie barcode...")
        convert.wait()
        
        print("Finished!")
        return 0
    except subprocess.CalledProcessError as err:
        error("Can't start ffmpeg/convert!", err)
        return 2
    
def usage(name, full):
    print('Usage:', name, '[OPTION]... VIDEO [IMAGE]')
    
    if full:
        print('  -w, --width              barcode width in pixels (default: 1280)')
        print('  -h, --height             barcode height in pixels (default: 480)')
        print('  -s, --solid-color        use average color of the entire frame per column')
        print('  -q, --samples            number of frame samples per column (default: 2)')
        print('      --help               display this help and exit')
    
def error(*args):
    print("Error:", *args, file=sys.stderr)
    
def warning(*args):
    print("Warning:", *args, file=sys.stderr)
    
if __name__ == "__main__":
   sys.exit(main(sys.argv))