def nth_percentile(dataset, percentile = 90):
    sorted_dataset = sorted(dataset)
    new_length = len(sorted_dataset) * percentile / 100
    return sorted_dataset[0:new_length]

def mean(dataset):
    return sum(dataset)/float(len(dataset))

dataset = [5, 9, 7, 101, 4, 8, 109, 104, 6, 1, 110, 106, 3, 107, 105, 2, 102, 10, 103, 108]
percentile_90 = nth_percentile(dataset)
lower_90 = min(percentile_90)
mean_90 = mean(percentile_90)
upper_90 = max(percentile_90)
sum_90 = sum(percentile_90)

print "90th percentile sorted dataset =", percentile_90
print "lower_90 =", lower_90
print " mean_90 =", mean_90
print "upper_90 =", upper_90
print "  sum_90 =", sum_90

##### This program will output:
#
# 90th percentile sorted dataset = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 101, 102, 103, 104, 105, 106, 107, 108]
# lower_90 = 1
#  mean_90 = 49.5
# upper_90 = 108
#   sum_90 = 891


