def github(query, url):
    url = "https://github.com/%s/issues" % url
    # Direct to issue number
    try:
        redirect("%s/%s" % (url, int(query)))
    except ValueError:
        # New ticket
        if query == "new":
            redirect("%s/new" % url)
        # Issue list
        elif query == "":
            redirect(url)
        # Phrase search
        else:
            redirect("%s/search?q=%s" % (url, query))

# Fabric tickets
def cmd_fab(query):
    github(query, "fabric/fabric")