def foobar(arg_string="abc", arg_list=[]): 
    print arg_string, arg_list 
    arg_string = arg_string + "xyz"
    arg_list.append("F")
 
 
for i in range(4): 
    foobar()