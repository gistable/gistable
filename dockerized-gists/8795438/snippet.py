import os

class Game(dict):
    def __init__(self, number_of_piecies, frontend=lambda x:None, start_column=0b001, end_column=0b100):
        super(Game, self).__init__()
        for column in [0b001, 0b010, 0b100]:
            self[column] = Column(self)
            self.frontend = frontend(self)
        for num in range(number_of_piecies,0,-1):
            Piece(num,self,0b001)    
        self.start_column=start_column
        self.end_column=end_column
    
    def start(self):
        if self.frontend:
            self.frontend.start()
        self[self.start_column][0].move_to(self.end_column)

class Column(list):
    def __init__(self, game):
        super(Column, self).__init__()
        self.game = game
        
    def pop(self, piece):
        if self[-1] != piece:
            raise Exception, "Can't remove a piece that there is another on top."
        return super(Column, self).pop()
        
    def append(self, piece):
         if self and self[-1].value < piece.value:
            raise Exception, "Can't put a larger piece on top of a smaller one."
         super(Column, self).append(piece)
    
class Piece(object):
    def __init__(self, value, game, column):
        self.value = value
        self.game = game
        self.column = column
        self.game[column].append(self)
        self.position = len(self.game[column])-1
    
    def other(self, *args):
        return ~(sum(args)) & 0b111
    
    def on_top(self):
        if len(self.game[self.column])-1 == self.position:
            return False
        return self.game[self.column][self.position+1]
    
    def move_to(self, destination):
        top_piece = self.on_top()
        if top_piece:
            other_column = self.other(self.column, destination)
            top_piece.move_to(other_column)
        self.make_move(destination)
        if top_piece:
            top_piece.move_to(destination)
    
    def make_move(self, destination):
        f,t,p = self.column, destination, self
        self.game[self.column].pop(self)
        self.game[destination].append(self)
        self.column = destination
        self.position = len(self.game[destination])-1
        if self.game.frontend:
            self.game.frontend.update(f,t,p)

class SimpleTerminalOut(object):
    def __init__(self, game):
        self.game = game
            
    def start(self):
        self.update()
        
    def update(self, f=None, t=None, p=None):
        os.system('clear')
        for column in self.game:
            print [x.value for x in game[column] ]
        os.system('sleep 1')  

  
if __name__ == "__main__":
    game = Game(7,SimpleTerminalOut)
    game.start()
