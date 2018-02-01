#After looking for a way to check if a model instance can be deleted in django , 
#i came across many sample, but was not working as expected. Hope this solution can help.

#Let start by creating an Abstract model class which can be inherited by other model

    class ModelIsDeletable(models.Model):
        name = models.CharField(max_length=200, blank=True, null=True, unique=True)
        description = models.CharField(max_length=200, blank=True, null=True)
        date_modified = models.DateTimeField(auto_now_add=True)
    
        def is_deletable(self):
            # get all the related object
            for rel in self._meta.get_fields():
                try:
                    # check if there is a relationship with at least one related object
                    related = rel.related_model.objects.filter(**{rel.field.name: self})
                    if related.exists():
                        # if there is return a Tuple of flag = False the related_model object
                        return False, related
                except AttributeError:  # an attribute error for field occurs when checking for AutoField
                    pass  # just pass as we dont need to check for AutoField
            return True, None
    
         class Meta:
            abstract = True



# Example
#So let say we have three model  Organization and Department and StaffType
#So many Department can be in an Organization
#And an Organization has a particular StaffType


    class StaffType(ModelIsDeletable):
    	pensionable = models.BooleanField(default=False)
    
    class Organization(ModelIsDeletable):
        staff_type = models.ForeignKey(to=StaffType)
    
    
    class Department(ModelIsDeletable):
        organization = models.ForeignKey(to=Organization, to_field="id")


#so let say after adding some information you want to remove an organization model instance
#that is already tied to a Department

#For instance we have
#Organization Table => (name = Engineering, pk = 1)
#Department Table => (name=Developer, organization_fk=1, pk=1)

#Now when you try to delete an organization after get it with the pk 

    a_org = Organization.objects.get(pk=1)

#With this at hand you can check if it deletable 

    deletable, related_obj = a_org.is_deletable()
    
    if not deletable:
    	# do some stuff with the related_obj list
    
    else:
    	# call the delete function
    	a_org.delete()