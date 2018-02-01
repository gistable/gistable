# usage:
#    IFS=$'\n' find ROOT_SOURCE_FOLDER -name "*.swift" -exec python PATH/TO/migrate.py {} \;
import sys
import re

func = re.compile('func\s+\w+\(')
param = re.compile('(?P<indent>\s*)/// -[ ]*[pP]arameter[ ]+(?P<name>\w+)[ ]*:(?P<description>[^\n]+)\n')
ret = re.compile('(?P<indent>\s*)/// -[ ]*[rR]eturns[ ]*:(?P<description>[^\n]+)\n')
continuation = re.compile('\s*///(?P<description>[^\n]+)')

def find_docstrings(lines):
    result = []
    for i, line in enumerate(lines):
        if not func.search(line):
            continue
        j = i - 1
        while j >= 0 and lines[j].strip().startswith('///'):
            j -= 1

        if j + 1 < i:
            result.append((j+1, i))
    return result

if __name__ == '__main__':
    for path in sys.argv[1:]:
        source = []
        with open(path) as source_file:
            source = source_file.readlines()
        docstring_ranges = find_docstrings(source)

        target = []
        start = 0
        for r in docstring_ranges:
            target += source[start: r[0]]

            description_ended = False
            D = 0
            P = 1
            R = 2
            stage = D
            parameter_continue = False
            description = []
            parameters = []
            returns = []
            for line in [source[i] for i in xrange(r[0], r[1])]:
                params = param.search(line)
                if params:
                    stage = P
                    parameters.append(params.groupdict())
                    continue
                rets = ret.search(line)
                if rets:
                    stage = R
                    returns.append(rets.groupdict())
                    continue

                if stage == D:
                    description.append(line)
                    continue
                else:
                    cont = continuation.search(line)
                    if cont:
                        cont_description = cont.groupdict()['description']
                        if stage == P:
                            indent = parameters[-1]['indent']
                            original_desc = parameters[-1]['description']
                            next_line = '{}///{}'.format(indent, cont_description[8:])
                            parameters[-1]['description'] = original_desc + '\n' + next_line
                        elif stage == R:
                            indent = returns[-1]['indent']
                            original_desc = returns[-1]['description']
                            next_line = '{}///{}'.format(indent, cont_description[8:])
                            returns[-1]['description'] = original_desc + ' ' + cont_description

            target += description
            if parameters:
                if len(parameters) == 1:
                    target.append("{indent}/// - Parameter {name}:{description}\n".format(**parameters[0]))
                else:
                    target.append("{}/// - Parameters:\n".format(parameters[0]['indent']))
                    for p in parameters:
                        target.append("{indent}///   - {name}:{description}\n".format(**p))
            if returns:
                target.append("{}///\n".format(returns[0]["indent"]))
                target.append("{indent}/// - Returns:{description}\n".format(**returns[0]))
            start = r[1]

        target += source[start:]

        with open(path, 'w') as target_file:
            target_file.write(''.join(target))
