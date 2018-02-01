# Order Statistics
# Ameer Ayoub <ameer.ayoub@gmail.com>
import random, copy

# From quicksort
# Nonrandomized Pivot
def partition(l, p, q, pivot=None):
    r = copy.copy(l)
    if pivot:
        r[pivot], r[p] = r[p], r[pivot]
    x = r[p]
    i = p
    for j in range(p+1, q+1):
        print r
        if r[j] <= x:
            i += 1
            r[i], r[j] = r[j], r[i]
    r[p], r[i] = r[i], r[p]
    return r, i

#Randomized Pivot
def partition_r(l, p, q):
    random.seed()
    pivot = random.randint(p, q)
    return partition(l, p, q, pivot)

# Randomized Pivot Divide & Conquer for Order Statistics
def rand_select(A, p, q, i):
    # Base case for recursion
    if p == q:
        return A[p]
    r = partition_r(A, p, q)
    # k = the rank of the randomized partition r
    k = r[1]-p+1
    # If we found the rank we're looking for
    if i == k:
        return r[0][r[1]]
    if i < k:
        return rand_select(r[0], p, r[1], i)
    else:
        return rand_select(r[0], r[1]+1, q, i-k)

# Test
if __name__ == "__main__":
    A = [6, 10, 13, 5, 8, 3, 2, 11]
    print rand_select(A, 0, len(A)-1, 6)
