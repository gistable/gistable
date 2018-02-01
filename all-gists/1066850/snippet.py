class IS_EMAIL_LIST(object):
    def __init__(self, error_message="Email %s is invalid", sep=","):
        self.error_message = error_message
        self.sep = sep
        
    def __call__(self, value):
            emails = value.strip().replace('\n','').replace('\t','').split(self.sep)
            for email in emails:
                email = email.strip()
                if IS_EMAIL()(email)[1] != None:
                    return (email, self.error_message % email)
            return (emails, None)     

db.define_table('emails',
                Field('list','text', requires=IS_EMAIL_LIST())
                )