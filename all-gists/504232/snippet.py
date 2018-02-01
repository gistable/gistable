import re
from jinja2 import Markup
from SOMEOTHERLIBRARYFOROTHERSTUFF import format_user_input


def strip_auth_tokens(value):
    from classlet.models import auth_token_re
    return auth_token_re.sub(u'', value)


quote_re = re.compile(ur'\s{0,4}[>|\}]')
quote_block_re = re.compile(ur'\s*----+\s*original message\s*----+$',
                            re.IGNORECASE)
quote_start_re = re.compile(ur'\s*\w.*:$')
MIN_QUOTE_LINES = 2

def _get_quotes(lines):
    quote_start = -1
    quotes = []

    lines = lines + ['']
    line = lines[0]
    for i, next_line in zip(range(len(lines)), lines[1:] + ['']):

        if quote_block_re.match(line):
            quotes.append((i, len(lines)))
            break

        if quote_re.match(line) or (quote_start_re.match(line) and
                                    quote_re.match(next_line)):
            if quote_start == -1:
                quote_start = i
        elif quote_start != -1:
            if i - quote_start >= MIN_QUOTE_LINES:
                quotes.append((quote_start, i))
            quote_start = -1

        line = next_line

    return quotes


def _enumerate_lines(value):
    value = strip_auth_tokens(value)
    lines = list(line.rstrip() for line in value.split('\n'))
    quotes = _get_quotes(lines)
    quote_state = 'outside'
    for line, i in zip(lines, range(len(lines))):
        if quotes:
            begin_quote, end_quote = quotes[0]
        else:
            begin_quote, end_quote = -1, -1
        if i == begin_quote:
            quote_state = 'begin'
        elif i == end_quote:
            quote_state = 'end'
            quotes.pop(0)
        elif quote_state == 'begin':
            quote_state = 'inside'
        elif quote_state == 'end':
            quote_state = 'outside'
        yield line, quote_state


def format_mail_web(value):
    formatted = Markup('')
    for line, quote_state in _enumerate_lines(value):
        if quote_state == 'begin':
            formatted += Markup('<div class="quote">'
                                '<a class="toggle_quote" '
                                'href="javascript:">'
                                '- show quoted text -'
                                '</a>\n'
                                '<div class="quote_body">\n')
        elif quote_state == 'end':
            formatted += Markup('</div></div>\n')
        formatted += line + Markup('<br/>\n')
    return format_user_input(formatted)


def _unquoted_lines(value):
    return (line for line, quote_state in _enumerate_lines(value)
            if quote_state == 'outside' or quote_state == 'end')


def format_mail_plain(value):
    lines = ('  ' + line for line in _unquoted_lines(value))
    return '\n'.join(lines)


def format_mail_html(value):
    return Markup('<br/>').join(_unquoted_lines(value))
