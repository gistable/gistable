# Instruction:
# - git clone https://google.github.io/material-design-icons/
# - Place and run this script inside the material-icons-main folder
#
# How to use (by example)
# python copy-android.py social notifications_none white 24dp ~/AndroidStudioProjects/my-project/app/src/main/res/
# or separate name with ',' multiple images from same group
# python copy-android.py social notifications_active,notifications,notifications_none,notifications_off,notifications_paused 24dp ~/AndroidStudioProjects/my-project/app/src/main/res/
#
# NOTE: You can search icons in https://www.google.com/design/icons/
#
# by Omar Miatello - Inspired by https://github.com/JonnoFTW/Material-Design-Copier
# tested on Python 2.7.6

import sys
import shutil
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Copy Image Assets from Material Design to your Android Project, preview all here: https://google.github.io/material-design-icons/, place and run this script inside the material-icons-main folder')
    parser.add_argument('group', type=str, help='Group (example: social, av, navigation, ...)')
    parser.add_argument('name', type=str, help='Name of the icon or icons separated by a comma (,) (example: 3d_rotation, attach_file, poll, ...)')
    parser.add_argument('color', type=str, help='Color of the icon', choices=['black', 'white'])
    parser.add_argument('dp', type=str, help='Dip of the icon', choices=['18dp', '24dp', '36dp', '48dp', '144dp'])
    parser.add_argument('dest', type=str, help='Desination res folder (example: ~/AndroidStudioProjects/my-project/app/src/main/res/)')
    args = parser.parse_args()
    res_dirs = ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'anydpi-v21']  # I use 'anydpi-v21' because of https://plus.google.com/u/0/+OmarMiatello/posts/AUBctxra9RG

    for name in args.name.lower().split(','):
        for res_dir in res_dirs:
            if res_dir == 'anydpi-v21':          # contains only black with 24dp
                fn = 'ic_{}_black_24dp.xml'.format(name)
            else:
                fn = 'ic_{}_{}_{}.png'.format(name, args.color, args.dp)
            drawable_dir = "drawable-{}".format(res_dir)
            src = '{}/{}/{}'.format(args.group, drawable_dir, fn)
            dest_dir = '{}/{}'.format(args.dest, drawable_dir)
            dest = '{}/{}'.format(dest_dir, fn)

            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                print 'Creating', dest_dir

            print 'Copying', src, 'to', dest
            shutil.copy(src, dest)
