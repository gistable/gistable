from annoying.decorators import ajax_request
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods

@ajax_request
@require_http_methods(["POST"])
def ajax_login(request):
  
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
      if user is not None:
          if user.is_active:
              login(request, user)
              return {"status" : "true"}
          else:
              return {"status" : "false", "reason" : "You need to activate your account. Please check your email"}
      else:
              return {"status" : "false", "reason" : "Invalid username/password"}
