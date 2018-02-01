import numpy
import math

# LSH signature generation using random projection
def get_signature(user_vector, rand_proj): 
    res = 0
    for p in (rand_proj):
        res = res << 1
        val = numpy.dot(p, user_vector)
        if val >= 0:
            res |= 1
    return res

# LSH signature generation using random projection (using pooled random numbers)
def get_signature_using_pool(user_vector, pool, d, m): 
    res = 0
    for proj in range(d):
        res = res << 1
        val = 0
        tmp = 17*proj
        for i,x in enumerate(user_vector):
            val += pool[(101*i+tmp) % m]*x        
        if val >= 0:
            res |= 1
    return res

# get number of '1's in binary
# running time: O(# of '1's)
def nnz(num):
    if num == 0:
        return 0
    res = 1
    num = num & (num-1)
    while num:
        res += 1
        num = num & (num-1)
    return res     

# angular similarity using definitions
# http://en.wikipedia.org/wiki/Cosine_similarity
def angular_similarity(a,b):
    dot_prod = numpy.dot(a,b)
    sum_a = sum(a**2) **.5
    sum_b = sum(b**2) **.5
    cosine = dot_prod/sum_a/sum_b # cosine similarity
    theta = math.acos(cosine)
    return 1.0-(theta/math.pi)

def run_algo(get_sig_func, user1, user2, pool, randv):
    m = len(pool)
    d = len(randv)
    if get_sig_func == 'orig':
        r1 = get_signature(user1, randv)
        r2 = get_signature(user2, randv)
    else: 
        r1 = get_signature_using_pool(user1, pool, d, m)
        r2 = get_signature_using_pool(user2, pool, d, m)
        
    xor = r1^r2
    hamming_dist = nnz(xor)
    true_sim, hash_sim = (angular_similarity(user1, user2), (d-hamming_dist)/float(d))
    try:
        diff = abs(hash_sim-true_sim)/true_sim
    except ZeroDivisionError:
        print 'true sim is zero'
        diff = float('inf')
    return diff       
        
if __name__ == '__main__':
    dim = 400 # number of dimensions per data
    d = 64 # number of bits per signature
    m = 1<<12 # random number pool size
    #numpy.random.seed(99)
    pool = numpy.random.randn(m)
    nruns = 100 # repeat times
    avg1, avg2 = 0,0
    for run in xrange(nruns):
        user1 = numpy.random.randn(dim)
        user2 = numpy.random.randn(dim)
        randv = numpy.random.randn(d, dim)
        diff1 = run_algo('orig', user1, user2, pool, randv)
        diff2 = run_algo('pool', user1, user2, pool, randv)
        avg1 += diff1; avg2 += diff2
        print "%3d, %.4f, %.4f" % (run, diff1, diff2)
    print 'avg diff' , avg1/nruns, avg2/nruns

"""
  0, 0.1979, 0.1106
  1, 0.1685, 0.0163
  2, 0.1760, 0.0809
  3, 0.1415, 0.0514
  4, 0.0371, 0.0672
  5, 0.0247, 0.0557
  6, 0.0433, 0.2285
  7, 0.1574, 0.1574
  8, 0.0298, 0.0601
  9, 0.0777, 0.1306
 10, 0.1059, 0.2212
 11, 0.0057, 0.1564
 12, 0.1366, 0.0441
 13, 0.1011, 0.0711
 14, 0.1007, 0.1636
 15, 0.0616, 0.1827
 16, 0.0871, 0.0560
 17, 0.0981, 0.2241
 18, 0.1335, 0.1729
 19, 0.1029, 0.1807
 20, 0.1945, 0.1277
 21, 0.0219, 0.1309
 22, 0.0417, 0.2458
 23, 0.0734, 0.0892
 24, 0.2275, 0.0112
 25, 0.2071, 0.0482
 26, 0.2806, 0.0768
 27, 0.0068, 0.0256
 28, 0.0087, 0.0392
 29, 0.0355, 0.0901
 30, 0.1218, 0.0664
 31, 0.1477, 0.0269
 32, 0.1348, 0.0859
 33, 0.0824, 0.0360
 34, 0.1262, 0.1574
 35, 0.0499, 0.0499
 36, 0.0460, 0.1950
 37, 0.0121, 0.0121
 38, 0.0049, 0.2059
 39, 0.0320, 0.0944
 40, 0.1110, 0.0804
 41, 0.1684, 0.0386
 42, 0.1921, 0.0341
 43, 0.1104, 0.0798
 44, 0.0791, 0.1367
 45, 0.0310, 0.2810
 46, 0.2063, 0.0160
 47, 0.1624, 0.0335
 48, 0.1581, 0.0379
 49, 0.0704, 0.0074
 50, 0.1122, 0.0466
 51, 0.0070, 0.0070
 52, 0.0717, 0.0411
 53, 0.0085, 0.0212
 54, 0.0129, 0.0178
 55, 0.0650, 0.0557
 56, 0.0144, 0.1415
 57, 0.2653, 0.1375
 58, 0.0818, 0.3681
 59, 0.1740, 0.2072
 60, 0.1088, 0.0770
 61, 0.0595, 0.1274
 62, 0.1658, 0.1178
 63, 0.1247, 0.1539
 64, 0.3327, 0.0169
 65, 0.1384, 0.0462
 66, 0.0750, 0.1076
 67, 0.0394, 0.0845
 68, 0.0536, 0.3170
 69, 0.0594, 0.0273
 70, 0.1002, 0.3084
 71, 0.1792, 0.0070
 72, 0.0879, 0.0401
 73, 0.2833, 0.0375
 74, 0.0084, 0.1306
 75, 0.0511, 0.1438
 76, 0.0061, 0.0263
 77, 0.0054, 0.1273
 78, 0.0481, 0.0154
 79, 0.3131, 0.2193
 80, 0.0995, 0.1518
 81, 0.3243, 0.0443
 82, 0.0478, 0.1791
 83, 0.2990, 0.0582
 84, 0.1532, 0.2232
 85, 0.0096, 0.1024
 86, 0.0487, 0.2367
 87, 0.1254, 0.1254
 88, 0.0892, 0.0871
 89, 0.0261, 0.1544
 90, 0.1473, 0.0354
 91, 0.0589, 0.0695
 92, 0.0819, 0.1090
 93, 0.0708, 0.0708
 94, 0.1543, 0.0637
 95, 0.0135, 0.1774
 96, 0.1840, 0.0929
 97, 0.0699, 0.0079
 98, 0.1024, 0.0394
 99, 0.0328, 0.1576
avg diff 0.103232336327 0.103529005184
"""
    