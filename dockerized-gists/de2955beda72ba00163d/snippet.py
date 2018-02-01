from __future__ import division
import math
import re
import collections
import bisect
import sys

si_prefix_unordered = {
    'y': 1e-24,  # yocto
    'z': 1e-21,  # zepto
    'a': 1e-18,  # atto
    'f': 1e-15,  # femto
    'p': 1e-12,  # pico
    'n': 1e-9,   # nano
    'u': 1e-6,   # micro
    'm': 1e-3,   # mili
    'k': 1e3,    # kilo
    '' : 1,      # None
    'M': 1e6,    # mega
    'G': 1e9,    # giga
    'T': 1e12,   # tera
    'P': 1e15,   # peta
    'E': 1e18,   # exa
    'Z': 1e21,   # zetta
    'Y': 1e24,   # yotta
}
si_prefix = collections.OrderedDict(sorted(si_prefix_unordered.items(), key = lambda x : x[1]))
si_prefix_inverted = { v : k for k, v in si_prefix.items() }

def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect.bisect_right(a, x)
    if i:
        return a[i-1]
    raise ValueError

def si_adjustment(value):
    try:
        adjustment = find_le(si_prefix.values(), value)
        return (si_prefix_inverted[adjustment], value / adjustment)
    except ValueError:
        return ('y', value / si_prefix['y'])

argregex_str = r'(\d+(\.\d+)?)(.*)'
argregex = re.compile(argregex_str)
units = ['o', 'v', 'a', 'w']
def argstring_to_dict(argstring):
    """convert strings of the form

    3.2v 6a
    3.2v 10w
    ...etc

    to a dictionary with keys of the unit type and values of the values
    """
    result = {}

    tokens = argstring.split()
    for token in tokens:
        m = argregex.match(token)
        if m is None:
            raise ValueError("'%s' is not of the form %s" % (token, argregex_str))
        value = m.group(1)
        suffix = m.group(3)
        if len(suffix) == 1:
            prefix = None
            suffix = suffix.lower()
        elif len(suffix) == 2:
            prefix = suffix[0]
            suffix = suffix[1].lower()
        elif len(suffix) > 2:
            raise ValueError("Unrecognized suffix '%s' (please use single letter suffixes e.g. 'o', 'a', 'v', 'w')" % suffix)
        if prefix is not None and prefix not in si_prefix:
            raise ValueError("Unrecognized SI prefix '%s'" % prefix)
        if suffix not in units:
            raise ValueError("token suffix '%s' not recognized" % suffix)
        if suffix in result:
            raise ValueError("Duplicate value for '%s'" % suffix)
        
        if prefix is not None:
            result[suffix] = float(value) * si_prefix[prefix]
        else:
            result[suffix] = float(value)
    
    if len(result) != 2:
        raise ValueError('Improper amount of arguments')

    return result

def solve_for_ohms(argdict):
    if 'v' in argdict and 'a' in argdict:
        volts = argdict['v']
        amps = argdict['a']
        return volts / amps
    elif 'w' in argdict and 'a' in argdict:
        watts = argdict['w']
        amps = argdict['a']
        return watts / amps ** 2
    elif 'w' in argdict and 'v' in argdict:
        watts = argdict['w']
        volts = argdict['v']
        return volts ** 2 / watts
    else:
        raise ValueError('Invalid arguments for solving ohms')

def solve_for_amps(argdict):
    if 'v' in argdict and 'o' in argdict:
        volts = argdict['v']
        ohms = argdict['o']
        return volts / ohms
    elif 'w' in argdict and 'o' in argdict:
        watts = argdict['w']
        ohms = argdict['o']
        return math.sqrt(watts / ohms)
    elif 'w' in argdict and 'v' in argdict:
        watts = argdict['w']
        volts = argdict['v']
        return watts / volts
    else:
        raise ValueError('Invalid arguments for solving watts')

def solve_for_volts(argdict):
    if 'a' in argdict and 'o' in argdict:
        amps = argdict['a']
        ohms = argdict['o']
        return amps * ohms
    elif 'w' in argdict and 'o' in argdict:
        watts = argdict['w']
        ohms = argdict['o']
        return math.sqrt(watts * ohms)
    elif 'w' in argdict and 'a' in argdict:
        watts = argdict['w']
        amps = argdict['a']
        return watts / amps
    else:
        raise ValueError('Invalid arguments for solving volts')

