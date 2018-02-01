def convert_time(struct_time): #struct_time to datetime object
    return datetime.datetime(*struct_time[:6])