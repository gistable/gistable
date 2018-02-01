from django.db import models
from django.db.models.signals import post_init

# Generic models...

class Note(models.Model):
    note = models.TextField()


class TimeLog(models.Model):
    time_spent = models.DecimalField(max_digits=4, decimal_places=2)
    notes = models.ManyToManyField(Note, blank=True)
    
    @property
    def init_track_fields(self):
        return ('time_spent',)
    
    def add_track_save_note(self):
        field_track = {}
        for field in self.init_track_fields:
            value = getattr(self, field)
            orig_value = getattr(self, '_original_%s' % field)
            if value != orig_value:
                field_track[field] = [orig_value, value]

        if field_track:
            note_str = 'The following fields were updated:<br /><br />'
            for k, v in field_track.iteritems():
                note_str += ('<b>{field}:</b> <i>{orig_value}</i> '
                             '<b>&rarr;</b> {value}<br />').format(
                    field=k,
                    orig_value=v[0],
                    value=v[1],
                )

            note = Note.objects.create(note=note_str)
            self.notes.add(note)
    
    def save(self, *args, **kwargs):
        add_track = bool(self.pk)
        super(TimeLog, self).save(*args, **kwargs)

        if add_track:
            self.add_track_save_note()


# Signal connector function
def timelog_post_init(sender, instance, **kwargs):
    if instance.pk:
        for field in instance.init_track_fields:
            setattr(instance, '_original_%s' % field, getattr(instance, field))


# Attach signal to the function
post_init.connect(
    timelog_post_init,
    sender=TimeLog,
    dispatch_uid='grinch.signals.timelog_post_init',
)