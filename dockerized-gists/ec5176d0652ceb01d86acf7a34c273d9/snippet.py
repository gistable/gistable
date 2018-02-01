def download_video(url, output_dir, filename, ext='mp4'):
    """Function to download video's from YouTube to a specific location.
    
    Args:
        url: YouTube URL.
        output_dir: Output directory to save the video.
        filename: Filename of the video.
        ext: File type to save the video to. Default to mp4.
    """
    import os
    file_loc = output_dir + filename + "." + ext
    # Download from Youtube URL
    if (url):
        print("Downloading Youtube Video")
        os.system("youtube-dl -o " + file_loc + " -f " + ext + " " + url)
        print("Done..")
    else:
        print("Please input a URL") 