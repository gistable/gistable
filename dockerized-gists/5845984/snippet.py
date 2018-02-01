#morse.py -- Generates ITU-Standard morse code (in bit format) from ASCII text.
#MIT License -- Copyright (c) Philip Conrad 2013, all rights reserved.

import time #used for testing later.


morseITUStandard = {
    "a" : [1, 0, 1,1,1], #dot dash
    "b" : [1,1,1, 0, 1, 0, 1, 0, 1], #dash dot dot dot
    "c" : [1,1,1, 0, 1, 0, 1,1,1, 0, 1], #dash dot dash dot
    "d" : [1,1,1, 0, 1, 0, 1], #dash dot dot
    "e" : [1], #dot
    "f" : [1, 0, 1, 0, 1,1,1, 0, 1], #dot dot dash dot
    "g" : [1,1,1, 0, 1,1,1, 0, 1], #dash dash dot
    "h" : [1, 0, 1, 0, 1, 0, 1], #dot dot dot dot
    "i" : [1, 0, 1], #dot dot
    "j" : [1, 0, 1,1,1, 0, 1,1,1, 0, 1,1,1], #dot dash dash dash
    "k" : [1,1,1, 0, 1, 0, 1,1,1], #dash dot dash
    "l" : [1, 0, 1,1,1, 0, 1, 0, 1], #dot dash dot dot
    "m" : [1,1,1, 0, 1,1,1], #dash dash
    "n" : [1,1,1, 0, 1], #dash dot
    "o" : [1,1,1, 0, 1,1,1, 0, 1,1,1], #dash dash dash
    "p" : [1, 0, 1,1,1, 0, 1,1,1, 0, 1], #dot dash dash dot
    "q" : [1,1,1, 0, 1,1,1, 0, 1, 0, 1,1,1], #dash dash dot dash
    "r" : [1, 0, 1,1,1, 0, 1], #dot dash dot
    "s" : [1, 0, 1, 0, 1], #dot dot dot
    "t" : [1,1,1], #dash
    "u" : [1, 0, 1, 0, 1,1,1], #dot dot dash
    "v" : [1, 0, 1, 0, 1, 0, 1,1,1], #dot dot dot dash
    "w" : [1, 0, 1,1,1, 0, 1,1,1], #dot dash dash
    "x" : [1,1,1, 0, 1, 0, 1, 0, 1,1,1], #dash dot dot dash
    "y" : [1,1,1, 0, 1, 0, 1,1,1, 0, 1,1,1], #dash dot dash dash
    "z" : [1,1,1, 0, 1,1,1, 0, 1, 0, 1], #dash dash dot dot

    "1" : [1, 0, 1,1,1, 0, 1,1,1, 0, 1,1,1, 0, 1,1,1], #dot dash dash dash dash
    "2" : [1, 0, 1, 0, 1,1,1, 0, 1,1,1, 0, 1,1,1], #dot dot dash dash dash
    "3" : [1, 0, 1, 0, 1, 0, 1,1,1, 0, 1,1,1], #dot dot dot dash dash
    "4" : [1, 0, 1, 0, 1, 0, 1, 0, 1,1,1], #dot dot dot dot dash
    "5" : [1, 0, 1, 0, 1, 0, 1, 0, 1], #dot dot dot dot dot
    "6" : [1,1,1, 0, 1, 0, 1, 0, 1, 0, 1], #dash dot dot dot dot
    "7" : [1,1,1, 0, 1,1,1, 0, 1, 0, 1, 0, 1], #dash dash dot dot dot
    "8" : [1,1,1, 0, 1,1,1, 0, 1,1,1, 0, 1, 0, 1], #dash dash dash dot dot
    "9" : [1,1,1, 0, 1,1,1, 0, 1,1,1, 0, 1,1,1, 0, 1], #dash dash dash dash dot
    "0" : [1,1,1, 0, 1,1,1, 0, 1,1,1, 0, 1,1,1, 0, 1,1,1], #dash dash dash dash dash

    " " : [0,0,0,0,0,0,0] #inter-word gap
}


def toMorse(inString):
    out = []
    sourceText = inString.lower()
    sourceText = list(sourceText) #explode string into list of characters
    prevChar = " "

    for c in sourceText:
        if c in morseITUStandard.keys():
            if prevChar != " ":
                out += [0,0,0] #inter-letter gap
            out += morseITUStandard[c]
            prevChar = c
    
    return out


if __name__ == '__main__':    
    #use the system bell character, '\a' to beep on 1 digits.
    telegraph = []
    for x in toMorse("SOS"):
        if x == 1:
            telegraph += "\a"
        else:
            telegraph += " "

    #play our tune on the command line:
    for x in telegraph:
        time.sleep(0.5)
        print x