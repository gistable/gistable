import sys


def main():
    if len(sys.argv) < 2:
        print 'please enter file path'
    file_path = sys.argv[1]
    with open(file_path, 'r') as f:
        s = f.read()
        try:
            s.decode('utf-8')
        except:
            print '%s not utf-8' % sys.argv[1]
        # print 'finish~~'

if __name__ == '__main__':
    main()
    # print sys.argv
