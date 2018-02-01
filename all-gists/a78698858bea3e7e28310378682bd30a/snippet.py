def kmp(text, pattern):
    partial = [0]

    for i in range(1, len(pattern)):
        j = partial[i - 1]
        while j > 0 and pattern[j] != pattern[i]:
            j = partial[j - 1]
        partial.append(j + 1 if pattern[j] == pattern[i] else j)

    ret = []
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = partial[j - 1]
        if text[i] == pattern[j]: j += 1
        if j == len(pattern):
            ret.append(i - (j - 1))
            j = 0

    return ret