# coding: utf-8

from weasyprint import HTML, CSS


def get_page_body(boxes):
    for box in boxes:
        if box.element_tag == 'body':
            return box

        return get_page_body(box.all_children())


# Main template
html = HTML('template.html')
main_doc = html.render(stylesheets=[CSS('styles.css')])

exists_links = False

# Template of header
html = HTML('header.html')
header = html.render(stylesheets=[CSS(string='div {position: fixed; top: 1cm; left: 1cm;}')])

header_page = header.pages[0]
exists_links = exists_links or header_page.links
header_body = get_page_body(header_page._page_box.all_children())
header_body = header_body.copy_with_children(header_body.all_children())

# Template of footer
html = HTML('footer.html')
footer = html.render(stylesheets=[CSS(string='div {position: fixed; bottom: 1cm; left: 1cm;}')])

footer_page = footer.pages[0]
exists_links = exists_links or footer_page.links
footer_body = get_page_body(footer_page._page_box.all_children())
footer_body = footer_body.copy_with_children(footer_body.all_children())


# Insert header and footer in main doc
for i, page in enumerate(main_doc.pages):
    if not i:
        continue

    page_body = get_page_body(page._page_box.all_children())

    page_body.children += header_body.all_children()
    page_body.children += footer_body.all_children()

    if exists_links:
        page.links.extend(header_page.links)
        page.links.extend(footer_page.links)

main_doc.write_pdf(target='main_doc.pdf')