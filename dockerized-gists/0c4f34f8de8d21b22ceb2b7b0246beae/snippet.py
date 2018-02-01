list_obj = [[1,2,[3]],4]
result = []
def flatten_list(input_ele, list_obj=[]):
    if isinstance(input_ele, list):
        flatten_list(input_ele, list_obj)
    else:
        list_obj.append(input_ele)
        