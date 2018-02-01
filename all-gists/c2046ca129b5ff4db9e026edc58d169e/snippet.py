# Hey everyone, How you all doing? Welcome to this session of Learning Python One-Step-
# At-A-Time! I think the best way to start exploring any programming language - is to
# first explore the different data types that it has to offer.

# Python, like all languages, has a number of data built-in data types - Numbers,
# Strings, Tuples, Arrays, etc. There's a lot more.

# In this short session, we'll dive into the first one: Numbers.
# Numbers are divided into a variety of different sub-types, called Integers,
# Booleans, Reals, Complex, Fractions, and Decimels.

# We're going to first have a look at Integers...

# Now the fun thing about Integers in Python is that they have unlimited range.
# This means that as long as you have virtual memory available in your allocated
# virtual environment, you're good to use an Integer number that drags on to whatever
# length you please.

# An Integer number can be either positive, negative, or a zero (0). Let's look at the
# examples below:

a = 5;      # Here, we have assigned values to two Integer variables. Let us under-
b = 4;      # stand this: Python implicitly considers a variable assigned a number
            # value as Integer, unless explicitly stated.

print('The value of A: ' + str(a));   # The 'print()' function is among the most basic functions in Python.
print('The value of B: ' + str(b));   # It outputs the value of any variable and string within it's parenthesis.
print('\n');                          # In this case, it would be 'The value of A: 5', as you will see on
                                      # running this code. Let's ignore the 'str(a)' part for now, though if you've
# worked with similar programming languages before, you should know what it is and how it works.

# Integer addition:
A_plus_B = a + b;
print('A + B = ' + str(A_plus_B));

# Integer subtraction:
A_minus_B = a - b;
print('A - B = ' + str(A_minus_B));

# Integer multiplication:
A_into_B = a * b;
print('A x B = ' + str(A_into_B));

# Integer 'true' division:
A_by_B = a / b;
print('A / B = ' + str(A_by_B));

# What you saw above was some really basic stuff you could do with positive integer numbers.
# Let's take a quick look at how negative numbers work...

# Negative Integers:
c = -3;
print('\n');
print('The value of C: ' + str(c));
d = -2;
print('The value of D: ' + str(d));
print('\n');

# Multipying negative Integers:
C_into_D = c * d; 
print('C x D = ' + str(C_into_D));

# On multiplying negative Integers, we see that the outputs are as desired. This shows that
# negative numbers can be safely used for operations.

# Let's check out some other basic stuff that Python allows us to do with numbers.

# Integer power operation:
A_squared = a ** 2;
print('\n');
print('A raised to 2 = ' + str(A_squared));

# Now, using the power operation, I'd like to demonstrate how Python provides an unrestricted
# range for the length of Integer numbers.
A_1024 = a ** 1024;
print('\n');
print('A raised to 1024 = ' + str(A_1024));
print('\n');
print('Length of the resulting number = ' + str(len(str(A_1024))));

# On running the above code, we see that the length of the number 'A raised to 1024' is 716 digits in all.
# This shows how large of an Integer number is allowed by Python.

# Let's look at a couple of more operators that Python provides us for
# working on Integers.

# Integer 'rounded off' division:
e = 9;
f = 5;
g = 2;
print('\n');
print('The value of E: ' + str(e));
print('The value of F: ' + str(f));
print('The value of G: ' + str(g));

E_by_F_true = e / f;
E_by_F_rounded_off = e // f;
print('\n');
print('E by F true = ' + str(E_by_F_true));
print('E by F rounded off = ' + str(E_by_F_rounded_off));

E_by_G_true = e / g;
E_by_G_rounded_off = e // g;
print('\n');
print('E by G true = ' + str(E_by_G_true));
print('E by G rounded off = ' + str(E_by_G_rounded_off));

# I want you to pay close attention to the above code. On running the code, you see,
# E divided by F gives us the value 1.8. But using the 'integer division' operator //,
# we see that the value of E // F is 1. Similarly, E / G = 4.5, but 4 // 5 = 4.
# So, the '//' operator divides the number and provides only the value before the decimal
# point. This is a rounding off action that rounds off to the lower limit.

# So why do I say lower limit? Check the next example using negative Integer values,
# it should clear things out. Just be careful while doing the calculations in your
# head.

h = -2;
print('\n');
print('The value of H: ' + str(h));

E_by_H_true = e / h;
E_by_H_rounded_off = e // h;
print('\n');
print('E by H true = ' + str(E_by_H_true));
print('E by F rounded off = ' + str(E_by_H_rounded_off));

# The above example works beautifully to explain why I used the words 'lower limit'.
# On running the above piece of code, we get the following outputs:
# E_by_H_true = -4.5. So the expected output for 'e // h' would be -4.
# But no. The output we get is -5. This is because on the number line, scientifically speaking,
# -5 is lower the -4.5, which in turn is lower that -4. So the operation provides an output
# settled on the lower limit. This is really important from a scientific point of view.
# Keep it in mind.

# Another fun operator is the 'Modulo operator'.
E_modulo_G = e % g;
E_modulo_F = e % f;
print('\n');
print('E modulo G = ' + str(E_modulo_G));
print('E modulo F = ' + str(E_modulo_F));

# A modulo operation divides two integers, and provides the remainder value as the output.
# For example 9 % 5 = 4. Do it in your head. Also look at 9 % 2 = 1. Yes.

# Integer truncation:
I = int(E_by_H_true);
print('\n');
print('E by H truncated = ' + str(I));

# The int() function can be used as alternative if you want to avoid the lower limit
# flooring that takes place when using the '//' operator. Remember this :)