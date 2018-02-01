__author__ = 'feng'


def is_match(patten, str):
    match_index = 0
    for idx, c in enumerate(patten):
        if c == '?':
            match_index += 1
        elif c == '*':
            if idx == len(patten) - 1:
                return True

            for i in range(0, len(str) - match_index):
                if is_match(patten[idx + 1:], str[match_index + i:]):
                    return True
            return False
        else:
            if c != str[match_index]:
                return False
            match_index += 1

    if match_index != len(str):
        return False
    return True;


if __name__ == '__main__':
    failed = 0
    tests = [("ab", "abc", False),

             ("abc", "abc", True),
             ("ab?", "abc", True),
             ("ab*", "abcd", True),

             ("a*b", "addb", True),
             ("*b", "b", True),
             ("a***b", "addb", True),
             ("a*?", "addb", True),
             ("*", "ab", True),

             ("*d", "ab", False),
             ("*d*", "ab", False),
             ("?a", "ab", False),

             ("a*b", "adabdab", True),
             ("a*b", "abdb", False)]

    for patten, str, expected in tests:
        if is_match(patten, str) != expected:
            failed += 1
            print "ERROR, patten", patten, "match", str, "should", expected

    print "Failed: ", failed, "; OK: ", len(tests) - failed


