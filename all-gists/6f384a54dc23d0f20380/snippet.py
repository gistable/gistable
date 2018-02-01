def gen_data():
    a = 1983
    po = pow(2, 32)
    while True:
        yield a % 10000 + 1
        a = (a * 214013 + 2531011) % po


def do_case(k, n):
    head = gen_data().next
    tail = gen_data().next
    cnt = hi = 0
    csum = head()
    while True:
        if csum <= k:
            if csum == k:
                cnt += 1
            hi += 1
            if hi == n:
                break
            csum += head()
        else:
            csum -= tail()
    return cnt


if __name__ == "__main__":
    c = int(raw_input())
    for i in range(c):
        k, n = [int(v) for v in raw_input().split()]
        print do_case(k, n)
