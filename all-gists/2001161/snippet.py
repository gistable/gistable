class UTCDateTime(TypeDecorator):
        impl = DateTime

        def convert_bind_param(self, value, engine):
            return value
        
        def convert_result_value(self, value, engine):
            return UTC.localize(value)

class StampedMixin(object):
    created_on = Column(UTCDateTime, default=datetime.utcnow, nullable=False)
    modified_on = Column(UTCDateTime, default=datetime.utcnow,
                         onupdate=datetime.now, nullable=False)

class TrackedMixin(object):
    @declared_attr
    def created_by_user_id(cls):
        return Column(Integer, ForeignKey('users.user_id'), nullable=False)

    @declared_attr
    def modified_by_user_id(cls):
        return Column(Integer, ForeignKey('users.user_id'), nullable=False)
    
    @declared_attr
    def created_by(cls):
        return relation(
            'User',
            primaryjoin='%s.create_user_id == User.user_id' % cls.__name__
        )
    
    @declared_attr
    def modified_by(cls):
        return relation(
            'User',
            primaryjoin='%s.modify_user_id == User.user_id' % cls.__name__
        )
