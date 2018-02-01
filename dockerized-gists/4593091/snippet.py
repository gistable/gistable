def create_for_mashup(request, mashups, filename):
    """
      request - django request object
      mashup - dict of items to mash from dlms, containin django content_type, title and link
      filename - output name
    """
    book = django_epub.EpubBook()
    book.setTitle('Dynamic Learning Maps - Resource Mashup')
    book.addCreator('Dynamic Learning Maps - https://learning-maps.ncl.ac.uk/')
    book.addMeta('date', datetime.datetime.now(), event = 'publication')
    css_path = settings.MEDIA_ROOT + 'css/epub.css'
    book.addCss(css_path, 'main.css' )
    book.addTitlePage()
    book.addTocPage()

    resources_output = ""
    resources_for_toc = []
    nodes_output = ""
    nodes_for_toc = []
    external_counter = 1

    for mashup in mashups:
        if mashup['content_type_label'] == 'resources_resource':
            mashup['anchor'] = 'r_%s' % mashup['id']
            resources_output += get_minimal_item_html(mashup)
            resources_for_toc.append({"title":mashup['title'],"anchor":mashup['anchor']})

        if mashup['content_type_label'] == 'external':
            mashup['anchor'] = 'n_e_%s' % external_counter
            resources_output += get_minimal_item_html(mashup)
            resources_for_toc.append({"title":mashup['title'],"anchor":mashup['anchor']})
            external_counter += 1

        if mashup['content_type_label'] == 'nodes_node':
            mashup['anchor'] = 'n_%s' % mashup['id']
            print_context = print_node(request,mashup['slug'],True)
            print_context['anchor'] = 'n_%s' % mashup['id']
            nodes_output += get_node_print_view_from_template(print_context)
            nodes_for_toc.append({"title":mashup['title'],"anchor":mashup['anchor']})

    soup = BeautifulSoup(nodes_output)
    nodes_output = soup.prettify() #clean the HTML, if there are any HTML errors epub readers don't work

    resources_element = book.addHtml('','resources.html',get_minimal_html('Resources','<ul>%s</ul>' % resources_output))
    book.addSpineItem(resources_element)
    n1 = book.addTocMapNode(resources_element.destPath, 'Resources')

    nodes_element = book.addHtml('','nodes.html',get_minimal_html('Maps and content','%s' % nodes_output))
    book.addSpineItem(nodes_element)
    n2 = book.addTocMapNode(nodes_element.destPath, 'Maps and content')

    for n in resources_for_toc:
        book.addTocMapNode(resources_element.destPath+'#'+n['anchor'], n['title'],parent=n1)

    for n in nodes_for_toc:
        book.addTocMapNode(nodes_element.destPath+'#'+n['anchor'], n['title'],parent=n2)

    rootDir = settings.UPLOAD_ROOT + '/%s' % filename

    book.createBook(rootDir)
    django_epub.EpubBook.createArchive(rootDir, rootDir + '.epub')

    return 'created'