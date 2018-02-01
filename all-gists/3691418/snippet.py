#!/usr/bin/env python
# -*- coding: utf-8 -*-

import html.parser

class ContentParser(html.parser.HTMLParser):
    def __init__(self, begin_tag, stop_tag):
        html.parser.HTMLParser.__init__(self)
        tag_temple = ('type', 'name', 'attrs', 'contains_me')
        self.begin_tag = dict(zip(tag_temple, begin_tag))
        self.begin_tag.setdefault('contains_me', False)
        self.stop_tag = dict(zip(tag_temple, stop_tag))
        self.stop_tag.setdefault('contains_me', False)
    def reset(self):
        html.parser.HTMLParser.reset(self)
        self.switch_flag = False
        self.content = ['']
    def begin_now(self):
        self.switch_flag = True
        return
    def stop_now(self):
        self.switch_flag = False
        return
    @staticmethod
    def tag_process(tag_type, target_tag, target_action, tag, attrs):
        def has_attr(match_attrs, source_attrs):
            match_dict = dict(match_attrs)
            source_dict = dict(source_attrs)
            if 'class' in match_dict:
                if 'class' in source_dict:
                    if set(str.split(match_dict.pop('class'))).issubset(set(str.split(source_dict.pop('class')))):
                        pass
                    else:
                        return False
                else:
                    return False
            return set(match_dict.items()).issubset(set(source_dict.items()))

        if target_tag['type'] == tag_type:
            if tag == target_tag['name']:
                if target_tag['attrs'] is None or len(target_tag['attrs']) == 0 or tag_type == 'endtag':
                    target_action()
                    return True
                else:
                    if len(target_tag['attrs']) > len(attrs):
                        return False
                    else:
                        if has_attr(target_tag['attrs'], attrs):
                            target_action()
                            return True
                        else:
                            return False
            else:
                return False
        else:
            return False
    def pre_tag_process(self, tag_type, tag, attrs = None):
        def get_tag_text():
            if tag_type == 'endtag':
                return '</{0}>'.format(tag)
            else:
                return self.get_starttag_text()

        if self.switch_flag == False:
            if self.tag_process(tag_type, self.begin_tag, self.begin_now, tag, attrs) == True:
                if self.begin_tag['contains_me'] == False:
                    self.content = []
                else:
                    self.content = [get_tag_text()]
                return True
            else:
                return False
        else:
            if self.tag_process(tag_type, self.stop_tag, self.stop_now, tag, attrs) == True:
                if self.stop_tag['contains_me'] == False:
                    return False
                else:
                    self.content.append(get_tag_text())
                    return True
            else:
                self.content.append(get_tag_text())
                return True
    def handle_starttag(self, tag, attrs):
        self.pre_tag_process('starttag', tag, attrs)
    def handle_endtag(self, tag):
        self.pre_tag_process('endtag', tag)
    def handle_startendtag(self, tag, attrs):
        self.pre_tag_process('startendtag', tag, attrs)
    def handle_data(self, data):
        if self.switch_flag == False:
            return False
        else:
            self.content.append(data)
            return True

def main():
    page = '<html><h1 id="q" class="a c b">Title</h1><p>Im a paragraph!</p><p>Another paragraph</p></html>'
    myparser = ContentParser(['starttag', 'h1', [('class','a b'), ('id', 'q')], True], ['endtag', 'p', None, True])
    myparser.feed(page)
    print(''.join(myparser.content))
    myparser.reset()
    print(myparser.content)

if __name__ == '__main__':
    main()