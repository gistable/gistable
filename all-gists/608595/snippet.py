'''Manager-based polymorphic model inheritance.

This module provides a non-intrusive approach for accessing polymorphically
instances of a model hierarchy. Non-intrusive means:
  - It does not require extending a custom ``Model`` base class or metaclass.
  - It does not require a ``ForeignKey`` to ``ContentType`` or the ``contenttypes``
    app in general. Instead the real class of an instance is determined based on
    the value (**polymorphic identity**) of a user-specified discriminating field
    (**polymorphic on**).
  - It does not override the default (or any other) model ``Manager`` (unless
    explicitly shadowed). Standard (non-polymorphic) managers and querysets can
    be still available.
  - It does not have "magic" hidden side effects.

A single :func:`polymorphic_manager` function is exported. To use it:

1. Create a polymorphic manager on the parent Model of the hierarchy::

    from polymorphic import polymorphic_manager

    class Player(models.Model):
        hitpoints = models.PositiveIntegerField(default=100)

        # polymorphic_on field
        race = models.SmallIntegerField(choices=enumerate(['Elf', 'Troll', 'Human']))

        # keep the default (non-polymorphic) manager
        objects = models.Manager()

        # a new manager polymorphic on Player.race
        objects_by_race = polymorphic_manager(on=race)

        def __unicode__(self):
            return u'Player(%s)' % self.pk

2. Create a polymorphic manager (usually default) on each child Model by
   calling the :meth:`.polymorphic_identity` method of the parent polymorphic
   manager and specifying the polymorphic identity for this model::

    class Elf(Player):
        bows = models.PositiveIntegerField(default=0)

        # polymorphic manager for race=0
        objects = Player.objects_by_race.polymorphic_identity(0)

        def __unicode__(self):
            return u'Elf(%s)' % self.pk

    class Troll(Player):
        axes = models.PositiveIntegerField(default=0)

        # polymorphic manager for race=1
        objects = Player.objects_by_race.polymorphic_identity(1)

        def __unicode__(self):
            return u'Troll(%s)' % self.pk

   Proxy models work too::

    class Human(Player):

        # polymorphic manager for race=2
        objects = Player.objects_by_race.polymorphic_identity(2)

        class Meta:
            proxy = True

        def __unicode__(self):
            return u'Human(%s)' % self.pk

3. And that's all, you can access instances polymorphically or non polymorphically::

    def test():
        from random import choice

        # create a bunch of random type players
        for i in xrange(10):
            choice([Elf, Troll, Human]).objects.create()

        # retrieval through the polymorphic manager returns instances of the right class
        print "Automatically downcast players:", Player.objects_by_race.all()

        # retrieval through default Player manager returns Player instances as usual
        players = Player.objects.all()
        print "Non-downcast players:", players

        # but they cast be explicitly downcast to the right class
        print "Explicitly downcast players:", map(Player.objects_by_race.downcast, players)

        # retrieving the instances of a specific class works as expected
        print "Elfs:", Elf.objects.all()
        print "Trolls:", Troll.objects.all()
        print "Humans:", Human.objects.all()

    >>> test()
    Automatically downcast players: [<Troll: Troll(1)>, <Human: Human(2)>, <Human: Human(3)>, <Elf: Elf(4)>, <Human: Human(5)>, <Troll: Troll(6)>, <Troll: Troll(7)>, <Human: Human(8)>, <Troll: Troll(9)>, <Elf: Elf(10)>]
    Non-downcast players: [<Player: Player(1)>, <Player: Player(2)>, <Player: Player(3)>, <Player: Player(4)>, <Player: Player(5)>, <Player: Player(6)>, <Player: Player(7)>, <Player: Player(8)>, <Player: Player(9)>, <Player: Player(10)>]
    Explicitly downcast players: [<Troll: Troll(1)>, <Human: Human(2)>, <Human: Human(3)>, <Elf: Elf(4)>, <Human: Human(5)>, <Troll: Troll(6)>, <Troll: Troll(7)>, <Human: Human(8)>, <Troll: Troll(9)>, <Elf: Elf(10)>]
    Elfs: [<Elf: Elf(4)>, <Elf: Elf(10)>]
    Trolls: [<Troll: Troll(1)>, <Troll: Troll(6)>, <Troll: Troll(7)>, <Troll: Troll(9)>]
    Humans: [<Human: Human(2)>, <Human: Human(3)>, <Human: Human(5)>, <Human: Human(8)>]
'''

