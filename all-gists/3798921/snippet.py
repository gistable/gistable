    def _update_write(values):
        def function(self, cr, uid, ids, context=None):
            return self.write(cr, uid, ids, values, context=context)
        return function

    confirm_cb = _update_write({'state' : 'confirmed'})
    cancel_cb = _update_write({'state' : 'cancelled'})