def solve_for_watts(argdict):
    if 'v' in argdict and 'a' in argdict:
        volts = argdict['v']
        amps = argdict['a']
        return volts * amps
    elif 'v' in argdict and 'o' in argdict:
        volts = argdict['v']
        ohms = argdict['o']
        return volts ** 2 / ohms
    elif 'a' in argdict and 'o' in argdict:
        amps = argdict['a']
        ohms = argdict['o']
        return amps ** 2 * ohms
    else:
        raise ValueError('Invalid arguments for solving watts')

# if willie is available, register commands with willie
try:
    from willie import web
    import willie.module

    @willie.module.commands('o')
    @willie.module.commands('ohm')
    @willie.module.commands('ohms')
    @willie.module.example('.ohms 5a 1v')
    @willie.module.example('.ohms 5w 1a')
    @willie.module.example('.ohms 5w 5v')
    @willie.module.example('.ohms 5Mw 5v')
    def ohms(bot, trigger):
        argstring = trigger.group(2)
        try:
            args = argstring_to_dict(argstring)
            result = solve_for_ohms(args)
            si, value = si_adjustment(result)
            bot.reply('%.02f%so' % (value, si))
        except ValueError as e:
            bot.reply('invalid command')
    
    @willie.module.commands('a')
    @willie.module.commands('amp')
    @willie.module.commands('amps')
    @willie.module.example('.amps 5v 1o')
    @willie.module.example('.amps 5w 1v')
    @willie.module.example('.amps 10v 5o')
    @willie.module.example('.amps 1v 5mo')
    def amps(bot, trigger):
        argstring = trigger.group(2)
        try:
            args = argstring_to_dict(argstring)
            result = solve_for_amps(args)
            si, value = si_adjustment(result)
            bot.reply('%.02f%sa' % (value, si))
        except ValueError as e:
            bot.reply('invalid command')

    @willie.module.commands('w')
    @willie.module.commands('watt')
    @willie.module.commands('watts')
    @willie.module.example('.watts 5v 1o')
    @willie.module.example('.watts 5a 25o')
    @willie.module.example('.watts 5a 10v')
    @willie.module.example('.watts 5mA 10mV')
    def watts(bot, trigger):
        argstring = trigger.group(2)
        try:
            args = argstring_to_dict(argstring)
            result = solve_for_watts(args)
            si, value = si_adjustment(result)
            bot.reply('%.02f%sw' % (value, si))
        except ValueError as e:
            bot.reply('invalid command')

    @willie.module.commands('v')
    @willie.module.commands('volt')
    @willie.module.commands('volts')
    @willie.module.example('.volts 10w 5a')
    @willie.module.example('.volts 10w 10o')
    @willie.module.example('.volts 5a 10o')
    @willie.module.example('.volts 5kA 10Mo')
    def volts(bot, trigger):
        argstring = trigger.group(2)
        try:
            args = argstring_to_dict(argstring)
            result = solve_for_volts(args)
            si, value = si_adjustment(result)
            bot.reply('%.02f%sv' % (value, si))
        except ValueError as e:
            bot.reply('invalid command')

except ImportError:
    print 'WARNING: willie not found'

def ohms_cmdline(argstring):
    try:
        args = argstring_to_dict(argstring)
        result = solve_for_ohms(args)
        si, value = si_adjustment(result)
        print '%.02f%so' % (value, si)
    except ValueError as e:
        print e.message

def volts_cmdline(argstring):
    try:
        args = argstring_to_dict(argstring)
        result = solve_for_volts(args)
        si, value = si_adjustment(result)
        print '%.02f%sv' % (value, si)
    except ValueError as e:
        print e.message

def amps_cmdline(argstring):
    try:
        args = argstring_to_dict(argstring)
        result = solve_for_amps(args)
        si, value = si_adjustment(result)
        print '%.02f%sa' % (value, si)
    except ValueError as e:
        print e.message

def watts_cmdline(argstring):
    try:
        args = argstring_to_dict(argstring)
        result = solve_for_watts(args)
        si, value = si_adjustment(result)
        print '%.02f%sw' % (value, si)
    except ValueError as e:
        print e.message

def main():
    argstring = ' '.join(sys.argv[2:])
    if sys.argv[1] == '.w' or sys.argv[1] == '.watt' or sys.argv[1] == '.watts':
        watts_cmdline(argstring)
    elif sys.argv[1] == '.o' or sys.argv[1] == '.ohm' or sys.argv[1] == '.ohms':
        ohms_cmdline(argstring)
    elif sys.argv[1] == '.a' or sys.argv[1] == '.amp' or sys.argv[1] == '.amps':
        amps_cmdline(argstring)
    elif sys.argv[1] == '.v' or sys.argv[1] == '.volt' or sys.argv[1] == '.volts':
        volts_cmdline(argstring)
    else:
        print 'Invalid arguments'

if __name__ == '__main__':
    main()
