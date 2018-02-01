filter = NoteStore.NoteFilter()
filter.ascending = False

spec = NoteStore.NotesMetadataResultSpec()
spec.includeTitle = True

ourNoteList = noteStore.findNotesMetadata(authToken, filter, 0, 100, spec)

for note in ourNoteList.notes:
    print "%s :: %s" % (note.guid, note.title)