__all__ = ['polymorphic_manager']

from itertools import imap
from django.db.models import Manager
from django.db.models.signals import pre_init
from django.core.exceptions import ImproperlyConfigured


def polymorphic_manager(on):
    '''Create a model Manager for accessing polymorphic Model instances.

    :param on: The field used to determine the real class of a model instance.
    '''
    # This creates a thin wrapper class around PolymorphicParentManager. There
    # are two reasons for not using PolymorphicParentManager directly:
    # 1. Preserve the __init__ signature. Regular Manager.__init__ doesn't take
    #    arguments but PolymorphicParentManager has to take the polymorphic_on
    #    field. This breaks code that attempts to subclass it and call the
    #    super __init__.
    # 2. Make all manager instances for this field share the same _id2model
    #    mapping. This is necessary, for example, to support polymorphic "related
    #    managers" at the other side of a ForeignKey or both sides of a
    #    ManyToManyField.
    parent = PolymorphicParentManager(on)
    class PolymorphicManager(PolymorphicParentManager):
        def __init__(self):
            PolymorphicParentManager.__init__(self, on, parent._id2model)
    return PolymorphicManager()


class PolymorphicParentManager(Manager):
    '''Polymorphic Manager for the parent Model of a hierarchy.

    All Manager methods that return model instances (``all``, ``iterator``,
    ``get``, ``create``, ``get_or_create``, etc.) automatically downcast them to
    the right class. Downcasting can be also done explicitly on any model
    instance using the :meth:`downcast` method.
    '''

    def __init__(self, on, id2model=None):
        '''Instantiate a new PolymorphicParentManager.

        :param on: The field used to determine the real class of a model instance.
        :param id2model: An optional mapping of each polymorphic identity to the
            respective Model subclass.
        '''
        super(PolymorphicParentManager, self).__init__()
        self._field = on
        if id2model is None:
            id2model = {}
        self._id2model = id2model

    @property
    def polymorphic_on(self):
        '''The name of the field this manager is polymorphic on.'''
        return self._field.name

    def polymorphic_identity(self, identity, autoinit=True):
        '''Create a polymorphic Manager for the given ``identity``.

        :param identity: The value of the :attr:`polymorphic_on` field.
        :param autoinit: If True (default), a ``pre_init`` signal handler is
            connected to the Model of the newly created manager, that sets the
            :attr:`polymorphic_on` field to ``identity`` (unless an explicit
            identity is passed). Usually there is no reason to set this to False.
        '''
        return PolymorphicChildManager(self, identity, autoinit)

    def downcast(self, obj, _hit_db=True):
        '''Return an instance having the real class of ``obj``.

        If ``obj`` is already an instance of the real class it is returned as
        is, otherwise a new instance is returned.

        :param obj: A model instance.
        :param _hit_db: Mainly for internal usage, if unsure leave it to True.
            Long answer: If ``obj`` has a primary key and its real model class
            is not a proxy, normally the database should be queried for it. In
            case it is known in advance that ``obj`` is not in the database,
            or if the full ``obj`` state is not important, pass ``_hit_db=False``
            to save a database roundtrip.
        '''
        polymorphic_value = getattr(obj, self.polymorphic_on)
        model = self._id2model.get(polymorphic_value, obj.__class__)
        if model is obj.__class__: # or polymorphic value is unknown
            return obj
        if _hit_db and obj.pk is not None and not model._meta.proxy:
            try:
                return model._default_manager.get(pk=obj.pk)
            except model.DoesNotExist:
                pass
        cast_obj = model(pk=obj.pk)
        # XXX: dumping the whole obj.__dict__ as a way to copy the state is
        # not foolproof but that's probably the best we can do
        cast_obj.__dict__.update(obj.__dict__)
        return cast_obj

    def get_query_set(self):
        queryset = super(PolymorphicParentManager, self).get_query_set()
        # blend the super queryset's class with the DowncastingQuerySetMixin
        queryset_subclass = DowncastingQuerySetMixin._get_subclass_with(queryset.__class__)
        # and return a clone of the queryset having the blended class
        # also pass the downcast bound method required by DowncastingQuerySetMixin
        return queryset._clone(klass=queryset_subclass, downcast=self.downcast)


