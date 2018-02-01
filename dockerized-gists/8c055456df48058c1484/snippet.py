from random import choice
from copy import deepcopy
from sys import exit

# Initial shape matrices for the five Tetrominos
shapes = [[[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
            [[1, 0, 0], [1, 0, 0], [1, 1, 0]],
            [[0, 0, 1], [0, 0, 1], [0, 1, 1]],
            [[0, 0, 1], [0, 1, 1], [0, 1, 0]], [[1, 1], [1, 1]]]


class Tetromino():
    """
    The Tetromino Class
    
    Tetrominos are the rotatatable blocks of Tetris.
    They are represented on one of: 2x2, 3x3 or 4x4 grids. #1
    
    Note that the position is specified as (col, row) on a 2D grid, 
    but its list-of-lists notation is reverse, i.e. [row][col].
    
    #1 http://tetris.wikia.com/wiki/SRS
    """
    
    def __init__(self, shape, pos_tl):
        """
        The class constructor
        
        Args:
        shape (list of lists): a 1-0 representation of the shape
        pos_tl (list(int, int)): top left position on the board
        """
        self._shape = shape
        self._tl = pos_tl

    def __repr__(self):
        """Representation: A string depicting the shape"""
        return "\n".join(["".join(["*" if j > 0 else "-" for j in i])
                            for i in self._shape])
    
    @property
    def shape(self):
        """Returns the current state of the shape """
        return self._shape
    
    @property
    def tl(self):
        """Returns the current top-left coordinate on the board"""
        return self._tl

    def set_shape(self, shape):
        "Modify the orientation of the Tetromino"
        self._shape = shape

    def set_tl(self, pos_tl):
        """Set a new top_left position"""
        self._tl = pos_tl


class Board():
    """
    The Game Board Class
    
    The board will be stored in the memory as an HxW list of lists.
    """
    def __init__(self, height = 12, width = 12):
        """
        The Board Constructor
        
        Instantiates the Board object, sets the height and widths
        params; and creates an initial grid state with all 0s.
        
        Args:
        height (int): board height as a multiple of fixed space chars
        width (int): board width as a multiple of fixed space chars
        """
        self._height = int(height)
        self._width = int(width)
        self._board = [[0] * width for i in range(height)]
        self._mino = None

    def __repr__(self):
        """Representation: String of the current board state"""
        drawing = deepcopy(self._board)
        if self._mino is not None:
            for i in range(len(self._mino.shape)):
                for j in range(len(self._mino.shape[i])):
                    if self._mino.shape[i][j] > 0:
                        drawing[self._mino.tl[1] + i][self._mino.tl[0] + j] = \
                            self._mino.shape[i][j]
        return "\n".join(["".join(["*" if j > 0 else "-" for j in i])
                            for i in drawing])

    @property
    def board(self):
        return self._board

    @property
    def width(self):
        return self._width

    @property
    def mino(self):
        return self._mino

    def set_mino(self, mino):
        self._mino = mino

class Game():
    """
    The Game Class
    
    This class will instantiate the Game and apply all moves.
    """
    def __init__(self):
        self._board = Board()
        self.new_tetromino()

    def __repr__(self):
        """Representation of the Game's Board object"""
        return self._board.__repr__()

    def new_tetromino(self):
        """
        Create a new Tetromino object
        
        Algorithm:
        1. Randomly select a shape from the shapes list.
        2. Pick a random top-left corner point on the horizontal axis.
        3. Check for any potential collisions with the grid.
        4. If there are collisions, exit the game, else continue.
        """
        mino = choice(shapes)
        # Should the position be at the center of the grid on X-axis
        # pos_tl = [int(floor((self._width - len(mino[0])) / 2.0)), 0]
        pos_tl = [choice(range(self._board.width - len(mino[0]))), 0]
        
        for i in range(len(mino)):
            for j in range(len(mino[i])):
                if mino[i][j] > 0 and \
                    self._board.board[pos_tl[1] + i][pos_tl[0] + j] == 1:
                    print self.__repr__()
                    print "Game Over!!!"
                    exit(0)
        
        self._board.set_mino(Tetromino(mino, pos_tl))

    def move_down(self):
        """
        Moves the current Tetromino down
        
        Algorithm:
        1. Return if the current Tetromino is None.
        2. Calculate the new position coordinates by shifting one row down.
        3. For blocks filled in the current Tetromino's shape:
            -- check if there is a collision, or it has hit the ground.
        4. If there is no collision or grounding:
            -- set the current Tetromino's new position.
        5. If there is a collision or grounding:
            -- add the current Tetromino's shape to the board grid.
        """
        if self._board.mino is None: return
        new_pos = [self._board.mino.tl[0], self._board.mino.tl[1] + 1]
        no_collision = True

        for i in range(len(self._board.mino.shape)):
            for j in range(len(self._board.mino.shape[i])):
                if self._board.mino.shape[i][j] > 0 and \
                    ((new_pos[1] + i) > (len(self._board.board) - 1) or 
                    self._board.board[new_pos[1] + i][new_pos[0] + j] == 1):
                    no_collision = False
                    break
            else:   # Using the very Pythonic for..else construct
                continue
            break   # Executed if else is skipped

        if no_collision:
            self._board.mino.set_tl(new_pos)
        else:
            for i in range(len(self._board.mino.shape)):
                for j in range(len(self._board.mino.shape)):
                    if self._board.mino.shape[i][j] > 0:
                        self._board.board[self._board.mino.tl[1] + i] \
                                            [self._board.mino.tl[0] +j] \
                            = self._board.mino.shape[i][j]
            self.new_tetromino()

    def move_lr(self, step):
        """
        Moves the current Tetromino left or right
        
        Algorithm is mostly same as the down movement algo.
        
        Args:
        step (signed int): negative for moving to the left, positive for right
        """
        if self._board.mino is None: return
        new_pos = [self._board.mino.tl[0] + step, self._board.mino.tl[1]]
        no_collision = True
    
        for i in range(len(self._board.mino.shape)):
            for j in range(len(self._board.mino.shape[i])):
                if (self._board.mino.shape[i][j] > 0 and
                    ((new_pos[0] + j) < 0 or
                    (new_pos[0] + j) >= (len(self._board.board[i])) or 
                    self._board.board[new_pos[1] + i][new_pos[0] + j] == 1)):
                    no_collision = False
                    break
            else:
                continue
            break

        if no_collision:
            self._board.mino.set_tl(new_pos)

    def rotate(self, angle):
        """
        Rotation of the Tetromino
        
        Algorithm:
        1. Return if the current Tetromino is None.
        2. Create a pseudo shape by rotating the current Tetromino.
            a. For clockwise rotation: i.e. by -90 degs
                -- Reverse the row order and transpose the matrix
            b. For counter clockwise rotation: i.e. by +90 degs
                -- Transpose the matrix and reverse the row order
        3. Check for conflicting geometries:
            a. If the new shape is outside the left boundary:
                -- Shift the new shape to the right
            b. If the new shape is outside the right boundary:
                -- Shift the new shape to the left
            c. If the new shape is outside the the bottom boundary
                -- Do nothing and return None
            d. If the new shape collides with an existing block
                -- Do nothing and return None
        4. If all the checks above fail:
            -- Assign the new shape to the Tetromino
        
        Args:
        angle (signed int): -1 for clockwise, 1 for counter clockwise
        """
        if self._board.mino is None or not angle in [-1, 1]: return
        if angle == 1:      # Rotate counter clockwise
            iters = range(len(self._board.mino.shape))
            t = [[self._board.mino.shape[j][i] for j in iters] for i in iters]
            new_shape = t[::-1]
        elif angle == -1:   # Rotate clockwise
            t = self._board.mino.shape[::-1]
            iters = range(len(t))
            new_shape = [[t[j][i] for j in iters] for i in iters]

        for i in range(len(new_shape)):
            for j in range(len(new_shape[i])):
                if new_shape[i][j] > 0:
                    if self._board.mino.tl[0] + j < 0:
                        self._board.mino.tl[0] += 1
                    if self._board.mino.tl[0] + j >= len(self._board.board[0]):
                        self._board.mino.tl[0] -= 1
                    if self._board.mino.tl[1] + i >= len(self._board.board):
                        return
                    if self._board.board[self._board.mino.tl[1] + i] \
                                        [self._board.mino.tl[0] + j] == 1:
                        return
        self._board.mino.set_shape(new_shape)


def print_instructions(game):
        print game
        print "Please enter a valid command: "
        print "a, d, w, s or <space> to continue"


if __name__=="__main__":
    game = Game()
    print_instructions(game)
    while True:
        for command in raw_input():
            if command == "a":
                game.move_lr(-1)
                game.move_down()
                print_instructions(game)
            elif command == "d":
                game.move_lr(1)
                game.move_down()
                print_instructions(game)
            elif command == "w":
                game.rotate(-1)
                game.move_down()
                print_instructions(game)
            elif command == "s":
                game.rotate(1)
                game.move_down()
                print_instructions(game)
            elif command == " ":
                game.move_down()
                print_instructions(game)
            else:
                print_instructions(game)