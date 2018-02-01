def utf8ify(value):
    if not value: return
    # remove some characters altogether
    value = re.sub(r'[?.,;/:"\'\|!@#~`+=$%^&\\*()\[\]{}<>]','',value, re.UNICODE)
    return value

def utf8ify_slugify(value):
    value = utf8ify(value)
    value = value.replace(" ", "-")
