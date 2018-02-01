import string, sys

def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)
 
def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError
    return x % m



p = 3490529510847650949147849619903898133417764638493387843990820577;
q = 32769132993266709549961988190834461413177642967992942539798288533;

N = p*q;

c = 96869613754622061477140922254355882905759991124574319874695120930816298225145708356931476622883989628013391990551829945157815154;

phin = (p - 1) * (q -1);
e =  9007;
d = modinv(e, phin);

m = pow(c, d, N);
letters = list(string.ascii_uppercase);
letters.insert(0, ' ');
number_string = str(m);

i = 0;
while i < len(number_string):
    k = int(number_string[i:i+2]);
    sys.stdout.write(letters[k]);
    i += 2;
print '';
