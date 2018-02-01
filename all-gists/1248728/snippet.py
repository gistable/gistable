from social_auth.backends.facebook import FacebookBackend
from social_auth.backends import google

def social_extra_values(sender, user, response, details, **kwargs):
    result = False
    
    if "id" in response:
        from apps.photo.models import Photo
        from urllib2 import urlopen, HTTPError
        from django.template.defaultfilters import slugify
        from apps.account.utils import user_display
        from django.core.files.base import ContentFile
        
        try:
            url = None
            if sender == FacebookBackend:
                url = "http://graph.facebook.com/%s/picture?type=large" \
                            % response["id"]
            elif sender == google.GoogleOAuth2Backend and "picture" in response:
                url = response["picture"]

            if url:
                avatar = urlopen(url)
                    
                photo = Photo(author = user, is_avatar = True)
                photo.picture.save(slugify(user.username + " social") + '.jpg', 
                        ContentFile(avatar.read()))
            
                photo.save()

        except HTTPError:
            pass
        
        result = True

    return result

pre_update.connect(social_extra_values, sender=None)