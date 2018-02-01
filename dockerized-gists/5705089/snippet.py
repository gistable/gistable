import re
leading_tab_re = re.compile('^(\t+)')

class ReindentingMiddleware(object):
    def process_response(self, request, response):
        return response
        if not response['Content-Type'].startswith('text/html'):
            return response
        content = response.content
        lines = content.split('\n')
        fixed_lines = []
        current_indent = 0
        for line in lines:
            if not line.strip():
                continue
            m = leading_tab_re.match(line)
            if m is not None:
                num_tabs = len(m.group(1))
                if num_tabs > current_indent:
                    current_indent += 1
                elif num_tabs < current_indent:
                    current_indent -= 1
                line = leading_tab_re.sub('\t' * current_indent, line)
            fixed_lines.append(line)
        response.content = '\n'.join(fixed_lines)
        return response
