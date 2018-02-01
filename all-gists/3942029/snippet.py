def isWin(board):
    """
    GIven a board checks if it is in a winning state.

    Arguments:
          board: a list containing X,O or -.

    Return Value:
           True if board in winning state. Else False
    """
    ### check if any of the rows has winning combination
    for i in range(3):
        if len(set(board[i*3:i*3+3])) is  1 and board[i*3] is not '-': return True
    ### check if any of the Columns has winning combination
    for i in range(3):
       if (board[i] is board[i+3]) and (board[i] is  board[i+6]) and board[i] is not '-':
           return True
    ### 2,4,6 and 0,4,8 cases
    if board[0] is board[4] and board[4] is board[8] and board[4] is not '-':
        return  True
    if board[2] is board[4] and board[4] is board[6] and board[4] is not '-':
        return  True
    return False


def nextMove(board,player):
    """
    Computes the next move for a player given the current board state and also
    computes if the player will win or not.

    Arguments:
        board: list containing X,- and O
        player: one character string 'X' or 'O'

    Return Value:
        willwin: 1 if 'X' is in winning state, 0 if the game is draw and -1 if 'O' is
                    winning
        nextmove: position where the player can play the next move so that the
                         player wins or draws or delays the loss
    """
    ### when board is '---------' evaluating next move takes some time since
    ### the tree has 9! nodes. But it is clear in that state, the result is a draw
    if len(set(board)) == 1: return 0,4

    nextplayer = 'X' if player=='O' else 'O'
    if isWin(board) :
        if player is 'X': return -1,-1
        else: return 1,-1
    res_list=[] # list for appending the result
    c= board.count('-')
    if  c is 0:
        return 0,-1
    _list=[] # list for storing the indexes where '-' appears
    for i in range(len(board)):
        if board[i] == '-':
            _list.append(i)
    #tempboardlist=list(board)
    for i in _list:
        board[i]=player
        ret,move=nextMove(board,nextplayer)
        res_list.append(ret)
        board[i]='-'
    if player is 'X':
        maxele=max(res_list)
        return maxele,_list[res_list.index(maxele)]
    else :
        minele=min(res_list)
        return minele,_list[res_list.index(minele)]


def test():
    assert isWin(list("XXX---OOO"))==True
    assert isWin(list('X---OO--X'))==False
    assert isWin(list('X--X--X--'))==True
    assert isWin(list('X-O-OO--X'))==False
    assert isWin(list('X-OOX--OX'))==True
    assert isWin(list('X-OOO-O-X'))==True
    assert nextMove(list('X----O-XO'),'X')==(1,2)
    assert nextMove(list('OXX---XOO'),'X')==(1,4)
    assert nextMove(list('XX---OO-O'),'X') == (1,2)
    #assert nextMove('X--OO-O--','X') ==-1
    assert nextMove(list('---------'),'X') == (0,4)
    assert nextMove(list('XXOOO-XO-'),'X') == (0,5)
    assert nextMove(list('OO-XXO-XO'),'X') == (0,2)
    assert nextMove(list('XX-OO-XO-'),'O') ==(-1,5)
    assert nextMove(list('XX--O-XOO'),'O') ==(1,2) # no chance for O to win
    return "Test cases passed"

print test()
help(nextMove)