

class BigForeignKey(models.ForeignKey):
    def db_type(self, connection):
        """ Adds support for foreign keys to big integers as primary keys.
        """
        rel_field = self.rel.get_related_field()
        if (isinstance(rel_field, BigAutoField) or
                (not connection.features.related_fields_match_type and
                isinstance(rel_field, (BigIntegerField, )))):
            return BigIntegerField().db_type(connection=connection)
        return super(BigForeignKey, self).db_type(connection)


class BigAutoField(models.fields.AutoField):
    def db_type(self, connection):
        if 'mysql' in connection.__class__.__module__:
            return 'bigint AUTO_INCREMENT'
        elif 'postgresql' in connection.__class__.__module__:
            return 'bigserial'
        return super(BigAutoField, self).db_type(connection)


if 'south' in settings.INSTALLED_APPS:
    add_introspection_rules([], [r"^a\.b\.c\.BigAutoField"])
    add_introspection_rules([], [r"^a\.b\.c\.BigForeignKey"])