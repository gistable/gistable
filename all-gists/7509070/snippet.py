def longest_common_prefix(str1, str2):
    result = ''
    for i in range(len(str1)):
        if(len(str2) > i and str1[i] == str2[i]):
            result = result + str1[i]
        else:
            break
    return result

def longest_common_substring(str1, str2):
    max = 0; position = -1
    for i in range(len(str1)):
        char = str1[i]
        for j in range(len(str2)):
            if(str2[j] == char):
                length = len(longest_common_prefix(str1[i:],str2[j:]))
                if(length > max): 
                    max = length
                    position = i
                    
    if position == -1: return ''                
    return str1[position: position+max]

print longest_common_substring("kjueabcdefklop","128abcdef9lop")