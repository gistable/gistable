# template.py btree.inl => btree.h, btree.out.inl

import re
import sys
import os
import os.path

if len(sys.argv) != 2:
    print "Usage: template.py <filename>"
    sys.exit(1)

filename = sys.argv[1]
base, extension = os.path.splitext(filename)

identifier_re = r"(?:[_a-zA-Z][_a-zA-Z0-9]*)"
identifier_split_re = r"(%s)" % identifier_re
directive_re = r"/// (%s)\((.*)\)\s*$" % identifier_re
comma_re = r",\s*"

template_rules = []

generated_out_filename = "%s.out%s" % (base, extension)

with open(generated_out_filename, "w") as generated_out:
    generated_out.write("// Generated from %s\n\n" % filename)
    generated_out.write('#line 1 "%s"\n' % filename)
    for line in open(filename):
        directive_match = re.match(directive_re, line)
        if directive_match:
            directive = directive_match.group(1)
            arguments = re.split(comma_re, directive_match.group(2))
            if directive == "TEMPLATE":
                template_rules.append((arguments[0], arguments[1]))
            else:
                print "Ignoring unknown directive: %s" % directive
            generated_out.write(line)
        else:
            pieces = re.split(identifier_split_re, line)
            for non_identifier, identifier in zip(pieces[::2], pieces[1::2]):
                generated_out.write(non_identifier)
                for prefix, new_prefix in template_rules:
                    if identifier.startswith(prefix):
                        generated_out.write("%s(%s)" % (prefix, identifier[len(prefix):]))
                        break
                else:
                    generated_out.write(identifier)
            generated_out.write(pieces[-1])

join_defines = """#pragma push_macro("JOIN_HELPER")
#undef JOIN_HELPER
#define JOIN_HELPER(a, b) a##b

#pragma push_macro("JOIN2")
#undef JOIN2
#define JOIN2(a, b) JOIN_HELPER(a, b)

#pragma push_macro("JOIN3")
#undef JOIN3
#define JOIN3(a, b, c) JOIN2(JOIN2(a, b), c)

#pragma push_macro("JOIN4")
#undef JOIN4
#define JOIN4(a, b, c, d, ...) JOIN2(JOIN2(JOIN2(a, b), c), d)

#pragma push_macro("JOIN")
#undef JOIN
#define JOIN(...) JOIN4(__VA_ARGS__, , , ,)

"""

join_undefines = """#pragma pop_macro("JOIN_HELPER")
#pragma pop_macro("JOIN2")
#pragma pop_macro("JOIN3")
#pragma pop_macro("JOIN4")
#pragma pop_macro("JOIN")
"""

prefix_macro_format = '#pragma push_macro("%s")\n#undef %s\n#define %s(name) JOIN2(%s, name)\n\n'

with open(base + ".h", "w") as generated_h:
    generated_h.write("// Generated from %s\n\n" % filename)
    generated_h.write(join_defines)
    macros = []
    for prefix, new_prefix in template_rules:
        generated_h.write(prefix_macro_format % (prefix, prefix, prefix, new_prefix))
        macros.append(prefix)
    generated_h.write('#include "%s"\n\n' % generated_out_filename)
    generated_h.write(join_undefines)
    for macro in macros:
        generated_h.write('#pragma pop_macro("%s")\n' % macro)
