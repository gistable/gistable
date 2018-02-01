import enum


class Choices(type(enum.Enum)):

    def __new__(metacls, cls, bases, classdict):
        temp = type(classdict)()
        names = set(classdict._enum_names)

        for k in classdict._enum_names:
            v = classdict[k]

            if v is Ellipsis:
                v = k

            if isinstance(v, (list, tuple)):
                v = tuple([k if x is Ellipsis else x for x in v])

            temp[k] = v

        for k, v in classdict.items():
            if k not in names:
                temp[k] = v

        # Add the __getitem__ we need to make this enum work for Django choices
        if "__getitem__" not in temp:
            temp["__getitem__"] = lambda self, idx: [self.value, self.display][idx]

        if "__len__" not in temp:
            temp["__len__"] = lambda self: 2

        return super(Choices, metacls).__new__(metacls, cls, bases, temp)

    @staticmethod
    def _find_new(classdict, obj_type, first_enum):
        def new(enum_class, db, display=None):
            real_new, save_new, use_args = type(enum.Enum)._find_new(
                                                                classdict,
                                                                obj_type,
                                                                first_enum,
                                                            )

            if not use_args:
                enum_item = real_new(enum_class)
                enum_item._value = db
            else:
                enum_item = real_new(enum_class, db)
                if not hasattr(enum_item, "_value"):
                    enum_item._value = obj_type(db)

            # Add the _display attribute
            enum_item.display = display if display is not None else db

            return enum_item

        return new, False, True


class Contact(models.Model):

    class Types(enum.Enum, metaclass=Choices):
        author = ...
        maintainer = "maintainer"
        individual = ("individual", "Individual")
        organisation = (..., "Organisation")

    type = models.CharField(_("Type"), max_length=150, choices=Types)

    name = models.TextField(_("Name"))
    email = models.EmailField(_("Email"), max_length=254, blank=True)
    url = URLTextField(_("URL"), blank=True)