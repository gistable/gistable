def cycle_key(self):
    #TODO: Errors here will tank the system, probably need some better handling...
    old_session_key = self.session_key
    old_session = Session.objects.get(session_key=old_session_key)
    try:
        cart = Cart.objects.get(session=old_session)
        super(SessionStore, self).cycle_key()
        new_session_key = self.session_key
        new_session = Session.objects.get(session_key=new_session_key)
        cart.session = new_session
        cart.save()
        logger.debug('Migrated cart from session %s to %s' %(old_session_key, new_session_key))
    except Cart.DoesNotExist:
        logger.debug('Session %s does not have a cart to migrate' %(old_session_key))
        # @strogonoff points out that we don't care about losing the association between
        # the session and cart when we encounter Cart.DoesNotExist.  But we should probably be cycling
        # key
        super(SessionStore, self).cycle_key()
        