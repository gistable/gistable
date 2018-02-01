def hanoi(n, fr, to, spare):
    '''(int, str, str, str)

    Solve the classic puzzle Tower of Hanoi

    >>> hanoi(1, "Middle", "Left", "Right")
    - Move top ring in 'Middle' tower to the 'Left' tower        
    '''
    def print_move(fr, to):
        print "- Move top ring in '{}' tower to the '{}' tower".format(fr, to)
    
    if n == 1:
        print_move(fr, to)

    else:
        hanoi(n-1, fr, spare, to)
        hanoi(1, fr, to, spare)
        hanoi(n-1, spare, to, fr)