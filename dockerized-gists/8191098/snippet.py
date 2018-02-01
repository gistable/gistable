def seg_access_log(line):
    delimiters = {'[': ']', '"': '"'}
    idx, start, count, delimiter, results = 0, 0, len(line), ' ', []

    while 1:
        idx = line.find(delimiter, start)
        delimiter = ' '  # reset
        if idx < 0:
            break

        if start < idx:
            results.append(line[start:idx])
        start = idx + 1
        # if idx != count - 1 and line[idx + 1] in delimiters:
        if line[idx + 1] in delimiters:
            delimiter = delimiters[line[idx + 1]]
            start += 1

    if start < count:
        results.append(line[start:].rstrip())

    return results
