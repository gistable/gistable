import time
import random
import sys
import os.path


def main():
    if len(sys.argv) < 2:
        print("File required.")
    else:
        if not os.path.exists(sys.argv[1]):
            print("The file " + sys.argv[1] + " could not be found.")
        else:
            print("Analyzing...")
            time.sleep(random.randint(1, 3))
            print("NO")


if __name__ == '__main__':
    main()