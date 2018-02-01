# Program to Add Binary Numbers without inbuilt functions. 

dec_num = []

class NUMtoDEC():
    """ This Class will Convert Binary to Decimal """
    def __init__(self, num):
        self.num = num
        self.lenth = len(num)
    def num_dec(self):
        dec = 0
        count = 1
        j = self.lenth - 1
        
        while count <= self.lenth:
            for i in self.num:
                a = int(i)*(2**j)
                dec = dec + a
                j -= 1
                count += 1 
        dec_num.append(dec)
        print "\nBinary of %s to Decimal is %s\n" %(''.join(str(i) for i in self.num), dec)
        
class ADDnumDEC():
    """ This Class will ADD the Decimal Numbers """
    def __init__(self, dec_num):
        self.dec_num = dec_num
    def add_num_dec(self):
        add = 0
        if len(self.dec_num)>=1:
            
            for i in self.dec_num:
                add = int(i) + add
        return add
    
class DECtoBIN():
    """ This Class will Convert Decimal to Binary """
    def __init__(self, add_dec):
        self.add_dec = add_dec
    def con_dec_to_bin(self):
        add = self.add_dec
        b = add // 2
        c = []
        while b >=1:
            a = add%2
            b = add // 2
            add = b
            c.append(a)

        d = c[::-1]
        str1 = ''.join(str(e) for e in d)
        print "Binary Addition is : ", str1
        
# Taking input
i = 1
j = int(raw_input("Number of Binary Numbers to ADD ? "))
while i <= j:
    num_dec = NUMtoDEC(list(raw_input("Enter Number%s Binary Number : "%i)))
    num_dec.num_dec()
    i += 1


add_num_dec = ADDnumDEC(dec_num)
add_dec = add_num_dec.add_num_dec()
print "Decimal Addition is : ", add_dec 
add_num_bin = DECtoBIN(add_dec)
add_num_bin.con_dec_to_bin()

                # END OF PROGRAM #
