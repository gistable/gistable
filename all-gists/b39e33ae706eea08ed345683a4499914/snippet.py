class Automaton(object):
    def __init__(self):
        self.states = ["q1","q2","q3"]
        self.current_state=self.states[0]
    def read_commands(self, commands):
        for i in commands:
            if(i=="1"):
                if(self.current_state=="q1")|(self.current_state=="q3"):
                    self.current_state=self.states[1]
            else:
                if (self.current_state == "q2"):
                    self.current_state = self.states[2]
                elif(self.current_state=="q3"):
                    self.current_state = self.states[1]
        return(self.current_state=="q2")
my_automaton = Automaton()
print(my_automaton.read_commands(["0", "0", "0", "0"]))
