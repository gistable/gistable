from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

'''
In this example, create usermodel who use email and password for login.
Don't forget to add in settings.py:

AUTH_USER_MODEL='your_app.UserModel' 

'''

class UserModelManager(BaseUserManager):
	def create_user(self, email, password, pseudo):
		user = self.model()
		user.pseudo = pseudo
		user.email = self.normalize_email(email=email)
		user.set_password(password)
		user.save()
		
		return user

	def create_superuser(self, email, password):
		'''
		Used for: python manage.py createsuperuser
		'''
		user=self.model()
		user.pseudo = 'admin-yeah'
		user.email = self.normalize_email(email=email)
		user.set_password(password)
		
		user.is_staff = True
		user.is_superuser = True
		user.save()
		
		return user


class UserModel(AbstractBaseUser, PermissionsMixin):
	## Personnal fields.
	email = models.EmailField(max_length=254, unique=True)
	pseudo = models.CharField(max_length=16)
	## [...]
	
	## Django manage fields.
	date_joined = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	
	USERNAME_FIELD = 'email'
	REQUIRED_FIELD = ['email', 'pseudo']
	
	objects = UserModelManager() 

	def __str__(self):
		return self.email
		
	def get_short_name(self):
		return self.pseudo[:2].upper()
	
	def get_full_name(self):
		return self.pseudo