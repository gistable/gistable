import os
import sys
import bencodepy
import humanize
import argparse


def total_size_files_torrent(file_name):
    try:
        parsed = bencodepy.decode_from_file(file_name)
    except bencodepy.exceptions.DecodingError as e:
        print("Error parsing {}: {}".format(file_name, e))
        return 0
    else:
        file_list = parsed.get(b'info').get(b'files')
        return sum(item[b'length'] for item in file_list)


def total_size_torrents_in_directory(directory, verbose=False):
    directory_file_total = 0
    for filename in os.listdir(directory):
        if filename.endswith(".torrent"):
            file_path = os.path.join(directory, filename)
            torrent_file_size = total_size_files_torrent(file_path)
            if verbose:
                print("{}: {}".format(file_path, humanize.naturalsize(
                    torrent_file_size)))
            directory_file_total += torrent_file_size
    return directory_file_total


def main():

    parser = argparse.ArgumentParser(
        description="%s displays file sizes of a set of torrent files." %
        sys.argv[0])

    parser.add_argument("location", type=str,
                        help="Torrent file or directory of torrent files")

    parser.add_argument("-v", action="store_true",
                        help="Display verbose output", )

    args = parser.parse_args()

    if os.path.isfile(args.location):
        combined_file_size = total_size_files_torrent(args.location)
        print("{}: {}".format(args.location, humanize.naturalsize(
            combined_file_size)))

    elif os.path.isdir(args.location):
        directory_size = total_size_torrents_in_directory(args.location,
                                                          verbose=args.v)
        print("Combined File Size for all torrents in directory "
              "'{}': {}".format(args.location,
                                humanize.naturalsize(directory_size)))

    else:
        print("Error: Could not find file or directory '{}'".format(
            args.location))


if __name__ == '__main__':
    main()
