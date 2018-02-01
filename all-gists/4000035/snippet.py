''' Django ORM don't support to pull id from sequence by default.'''

def update_id(func):
    '''A decorator for pulling a data object's ID value out of a
       user-defined sequence.  This gets around a limitation in 
       django whereby we cannot supply our own sequence names.'''
    
    def decorated_function(*args):
        # Grab a reference to the data object we want to update.
        data_object = args[0]
        
        # Only update the ID if there isn't one yet.
        if data_object.id is None:
            # Construct the new sequence name based on the table's meta data.
            sequence_name = 'pk_%s' % data_object._meta.db_table
        
            # Query the database for the next sequence value.
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT nextval(%s)", [sequence_name])
            row = cursor.fetchone()
        
            # Update the data object's ID with the returned sequence value.
            data_object.id = row[0]
        
        # Execute the function we're decorating.
        return func(*args)
    
    return decorated_function


# Example model using the decorator to grab the ID.  Note that the ID
# is a regular integer field and that it is not displayed in the admin.
class FAQ(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.ForeignKey(FAQCategory)
    question = models.CharField(maxlength=255)
    answer = models.TextField()
    published = models.BooleanField(default=False)
    list_ordering = models.FloatField(max_digits=6, decimal_places=2, default=9999)
    
    def __str__(self):
        return self.question
    
    @update_id
    def save(self):
        # Now actually save the object.
        super(FAQ, self).save()
    
    class Meta:
        db_table = 'faqs'
    
    class Admin:
        fields = (
            (None, {'fields': ('category', 'question', 'answer', 'published', 'list_ordering')}),
        )
        list_display = ('question', 'category', 'list_ordering')