class PolymorphicChildManager(Manager):
    '''Polymorphic manager for the children Models of a hierarchy.

    Querysets created by this manager are filtered to return only objects with
    the polymorphic identity value of the manager.
    '''

    def __init__(self, polymorphic_manager, identity, autoinit=True):
        super(PolymorphicChildManager, self).__init__()
        self._polymorphic_manager = polymorphic_manager
        self._identity = identity
        self._autoinit = autoinit

    def downcast(self, obj, _hit_db=True):
        return self._polymorphic_manager.downcast(obj, _hit_db)
    downcast.__doc__ = PolymorphicParentManager.downcast.__doc__

    def contribute_to_class(self, cls, name):
        super(PolymorphicChildManager, self).contribute_to_class(cls, name)
        polymorphic_on = self._polymorphic_manager.polymorphic_on
        identity = self._identity
        id2model = self._polymorphic_manager._id2model
        if identity in id2model:
             raise ImproperlyConfigured(
                'More than one subclasses with the same identity (%s.%s=%s)' %
                (self._polymorphic_manager.model.__name__, polymorphic_on, identity))
        id2model[identity] = cls
        if self._autoinit:
            def preset_identity(sender, args, kwargs, **_):
                if polymorphic_on not in kwargs:
                    kwargs[polymorphic_on] = identity
            pre_init.connect(preset_identity, sender=cls, weak=False)

    def get_query_set(self):
        cond = {self._polymorphic_manager.polymorphic_on: self._identity}
        return super(PolymorphicChildManager, self).get_query_set().filter(**cond)


class DowncastingQuerySetMixin(object):
    '''Mixin class to be used along with a QuerySet class for automatic downcasting.

    Instances must have a ``downcast`` method with the signature of
    :meth:`PolymorphicParentManager.downcast`.
    '''

    def iterator(self):
        return imap(self.downcast, super(DowncastingQuerySetMixin, self).iterator())

    def create(self, **kwargs):
        # make a clone of this queryset but replace self.model with the real one
        # we don't care about the full instance state, we just need the class
        cast_obj = self.downcast(self.model(**kwargs), _hit_db=False)
        clone = self._clone(model=cast_obj.__class__)
        return super(DowncastingQuerySetMixin, clone).create(**kwargs)

    def get_or_create(self, **kwargs):
        obj_created = super(DowncastingQuerySetMixin, self).get_or_create(**kwargs)
        if obj_created[1]:
            # the real-class object is not in the db, so don't hit it again
            cast_obj = self.downcast(obj_created[0], _hit_db=False)
            cast_obj.save(force_insert=True, using=self.db)
            obj_created = cast_obj, obj_created[1]
        # else get() has already downcast it; nothing else to do
        return obj_created

    def _clone(self, **kwargs):
        kwargs['downcast'] = self.downcast  # propagate the downcast callable
        return super(DowncastingQuerySetMixin, self)._clone(**kwargs)

    # mapping of a Queryset (sub)class to a subclass of it with DowncastingQuerySetMixin
    _cached_subclasses = {}

    @classmethod
    def _get_subclass_with(cls, qset_cls):
        if issubclass(qset_cls, cls):
            return qset_cls     # already a DowncastingQuerySetMixin subclass
        try:
            return cls._cached_subclasses[qset_cls]
        except KeyError:
            sub_cls = type(cls.__name__ + qset_cls.__name__, (cls, qset_cls), {})
            cls._cached_subclasses[qset_cls] = sub_cls
            return sub_cls
