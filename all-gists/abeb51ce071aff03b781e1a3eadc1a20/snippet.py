from __future__ import print_function
import requests
import bs4
import re
headers = {
    'Referer': 'http://tyr0.chem.wsu.edu/~kipeters/basissets/alkal-nr.html',
    'Origin': 'http://tyr0.chem.wsu.edu',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
}
NUMBER = "((?:[-+]?\\d*\\.\\d+(?:[DdEe][-+]?\\d+)?)|(?:[-+]?\\d+\\.\\d*(?:[DdEe][-+]?\\d+)?))"


def pull(element, basis):
    data = [
      ('element', element),
      ('basis', basis),
      ('program', 'Gaussian'),
    ]
    r = requests.post('http://tyr0.chem.wsu.edu/~kipeters/basissets/basisform-alkal.php', data=data)
    # print(r.text)
    soup = bs4.BeautifulSoup(r.text, 'lxml').nobr     
    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.text.replace(u'\xa0', ' ').replace('!', '')
    lines = [e.strip() for e in text.splitlines() if e.strip()]
    return lines


def format(lines, element):
        
    def process_lines(lines):
        for line in lines:
            m0 = re.match(r'^BASIS=.*', line)
            m1 = re.match(r'^(%s)\s+0' % element, line)
            m2 = re.match(r'^\s*(\w+)\s*(\d+)\s*(-?\d+\.\d+)', line)
            m3 = re.match(r'^\s*' + NUMBER + '\s+' + NUMBER + '.*', line)
            m4 = re.match(r'^\*\*\*\*$', line)

            if m0:
                continue
            elif m1:
                yield m1.group(1) + '     0'
            elif m2:
                yield m2.group(1) + '   ' + m2.group(2) + '   ' + m2.group(3)
            elif m3:
                # >>> '{:20} {: }'.format('ydisp', 0.176)
                c0 = float(m3.group(1))
                c1 = float(m3.group(2))

                if float('{: 15.7f}'.format(c0)):
                    f0 = '{: 15.7f}'.format(c0)
                else:
                    f0 = '{: 15.7e}'.format(c0)

                f1 = '    {: 23.7e}'.format(c1)

                yield f0 + f1
            elif m4:
                yield line
            else:
                raise ValueError(line)

    return '\n'.join(process_lines(lines))


def pull_pw(args):
    l1 = format(pull(element=args.element, basis=args.basis.replace('wC', '')), element=args.element).splitlines()
    l2 = format(pull(element=args.element, basis=args.basis), element=args.element).splitlines()

    q1, h1 = format_into_list_of_contractions(l1, args.element)
    q2, h2 = format_into_list_of_contractions(l2, args.element)

    print(h1)
    for shell in q2:        
        if shell not in q1:
            print('\n'.join(shell))
    print('****')


def format_into_list_of_contractions(lines, element):
    basis_set = []
    contraction = None
    for line in lines:
        m1 = re.match(r'^(%s)\s+0' % element, line)
        m2 = re.match(r'^\s*(\w+)\s+(\d+)\s+(-?\d+\.\d+)', line)
        m3 = re.match(r'^\s*' + NUMBER + '\s+' + NUMBER + '.*', line)
        m4 = re.match(r'^\*\*\*\*$', line)

        if m1:
            head = line
        elif m2:
            if contraction is not None:
                basis_set.append(contraction)
            contraction = [line]
        elif m3:
            contraction.append(line)
        elif m4:
            basis_set.append(contraction)
        else:
            raise ValueError(line)

    return basis_set, head


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('element')
    p.add_argument('basis')
    args = p.parse_args()

    if 'pwC' in args.basis:
        return pull_pw(args)

    lines = pull(element=args.element, basis=args.basis)

    print(format(lines, args.element))


if __name__ == '__main__':
    main()
