print("##########################################################")
print("\n Welcome to my file text encrypter/decrypter!")
print("Made using python ;)")
print("Usage: type encrypt to encrypt a file with providing a seed")
print("Usage: type decrypt to decrypt a file\'s contents if you have the correct seed")
print("##########################################################\n")
chars = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j', 11: 'k', 12: 'l', 13: 'm',
         14: 'n', 15: 'o', 16: 'p', 17: 'q', 18: 'r', 19: 's', 20: 't', 21: 'u', 22: 'v', 23: 'w', 24: 'x', 25: 'y',
         26: 'z',27: '',28: " ", 29: 0, 30: 1, 31: 2,32: 3,33: 4,34:5,35:6,36:7,37:8,38:9,39:'\n'}
charz = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12, 'm': 13,
         'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25,
         'z': 26,'':27,' ':28,0:29,1:30,31:2,32:3,33:4,34:5,35:6,36:7,37:8,38:9,'\n':39}
decid = input("would you like to encrypt or decrypt a file?: ")
if decid.lower() == 'encrypt':
    filepath = input("Enter a file path to be decrypted: ")
    seed = int(input("enter a seed: ")) % 27
    newstring = ''
    num = 0

    with open(filepath, 'r') as ftbe:
        text = ftbe.read()
        txtlst = list(text)
        for char in txtlst:
            if char in txtlst:
                global num
                num = charz.get(char)
                if num == None:
                    num = 10
                global seed
                if num > seed:
                    numnm = abs(num - seed)
                    if numnm >38:
                        numnm += 27
                    else:
                        mynewlist = []
                        mynewlist.append(chars.get(numnm))
                        for character in mynewlist:
                            global newstring
                            newstring = newstring + str(character)
                else:
                    if char != None:
                        newstring += str(char)
            else:
                if char != None:
                    newstring += str(char)

    with open(filepath, 'w') as f:
        f.write(newstring)
elif decid == 'decrypt':
    filepath = input("Enter a file path to be decrypted: ")
    seed = int(input("enter a seed: ")) % 27
    newstring = ''
    num = 0

    with open(filepath, 'r') as ftbe:
        text = ftbe.read()
        txtlst = list(text)
        for char in txtlst:
            if char in txtlst:
                global num
                num = charz.get(char)
                if num == None:
                    num = 10
                global seed
                if num > seed:
                    numnm = abs(num + seed)
                    if numnm >38:
                        numnm -= 27
                    else:
                        mynewlist = []
                        mynewlist.append(chars.get(numnm))
                        for character in mynewlist:
                            global newstring
                            newstring = newstring + str(character)
                else:
                    if char != None:
                        newstring += str(char)
            else:
                if char != None:
                    newstring += str(char)
                    newstring -= 'o'

    with open(filepath, 'w') as f:
        f.write(newstring)
else:
    print('you didn\'t enter anything')