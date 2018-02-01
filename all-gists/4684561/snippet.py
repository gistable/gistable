from functools import wraps
from django.db import models
from django.core.exceptions import ValidationError


class ConstraintModel(models.Model):
    class Meta:
        abstract = True

    def _fill_constraints_register(self):
        cache = []
        is_callable = lambda obj, prop: hasattr(getattr(obj, prop), '__call__')

        for prop in dir(self):
            if prop.startswith('check_') and is_callable(self, prop):
                _method = getattr(self, prop)
                if getattr(_method, '_is_constraint', False):
                    cache.append(prop)
        self._constraints_register = set(cache)

    def _constraints(self):
        try:
            self._constraints_register
        except AttributeError:
            self._fill_constraints_register()
        return self._constraints_register

    constraints = property(_constraints)

    def clean(self):
        for constraint_method_name in self.constraints:
            constraint_method = getattr(self, constraint_method_name)

            if self.id:
                if constraint_method.assert_on_create:
                    constraint_method()
            else:
                if constraint_method.assert_on_update:
                    constraint_method()

        self._cleaned = True

    def delete(self, using=None):
        for constraint_method_name in self.constraints:
            constraint_method = getattr(self, constraint_method_name)

            if constraint_method.assert_on_delete:
                constraint_method()

        super(ConstraintModel, self).delete(using)

    def save(self, *args, **kwargs):
        # Do not run clean twice if was already done, but make sure it executes
        # if it have not been called

        if not hasattr(self, '_cleaned'):
            self.clean()

        # TODO: Implementar desnormalizacion de relaciones y otros campos
        # if hasattr(self, '_compute'):
        #     if hasattr(getattr(self, '_compute'), '__call__'):
        #         self._compute()

        super(ConstraintModel, self).save(*args, **kwargs)



def constraint(on_create=True, on_update=True, on_delete=False):
    def decorator(constraint_func):
        constraint_func._is_constraint = True
        constraint_func.assert_on_delete = on_delete
        constraint_func.assert_on_update = on_update
        constraint_func.assert_on_create = on_create

        @wraps(constraint_func)
        def _wrapped_method(self, **kwargs):
            res = constraint_func(self, **kwargs)

            if isinstance(res, str):
                raise ValidationError(res)

        return _wrapped_method

    return decorator


"""
Example:

  - Create a model and extend from ConstraintModel
  - Using the @constraint decorator register what tests to check
  - Return a string to raise a validation Error
"""

class Loan(ConstraintModel):
    user = models.ForeignKey('auth.User')
    amount = models.IntegerField()

    def check_amount(self):
        # Do not not lend less than 100
        if self.amount < 100:
            # Return an error.
            return 'Unable to lend less than 100$'
    check_amount._is_constraint = True
            
    @constraint()
    def check_unpaid_loans(self):
        # Do not not lend less than 100
        if self.user.total_unpaid_loans() > 1000:
            return 'Not allowed, the user has already more than 1000$ in unpaid loans.'

    @constraint()
    def check_luckyness(self):
        import random
        lucky = lambda p, m: True if m() < p else False
        if not lucky(0.2, random.random):
            return 'We are sorry, but after a detailed review we are unable to lend money to this user'
