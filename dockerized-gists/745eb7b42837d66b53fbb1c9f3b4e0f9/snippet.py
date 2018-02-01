# Copies a model from one DB to another using Django
# If you're using heroku, you may wanna check https://gist.github.com/D3f0/edd70a6066863ee74674ac5ede838a20

def db_copy(obj, to, *skip, **kwargs):
    '''
    Copies a model from one database into another.
    `obj` is the model that is going to be cloned
    `to` is the db definition
    `skip` is a list of attribtues that won't be copied
    `kwargs is a list of elements that will be overwritten over model data
    returns the copied object in `to` db
    
    Use:
    db_copy(User.objects.using("mydbconn"), 'myotherdbconn', 'skip_foo', 'skip_bar', some_field=User.objects.get(...))
    
    '''
    from django.forms.models import model_to_dict
    from django.db.models import Model
    assert isinstance(obj, Model)
    data = model_to_dict(obj)
    for key in skip:
        if key in data:
            v = data.pop(key)
            print("Removing {}: {}".format(key, v))
    data.update(kwargs)
    return type(obj).objects.using(to).create(**data)

  