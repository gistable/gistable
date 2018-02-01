alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Rotor():
    perms = []
    turnover_position = ''
    position = 'A'
    def __init__(self, perms, turnover_position, ring_setting):
        i = alphabet.index(ring_setting)
        perms = perms[i:] + perms[:i]
        self.perms = [c for c in perms]
        self.turnover_position = turnover_position
        
    def set_position(self, position):
        position_change = alphabet.index(position) - alphabet.index(self.position)
        self.position = position
        self.perms = self.perms[position_change:] + self.perms[:position_change]
        
    def turnover(self):
        return True if self.turnover_position == self.position else False
    
    def step(self):
        turnover = self.turnover()
        self.perms = self.perms[1:] + self.perms[:1]
        self.position = alphabet[(alphabet.index(self.position) + 1) % 26]
        if turnover:
            return True
        else:
            return False
    
    def encrypt_forward(self, c):
        return self.perms[alphabet.index(c)]
    
    def encrypt_backward(self, c):
        return alphabet[self.perms.index(c)]
    
class Reflector():
    def __init__(self, pairs):
        self.pairs = {}
        for i, c in enumerate(alphabet):
            self.pairs[c] = pairs[i]
    
    def reflect(self, c):
        return self.pairs[c]
    

class Machine():
    rotors = []
    reflector = None
    plug_board = {}
    double_step = False
    
    def __init__(self, rotors, reflector, plug_board):
        self.rotors = [Rotor(rotor[0], rotor[1], rotor[2]) for rotor in rotors]
        self.reflector = Reflector(reflector)
        for pair in plug_board:
            self.plug_board[pair[0]], self.plug_board[pair[1]] = pair[1], pair[0]
            
    def set_rotors(self, positions):
        if len(positions) != len(self.rotors):
            print 'Error: rotor settings do not match with number of rotors' 
        else:
            [rotor.set_position(positions[i]) for i, rotor in enumerate(self.rotors)]
        return
    
    def encrypt_char(self, c):
        c = self.plug_board[c] if c in self.plug_board else c
        for i, rotor in enumerate(self.rotors[::-1]):
            if i is 0:
                c = rotor.encrypt_forward(c)
            else:
                difference = (alphabet.index(self.rotors[::-1][i-1].position) - alphabet.index(self.rotors[::-1][i].position)) % 26
                c = rotor.encrypt_forward(alphabet[alphabet.index(c) - difference])
            print c
        difference = alphabet.index(self.rotors[0].position)
        c = self.reflector.reflect(c)
        print '\n'
        print c
        print '\n'
        for i, rotor in enumerate(self.rotors):
            if i is 0:
                c = rotor.encrypt_backward(c)
            else:
                difference = (alphabet.index(self.rotors[i-1].position) - alphabet.index(self.rotors[i].position)) % 26
                print difference
                c = rotor.encrypt_backward(alphabet[alphabet.index(c) - difference])
            print c
        c = self.plug_board[c] if c in self.plug_board else c
        return c
    
    def status(self):
        return self.rotors[0].position + self.rotors[1].position + self.rotors[2].position
    
    def step(self):
        if self.double_step:
            self.rotors[1].step()
            self.rotors[0].step()
            self.double_step = False
        if self.rotors[2].step():
            self.rotors[1].step()            
            if self.rotors[1].turnover():
                self.double_step = True
                
    def encrypt(self, s):
        out = ''
        for c in s:
            self.step()
            out += self.encrypt_char(c)
        return out
        
        
    
    
    
def test():
    rotors=[('ESOVPZJAYQUIRHXLNFTGKDCMWB', 'J', 'G'),
            ('AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E', 'M'),
            ('VZBRGITYUPSDNHLXAWMJQOFECK', 'Z', 'Y')]
    reflector = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'
    plug_board = [('D', 'N'), ('G', 'R'), ('I', 'S'), ('K', 'C'), ('Q', 'X'), ('T', 'M'), ('P', 'V'), ('H', 'Y'), ('F', 'W'), ('B', 'J')]

    
    machine = Machine(rotors, reflector, plug_board)
    return machine
