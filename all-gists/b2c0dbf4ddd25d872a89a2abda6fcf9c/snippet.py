 def do_math(x):
     print(x ** 2)
     return
 
 if __name__ == '__main__':
     i = input('Please insert an int: ')
     assert int(i), 'Not an int. terminating'
 
     i = int(i)
     result = do_math(i)
 
