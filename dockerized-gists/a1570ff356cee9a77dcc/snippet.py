from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    # ADD YOUR OPTION HERE:


    (options, args) = parser.parse_args()
    print 'options are', options
    print 'args are', args



if __name__ == '__main__':
    main()