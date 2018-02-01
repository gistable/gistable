def check_sudoku(grid, p_info = False, gridsize = 9):
    '''sudoku checker - enter True as second func. argument
        to print more info
        about check failures'''

    def check_sudoku_complete_results(grid, gridsize = 9):
        if type(grid) != list: return None, 'function accepts list, got %s instead' % (str(type(grid)))

        if gridsize % 3 != 0: return None, 'incorrect size'
        if len(grid) != gridsize:
            return False, 'incorrect num. rows'

        def has_nonzero_repeats(column, failure_msg = (False, '')):    
            z_c = column.count(0)    
            if z_c == 0: 
                if len(set(column)) != len(column): return failure_msg
            else:
                if len(column) != (len(set(column))+ z_c - 1):
                    return failure_msg
            return (True, 'no problems found')

        rng = range(gridsize)

        for nrow in rng:
            j = nrow
            e = grid[nrow]

            if len(e) != gridsize:
                return (None,
                'incorrect num. of col. in row %s' % (j))  
            column = []       
            for ncol in rng:
                i = e[ncol]
                k = ncol

                if type(i) != int:
                    return (
                        False,
                        'element %s in row %s is not an int'
                        % (k, j)
                        )
                if not (0 <= i <= 9):
                    return  (
                        None,
                        'element %s value in row %s is too high or low'
                        % (k, j)
                        )
                if i != 0 and e.count(i) > 1:
                    return (
                        False,
                        'element value i = %s in row %s repeats %s times'
                        % (i, j, e.count(i))
                        )

                column.append(grid[k][j])

            failure_msg = (False, 'nonzero values repeat in col.%s' % j)

            a, b = has_nonzero_repeats(column, failure_msg)
            if not a: return (a, b)

        ## some redundant iterations, but I think it's easier to read:

        for l in range(gridsize):
            if (l+3) % 3 == 0:
                for m in range(gridsize):
                    if (m+3) %3 == 0:
                        elem_square_3x3 = [grid[n][p] 
                                           for n in range(l, l + 3)
                                            for p in range(m, m + 3)]
                        failure_msg = '''small 3x3 square,
                        that starts from %sx%s
                        has repeating nonzero elements''' % (m, n)
                        has_nonzero_repeats(elem_square_3x3,
                                    failure_msg)

        return True, 'tests passed'

    state, info = check_sudoku_complete_results(grid)
    if p_info: return state, info
    return state

#############soluton part

def solve_sudoku(grid):
    if not check_sudoku(grid): return None
    solve_sudoku.solution = ''
    def same_row(i,j): return (i/9 == j/9)
    def same_col(i,j): return (i-j) % 9 == 0
    def same_block(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

    g = ''
    for e in grid:
        for i in e:
            g += str(i)

    def solve(g):
        i = g.find('0')
        if i == -1:
            #it's ugly, but it works
            solve_sudoku.solution = g
            return
        else:
            excluded_numbers = set()
            for j in range(81):
                if same_row(i,j) or same_col(i,j) or same_block(i,j):
                    excluded_numbers.add(g[j])

            for m in '123456789':
                if m not in excluded_numbers:
                    solve(g[:i]+m+g[i+1:])
    solve(g)
    try:
        out = []
        for e in range(0, 81, 9):
            s = solve_sudoku.solution[e:e+9]; print s
            out.append([]); i = e/9
            for e in s: out[i].append(int(e))
        return check_sudoku(out)
    except IndexError:
        return False