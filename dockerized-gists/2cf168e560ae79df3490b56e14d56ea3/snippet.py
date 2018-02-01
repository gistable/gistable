def solve(words=None):
    if not words or not isinstance(words, list):
        words = []
        a = None
        while(True):
            a = raw_input('input word (type q when ended):')
            if a!='q':
                words.append(a)
            else:
                break
    words = sorted(words)
    
    print_words(words)
    
    while(len(words) > 1):
        check(words)
        print_words(words)
        
       
def check(words):
    selected_index = int(raw_input('which word(index):'))
    selected_word = words[selected_index]
    print(selected_word)
    
    precise_count = raw_input('precision:')
    
    n = int(precise_count)
    
    remove_words = []
    if n==0:    
        for w in words:
            for i, character in enumerate(selected_word):
                if w[i] == character:
                    remove_words.append(w)
                    break
    else:
        for w in words:
            same_count = 0
            for i, character in enumerate(selected_word):
                if w[i] == character:
                    same_count+=1
            if same_count != n:
                remove_words.append(w)
    for r in remove_words:
        try:
            words.remove(r)
        except ValueError as e:
            print("error : cannot remove {}".format(r))
    
    
def print_words(words):        
    for i, w in enumerate(words):
        print(i, w)
    print('---------')
    
if __name__=='__main__':
    solve()
    