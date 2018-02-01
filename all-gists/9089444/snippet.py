from rest_framework import serializers

class HyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    This is a performance wrapper for HyperlinkedIdentityField.
    We save a ton of time by not calling reverse potentially
    thousands of times per request.
    """

    def __init__(self, *args, **kwargs):
        self.view_url = kwargs.pop("view_url", "")
        super(HyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def field_to_native(self, obj, field_name):
        return "http%s://%s%s" % (
            "s" if not settings.DEBUG else "",
            self.context["request"]._request.META["HTTP_HOST"],
            self.view_url % obj.id,
        )

# Example : 
# items = HyperlinkedIdentityField(view_url="/api/subscriptions/%s/items/",
#    view_name="subscription_item_list", pk_url_kwarg="subscription_id")
