# Example model
class User(Base):
    __tablename__ = 'user'
    
    @classmethod
    def _base_filters(self, obj):
        # Add this method to your model if you want base filtering, otherwise leave it out
        # import and_ from sqlalchemy package
        # this is a base filter for ALL queries
        return and_(
            obj.country == 'puerto rico',
            obj.email != 'stupid@face.com'
        )

# The custom Query
class BaseFilterQuery(Query):
    def get(self, ident):
        # Override get() so that the flag is always checked in the
        # DB as opposed to pulling from the identity map. - this is optional.
        return Query.get(self.populate_existing(), ident)

    def __iter__(self):
        return Query.__iter__(self.private())

    def from_self(self, *ent):
        # Override from_self() to automatically apply
        # the criterion to.  this works with count() and
        # others.
        return Query.from_self(self.private(), *ent)

    def private(self):
        # Fetch the model name and column list and apply model-specific base filters
        mzero = self._mapper_zero()

        if mzero:
            # Sometimes a plain model class will be fetched instead of mzero
            try:
                model = mzero.class_
                obj = mzero.class_
            except Exception as e:
                model = mzero.__class__
                obj = mzero

            if hasattr(model, '_base_filters'):
                return self.enable_assertions(False).filter(model._base_filters(obj))

        return self

# Apply to flask session
db = SQLAlchemy(app, session_options={'query_cls': BaseFilterQuery})

# Otherwise..
# sessionmaker(bind=engine, query_cls=BaseFilterQuery)