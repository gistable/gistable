class Automaton:
    def __init__(self, nstates):
        self.transitions = [{} for i in range(nstates)]
        self.accept_states = [False] * nstates

    def register(self, source_state, char, target_state):
        self.transitions[source_state][char] = target_state

    def register_accept(self, state):
        self.accept_states[state] = True

    def accept(self, input):
        state = 0
        try:
            for char in input:
                state = self.transitions[state][char]
            return self.accept_states[state]
        except KeyError:
            return False
        
#to recognize "[abc]x*"
"""
       a   
      ---   --
     / b \ / |x
    0----@1--
     \ c /
      ---
"""

automaton = Automaton(2)
automaton.register(0, 'a', 1)
automaton.register(0, 'b', 1)
automaton.register(0, 'c', 1)
automaton.register(1, 'x', 1)
automaton.register_accept(1)

print automaton.accept('ax') #True
print automaton.accept('bxxx') #True
print automaton.accept('abxxx') #False
print automaton.accept('dx') #False


