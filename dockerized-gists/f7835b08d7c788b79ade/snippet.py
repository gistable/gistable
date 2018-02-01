def remove_empty_fields(data_):
    """
        Recursively remove all empty fields from a nested
        dict structure. Note, a non-empty field could turn
        into an empty one after its children deleted.
        
        E.g,
        
        {
            "location": {
                "city": "",
                "state": None,
                "tags": []
            },
            "name": "Nick's Caffee",
            "reviews": [{}]
        } 
        
        => 
        
        {
            "name": "Nick's Caffee"
        }

        :param data_: A dict or list.
        :return: Data after cleaning.
    """
    if isinstance(data_, dict):
        for key, value in data_.items():

            # Dive into a deeper level.
            if isinstance(value, dict) or isinstance(value, list):
                value = remove_empty_fields(value)

            # Delete the field if it's empty.
            if value in ["", None, [], {}]:
                del data_[key]

    elif isinstance(data_, list):
        for index in reversed(range(len(data_))):
            value = data_[index]

            # Dive into a deeper level.
            if isinstance(value, dict) or isinstance(value, list):
                value = remove_empty_fields(value)

            # Delete the field if it's empty.
            if value in ["", None, [], {}]:
                data_.pop(index)

    return data_