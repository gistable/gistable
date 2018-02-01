import datetime, re, difflib

def k10(stack):
    if len(stack) <= 1:
        return

    checkHashes, checkDuplicates, checkDelta, checkName = True, True, True, True
    score, dCount, fCount, deltaScore, fnameScore, chainAverage = 65, 0, 0, 0, 0, 0
    duplicates, dChain, fChain, features = [], [], [], [ 'valid_filenames' ]

    hashMatches = [ '[0-9a-fA-F]{25}', '[0-9a-fA-F]{32}', '[0-9a-fA-F]{40}', '[0-9a-fA-F]{64}' ]

    stackLen = len(stack) -1

    for idx, item in enumerate(stack):
        if checkHashes: # if a filename appears like a hash, remove value
            for pattern in hashMatches:
                compiled = re.compile(pattern)
                if compiled.search(item['f_name']) != None:
                    checkHashes = False
                    features.remove('valid_filenames')
                    score -= 65
                    break

        if checkDuplicates: # if a user submits duplicates, add value
            check = max(item['f_hashes'], key=len)
            if not check in duplicates:
                duplicates.append(check)
            else:
                checkDuplicates = False
                features.append('duplicates')
                score += 20

        if checkDelta: # construct the delta chains
            cNode = datetime.datetime.strptime(item['s_date'],"%Y-%m-%d %H:%M:%S")
            nNode = datetime.datetime.strptime(stack[idx+1]['s_date'],"%Y-%m-%d %H:%M:%S")
            if (nNode - cNode).seconds < 86400:
                dCount += 1
            else:
                if dCount > 0:
                    dChain.append(dCount)
                    dCount = 0
            if (idx+1) == stackLen:
                if dCount > 0:
                    dChain.append(dCount)
                checkDelta = False

        if checkName: # construct the filename chains
            if difflib.SequenceMatcher(None, item['f_name'], stack[idx+1]['f_name']).ratio() > 0.75:
                fCount += 1
            else:
                if fCount > 0:
                    fChain.append(fCount)
                    fCount = 0
            if (idx+1) == stackLen:
                if fCount > 0:
                    fChain.append(fCount)
                checkName = False

    if sum(dChain) > 0:
        features.append('delta_chains')
        deltaScore = float(sum(dChain))/len(stack)
    if sum(fChain) > 0:
        features.append('filename_chains')
        fnameScore = float(sum(fChain))/len(stack)

    score += sum(dChain) + sum(fChain)

    chainAverage = float(deltaScore + fnameScore)/2

    ret = {
        'score': score, 'valid_names': checkHashes, 'duplicates': not checkDuplicates,\
        'filename_chains': fChain, 'delta_chains': dChain, 'features': features, 'representation': len(stack),\
        'delta_score': deltaScore, 'fname_score': fnameScore, 'chain_average': chainAverage
    }

    return ret