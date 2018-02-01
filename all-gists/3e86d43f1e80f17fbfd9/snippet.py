def track_field_changes(only=None, exclude=()):
    """
    Django models decorator for tracking fields changes

        :only: fields to track for changes (all otherwise)
        :exclude: fields to exclude from tracking

    Adds to model instance:
        get_old_value(field_name) — old value of given field
        is_changed(field_name=None) — is any field (or given field) is changed
        changed_fields — changed fields dictionary with old values { field_name: old_value }
        update_if_changed — context manager that updates object only if it changed inside context

    [Warning!] Do not works with instances obtained with only()/defer(), because no post_init thrown

    Example:
        @track_field_changes()
        class Post(models.Model):
            user = models.ForeignKey(User)        
            is_published = models.BooleanField(...)

        # Variant one: update posts counter only if post created or is_published changed
        @receiver(post_save, sender=Post)
        def update_user_posts_count(cls, sender, instance, created, **kwargs):
            post, user = instance, instance.user
            if created or post.is_changed('is_published'):
                published_old = not created and post.get_old_value('is_published') == True
                published_new = post.is_published
                user.count_posts += int(published_new) - int(published_old)
                user.save()
                    
        # Alternative: update posts counter only if it changes
        @receiver(post_save, sender=Post)
        def update_user_posts_count(cls, sender, instance, created, **kwargs):            
            with user.update_if_changed(['count_posts']):
                published_old = not created and post.get_old_value('is_published') == True
                published_new = post.is_published
                user.count_posts += int(published_new) - int(published_old)                    
    """
    def get_field_value(obj, field_name):
        """Returns field value by field name"""
        field = obj._meta.get_field(field_name)
        return getattr(obj, field.get_attname())

    def make_tracking_fields_list(obj):
        """Generate list of model fields for tracking"""
        if only:
            return only
        else:
            return [field.name for field in obj._meta.local_fields if field.name not in exclude]

    def make_fields_snapshot(obj, fields):
        """Make fields snapshot {field: value}"""
        return {field: get_field_value(obj, field) for field in fields}

    def store_fields(obj, update_fields=None):
        u"""Store or update snapshot of tracking fields"""
        if not update_fields:
            obj.__fields_snapshot = make_fields_snapshot(obj, make_tracking_fields_list(obj))
        else:
            obj.__fields_snapshot.update(make_fields_snapshot(obj, update_fields))

    def compare_with_snapshot(obj, snapshot):
        """Compare fields snapshot with current obj fields and returns dict {field: old_value}"""
        return {
            field: old_value
            for field, old_value in snapshot.iteritems()
            if old_value != get_field_value(obj, field)
        }

    def decorator(cls):
        # To store old values
        cls.__fields_snapshot = {}

        def get_old_value(self, field):
            """Returns old value of given field"""
            return self.__fields_snapshot.get(field)
        cls.get_old_value = get_old_value

        def is_changed(self, field=None):
            """
            Returns True if given field was changed
            If fields is excluded from tracking returns False always
            If field is not specified returns True if any tracking field was changed
            """
            tracking_fields = self.__fields_snapshot.keys()
            if field and field not in tracking_fields:
                return False
            else:
                return any(
                    self.get_old_value(f) != get_field_value(self, f)
                    for f in ([field] if field else tracking_fields)
                )
        cls.is_changed = is_changed

        def get_changed_fields(self):
            """Returns changed fields as dict {field: old_value}"""
            return compare_with_snapshot(self, self.__fields_snapshot)
        cls.get_changed_fields = get_changed_fields
        cls.changed_fields = property(get_changed_fields, doc="Get changed fields dict {field_name: old_value, ...}")

        @contextmanager
        def update_if_changed(self, fields=None, commit=True, update_changed_only=False):
            """
            Context manager for update object only if given (or all tracked) fields was changed

            *fields* list of fields to track for changes or all default fields if None.
            If no changes in given fields inside context, no save occur

            *commit* if False nothing happens, useful for create model methods with 'commit' argument
            fields = [] has same effect

            *update_changed_only* if True django update_fields will be used for update only changed in context fields
            WARNING! It can brake logic with auto-calculated fields on pre-save

            Example:
                with post.update_if_changed(['title', 'description']):
                    post.title = get_new_title()
            """
            tracking_fields = make_tracking_fields_list(self) if fields is None else fields
            if not tracking_fields or not commit:
                yield
            else:
                # Make new fields snapshot
                fields_snapshot = make_fields_snapshot(self, tracking_fields)
                yield
                changed_fields = compare_with_snapshot(self, fields_snapshot).keys()
                if changed_fields:
                    if update_changed_only:
                        self.save._original(self, update_fields=changed_fields)
                        # Update snapshot
                        self.__fields_snapshot.update(make_fields_snapshot(self, changed_fields))
                    else:
                        self.save()

        cls.update_if_changed = update_if_changed

        # Store field values on init
        def _post_init(sender, instance, **kwargs):
            store_fields(instance)
        models.signals.post_init.connect(_post_init, sender=cls, weak=False)

        # Reset stored fields on save
        def save(self, *args, **kwargs):
            save._original(self, *args, **kwargs)
            # Check update_fields param!
            store_fields(self, kwargs.get('update_fields', None))
        save._original = cls.save
        cls.save = save

        return cls

    return decorator