# Hat tip to https://github.com/anders/pwgen for various initial documentation
# For an alternative method, check out:
# https://gist.github.com/pudquick/8d3dedc337161b187a8a1c9564c83463

import objc
from Foundation import NSBundle, NSMutableArray, NSString

SecurityFoundation = NSBundle.bundleWithPath_('/System/Library/Frameworks/SecurityFoundation.framework')
success = SecurityFoundation.load()

PASS_MIN_LENGTH  = 4
PASS_MAX_LENGTH  = 1024
PASS_MAX_REQUEST = 15

algorithm = {
             'memorable':    0,
             'random':       1,
             'letters':      2, # FIPS-181 compliant
             'alphanumeric': 3,
             'numbers':      4,
}

SFPWAContextRef = objc.createOpaquePointerType("SFPWAContextRef", b"^{_SFPWAContext=}", None)

functions = [
             ('SFPWAPolicyCopyDefault', '@'),
             ('SFPWAContextCreateWithDefaults', '^{_SFPWAContext=}'),
             ('SFPWAContextCreate', '^{_SFPWAContext=}'),
             ('SFPWAContextLoadDictionaries', 'v^{_SFPWAContext=}^{__CFArray=}I'),
             ('SFPWAPasswordSuggest', '@^{_SFPWAContext=}^{__CFDictionary=}IIII'),
             ('SFPWAPasswordEvaluator', '@^{_SFPWAContext=}^{__CFString=}I^{__CFDictionary=}'),
             ('SFPWAPolicyParse', 'v^{_SFPWAContext=}^{__CFDictionary=}'),
            ]

objc.loadBundleFunctions(SecurityFoundation, globals(), functions)

def password_languages():
    policy = SFPWAPolicyCopyDefault()
    return policy.get('Languages-Evaluate','').split(',')

def password_suggested_language():
    policy = SFPWAPolicyCopyDefault()
    return policy.get('Languages-Suggest','')

def load_dictionaries(context_ref, language_list):
    # The function is a bit picky about making sure we pass a clean NSArray with NSStrings
    langs = NSMutableArray.array()
    for x in language_list:
        langs.addObject_(NSString.stringWithString_(x))
    # The True argument is for whether the language string objects are already retained
    SFPWAContextLoadDictionaries(context_ref, langs, True)

def password_suggest(length=8, count=1, alg=None, langs=None, policy=None):
    # The default algorithm is 'memorable' which has issues at lengths beyond 32 characters, FYI
    # This will return at a max PASS_MAX_REQUEST (15) passwords at a time
    if langs is None:
        langs = [password_suggested_language()]
    else:
        available_langs = password_languages()
        for x in langs:
            if x not in available_langs:
                raise Exception('Error: unavailable language')
    if alg is None:
        alg = algorithm['memorable']
    else:
        alg = algorithm.get(alg, None)
        if alg is None:
            raise Exception('Error: unavailable algorithm')
    if policy is None:
        policy = SFPWAPolicyCopyDefault()
        context = SFPWAContextCreateWithDefaults()
    else:
        context = SFPWAContextCreate()
    SFPWAPolicyParse(context, policy)
    # Language dictionaries are used for memorable-style passwords
    load_dictionaries(context, langs)
    pass_length = max(min(PASS_MAX_LENGTH, length), PASS_MIN_LENGTH)
    pass_count  = max(min(PASS_MAX_REQUEST, count), 1)
    # The 0 argument is a null argument for callbacks
    return SFPWAPasswordSuggest(context, policy, pass_length, 0, pass_count, alg)

def password_evaluate(password, policy=None, langs=None):
    # Check out the return results of SFPWAPolicyCopyDefault() which is just a dict
    # You can build your own dict with customized rules
    # A key not present in the default policy is 'CharacterSetString' which can be
    # set to contain the legal characters allowed by the password policy
    # You can set it like: 
    #  policy = SFPWAPolicyCopyDefault()
    #  policy.update(CharacterSetString="abc123")
    if langs is None:
        langs = [password_suggested_language()]
    else:
        available_langs = password_languages()
        for x in langs:
            if x not in available_langs:
                raise Exception('Error: unavailable language')
    if policy is None:
        policy = SFPWAPolicyCopyDefault()
        context = SFPWAContextCreateWithDefaults()
    else:
        context = SFPWAContextCreate()
    SFPWAPolicyParse(context, policy)
    load_dictionaries(context, langs)
    # The 0 argument is a null argument for callbacks
    return SFPWAPasswordEvaluator(context, password, 0, policy)
