from __future__ import print_function

if 3/2 == 1:
    input = raw_input
    range = xrange

pretty_print = True

N = int(input())

if pretty_print:
    format_str = '{:%d}' % len(str(N*N))

for i in range(N):
    for j in range(N):
        m_d = min(i, j, N-1-i, N-1-j)
        N_rel = N - 2*m_d
        v = 4*m_d*(N-m_d)
        ir = i - m_d
        jr = j - m_d

        if ir == 0:
            v += jr + 1
        elif jr == N_rel - 1:
            v += N_rel + ir
        elif jr == 0:
            v += (N_rel - 1) * 4 - ir + 1
        elif ir == N_rel - 1:
            v += (N_rel - 1) * 3 + 1 - jr
        print(format_str.format(v) if pretty_print else v, end=' ')
    print()