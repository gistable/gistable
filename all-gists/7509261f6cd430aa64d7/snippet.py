def symmetric_multi_difference(list_a, list_b):
    seen = []
    result = []

    for element in list_a + list_b:
        if element in seen:
            continue
        seen.append(element)

        elements_in_a = [x for x in list_a if x == element]
        elements_in_b = [x for x in list_b if x == element]
        if len(elements_in_a) > len(elements_in_b):
            result.extend(elements_in_a[:len(elements_in_a) - len(elements_in_b)])
        elif len(elements_in_b) > len(elements_in_a):
            result.extend(elements_in_b[:len(elements_in_b) - len(elements_in_a)])

    return result


print sorted(symmetric_multi_difference(["a", "a", "b", "b"], ["a", "a", "a", "b"]))
# ['a', 'b']