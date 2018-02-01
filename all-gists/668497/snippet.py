def merge(list1, list2):
    result = []
    index1 = index2 = 0
    while index1 < len(list1) and index2 < len(list2):
        key1 = list1[index1]
        key2 = list2[index2]
        if key1 <= key2:
            result.append(key1)
            index1 += 1
        else:
            result.append(key2)
            index2 += 1
            
    if index1 < len(list1): result += list1[index1:]
    elif index2 < len(list2): result += list2[index2:]
    return result


def merge_sort(keys):
    if len(keys) < 2: return keys
    else:
        middle = len(keys)/2
        list1 = keys[:middle]
        list2 = keys[middle:]
        sorted1 = merge_sort(list1)
        sorted2 = merge_sort(list2)
        return merge(sorted1, sorted2)