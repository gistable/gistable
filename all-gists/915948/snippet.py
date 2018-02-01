###
#   This field is used on the user model to transparently add stuff from the
#   user profile object into the user resource.
#
#   Copyright (c) 2012 Colin Sullivan <colinsul [at] gmail.com>
#   Licensed under the MIT License.
###
class UserProfileManyToManyField(fields.ManyToManyField):
    ###
    #   We will override the dehydrate method so when we're trying to dehydrate
    #   the attribute, if it fails we can check to see if the attribute is in
    #   the user profile instead.
    ###
    def dehydrate(self, bundle):
        try:
            # Use parent's dehydrate method initially
            result = super(UserProfileManyToManyField, self).dehydrate(bundle)
            # If it worked than this attribute was in the User model.
            return result
        except AttributeError:
            # If there was an attribute error, try using our user profile instead
            result = super(UserProfileManyToManyField, self).dehydrate(
                # Create a new bundle with our user profile object instead
                Bundle(obj = bundle.obj.get_profile())
            )
            # If it worked, than the attribute was in the `ConcertUser` model.  If
            # the above line throws an error, then the attribute did not exist in 
            # the `User` model or the `ConcertUser` model.
            return result

class UserResource(MyResource):
    # unreadEvents is actually on the user profile model
    unreadEvents = UserProfileManyToManyField(
        'concertapp.event.api.EventResource',
        'unreadEvents'
    )
    
    class Meta:
        queryset = User.objects.all()
        authentication = DjangoAuthentication()
        authorization = ConcertAuthorization()
        fields = ['id', 'username',]
