# Caveat emptor and all of that; apologies for mistakes.

class InlineStylesTreeprocessor(Treeprocessor):
    """
    A treeprocessor that recursively applies inline styles
    to all elements of a given tree.
    """
    def __init__(self, styles):
        self.styles = styles
    
    def run(self, root):
        self.apply_styles(root)

    def apply_styles(self, element):
        for child in element:
            self.apply_styles(child)
        
        styles = self.styles.get(element.tag)
        if not styles:
            return
        
        current_styles = element.get('style', '')
        new_styles = '%s %s' % (current_styles, styles)
        element.set('style', new_styles)


class InlineStylesExtension(Extension):
    """
    A Markdown extension for adding inline styles to
    elements, by tag name.
    """
    def __init__(self, **styles):
        self.styles = styles or {}
    
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors['inline_styles'] = InlineStylesTreeprocessor(self.styles)

