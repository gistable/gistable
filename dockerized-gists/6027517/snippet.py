def get_key_from_dict_by_value(dictionary, value):
    for k in dictionary:
        if dictionary[k] == value:
            return k
