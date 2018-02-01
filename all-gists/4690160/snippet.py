class Partner(models.Model):
    """
    New partner class.

    Note: 'name' and 'users' are dropped from Oscar's partner model.
    """
    user = models.OneToOneField('auth.User')

    def __unicode__(self):
        return u'%s: %s' % (_('Fulfillment Partner'),
                            self.user)

    @property
    def name(self):
        """
        Duck-typing to not break Oscar.
        """
        return unicode(self)

    @property
    def users(self):
        """
        Duck-typing to not break Oscar.
        """
        return [self.user,]

    class Meta(AbstractPartner.Meta):
        pass