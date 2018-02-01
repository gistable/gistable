def store_pdfs_in_zip():
    docs = Dokument.all().order('updated_at')
    file_name = files.blobstore.create(mime_type='application/zip',
                                       _blobinfo_uploaded_filename='test.zip')
    with files.open(file_name, 'w') as f:
        z = blobstoreZipFile(f)
        for doc in docs.fetch(75):
            pdf = doc.data
            fname = "%s-%s.pdf" % (doc.designator, doc.updated_at)
            fname = fname.encode('ascii', 'replace')
            z.writestr(fname, pdf, date_time=doc.updated_at.timetuple()[:6])
        # Finalize ZIP file and write directory
        z.flush()
    # Finalize the file in the blobstore
    files.finalize(file_name)
    # Get the file's blob key
    blob_key = files.blobstore.get_blob_key(file_name)
