class ABBADiv1:
    def canObtain(self, initial, target):
        def AddChar(s):
            if len(s) == len(target):
                return s == target
            if s not in target and s not in rev_target:
                return False
            return AddChar(s + 'A') or AddChar((s + 'B')[::-1])
        rev_target = target[::-1]
        return "Possible" if AddChar(initial) else "Impossible"