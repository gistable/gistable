def findOdd(arr):
    index = 0
    count = 1
    last_char = arr[index]
    while(index < len(arr)):
        if(arr[index] != last_char):
            break
        count+=1
        index+=1
    count2 = 1
    last_char2 = arr[index]
    while(index < len(arr)):
        if(arr[index] != last_char2):
            break
        count2+=1
        index+=1
    if count != count2:
        count3 = 1
        last_char3 = arr[index]
        while(index < len(arr)):
            if(arr[index] != last_char3):
                break
            count3+=1
            index+=1
        if count == count3:
            return last_char2
        else:
            return last_char
    else:
        while(True):
            count2 = 1
            last_char = arr[index]
            while(index < len(arr)):
                if(arr[index] != last_char):
                    break
                count2+=1
                index+=1
            if(count2 != count):
                return last_char
            if not(index < len(arr)):
                return None
        
        