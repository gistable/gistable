
"""
Inspired by:
    http://eli.thegreenplace.net/2009/08/29/co-routines-as-an-alternative-to-state-machines/
"""

def parse_args(target):
    """A generator that parses a stream of arguments one character at a time.
       As soon as a flag, or flag value pair ("-a" or "-a value") is processed
       the pair is sent off as a tuple to the 'target' generator.

       The parser can handle escape characters, and double and single quoting
       of values:
           -flag value
           --a-flag value
           -one flag --two flag
           -quotes "Some \" text"
           -quotes 'Some \' text'
           -escaped-spaces here\ are\ some\ spaces

       Use by sending characters one at a time:
           p = parse_args()
           p.next()
           p.send('-')
           p.send('a')

           p.send(' ')
           p.send('-')
           # Sends ('-a', '') to target.
        Sending the last " -" tricks the parser into sending the last flag
        value pair, by making it think you're starting a new flag arg pair.
    """
    # Grab the first char of the input.
    char = (yield)
    while True:
        # Init the name and value pair. These will contain the name of the
        # flag (so "a" for -a) and the value, if there is one (so, "val" for
        # -a val).
        name = ""
        value = ""
        while True:
            # This loop iterates once per: name or value. Also iterates thru
            # spaces that aren't a part of a name or value.
            if char == " ":
                # Skip spaces.
                char = (yield)
            elif char == "-":
                if name != "":
                    break
                # Start processing new option flag.
                while char == "-":
                    # Skip hyphens at beginning.
                    char = (yield)
                while char != " ":
                    # Keep grabbing characters until we get to a space.
                    name += char
                    char = (yield)
            elif char.isalnum():
                # Start processing unquoted value.
                value += char
                char = (yield)
                while char.isalnum():
                    # Keep grabbing characters until we get to a non-alpha
                    # numeric character signalling the value is over.
                    value += char
                    char = (yield)
                    while char == "\\":
                        # If the escape character is countered, just add
                        # the the character following it to the value.
                        value += (yield)
                        char = (yield)
                # Grab next char for next iteration.
                char = (yield)
                # At this point, we should have a flag and value pair.
                # Breaking will get us to target.send
                break
            elif char in ["\'", "\""]:
                # Process quoted value.
                # Remember the quote character.
                quote = char
                char = (yield)
                while char != quote:
                    # Keep grabbing chars until we get to the matching quote.
                    value += char
                    char = (yield)
                    while char == "\\":
                        # Handle the escape character.
                        value += (yield)
                        char = (yield)
                # Forwad past the matching quote.
                char = (yield)
                # Grab next char for next iteration.
                char = (yield)
                break
        # Send the name, value pair to the receiver.
        target.send( (name, value) )

def target():
    """Simple target for the arg parser that just prints out each pair.
    """
    while True:
        print repr((yield))

# Functions for creating and initializing generators.
def make_target():
    t = target()
    t.next()
    return t
def make_parser(*args, **kwargs):
    p = parse_args(*args, **kwargs)
    p.next()
    return p

if __name__=="__main__":
    tests= [
            "-a",
            "--a-long-arg",
            "-name1 value",
            "-name2 'single quote'",
            '-name3 "double quote"',
            r"-name4 spaces\ using\ escape\ chars",
            "-name5 'escaping in quotes: \''",
            "-one arg --two-args val",
            ]
    parser = make_parser(make_target())
    for test in tests:
        print "Testing: %s" % repr(test)
        for c in test:
            parser.send(c)
        parser.send(" ")
        parser.send("-")