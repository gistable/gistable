"""
Here I want to share a POC that make two things:
* Convert a multi page pdf to png files
* Make a diff file between page 1 and page 2 of the pdf

This is done using [wand librairy](http://wand-py.org).
"""
from wand.image import Image


def pdf2png_and_diff_p1_p2(source_file, target_file, diff_file):
    RESOLUTION = 300
    with Image(filename=source_file, resolution=(RESOLUTION, RESOLUTION)) as img:
        # Save one png file per page
        img.save(filename=target_file)
        # If there are at least 2 pages, compare page 1 with page 2 and save
        # diff file
        if len(img.sequence) > 1:
            img_ref = img.sequence[0]
            img_diff = img.sequence[1]
            img_ref.composite_channel(channel='all_channels',
                                      image=img_diff,
                                      operator='difference')
            with Image(width=img.width, height=img.height) as result:
                result.composite_channel(channel='all_channels',
                                         operator='add', image=img_ref)
                result.format = 'png'
                result.save(filename=diff_file)

    return True

if __name__ == "__main__":
    source_file = "/path_to/multi-pages.pdf"
    target_file = "/path_to/output.png"
    diff_file = "/path_to/diff_p1_p2.png"

    pdf2png_and_diff_p1_p2(source_file, target_file, diff_file)
