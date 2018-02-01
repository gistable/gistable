def unicode_it(data):
    # Take a string of data and convert it to unicode
    try:
        return unicode(data, errors="replace").strip()
    except TypeError as E:
        return u""

def extract(msg, msg_obj, attachments):
    if msg.is_multipart():
        for part in msg.get_payload():
            if part.is_multipart():
                extract(part, msg_obj, attachments)
                continue
            if part.get('Content-Disposition') is None:
                msg_obj["body"] += unicode_it(part.get_payload())
            else:
                if part.get('Content-Disposition').startswith('attachment'):
                    attachments[part.get_filename()] = {
                            'data': part.get_payload(decode=True),
                            'mime': part.get_content_type()
                        }
    else:
        msg_obj["body"] += unicode_it(msg.get_payload())
    return

mail_directory = "maildir"

mdir = mailbox.Maildir(mail_directory, factory=email.message_from_file)

for directory in mdir.list_folders():
    d = mdir.get_folder(directory)
    for msg in d:
        msg_obj = {"path": directory, "body": ""}
        attachments = {}
        for key, value in msg.items():
            msg_obj[key.lower()] = unicode_it(value)
        lists = ["from", "cc", "bcc", "to"]
        extract(msg, msg_obj, attachments)
        # Add your own handler to do things with the message
        # if attachments:
        #    for fname, data in attachments.items():
        #        Add your own handler to do things with the attachments