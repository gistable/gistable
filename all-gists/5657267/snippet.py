def not_in_student_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to 
    authenticated users who are not in the "Student" group."""
    return user.is_authenticated() and not user.groups.filter(name='Student').exists()


# Use the above with:
@user_passes_test(not_in_student_group, login_url='/elsewhere/')
def some_view(request):
    # ...


# Another, less verbose, option:
def not_student(function=None):
  actual_decorator = user_passes_test(
    lambda u: u.is_authenticated() and not user.groups.filter(name='Student').exists()
  )
  return actual_decorator(function)


# Use the above with:
@not_student
def some_view(request):
    # ...