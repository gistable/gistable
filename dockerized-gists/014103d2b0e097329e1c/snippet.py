from passlib.apps import custom_app_context as pwd_context

class User(db.Model):
    # ... 

    def set_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)