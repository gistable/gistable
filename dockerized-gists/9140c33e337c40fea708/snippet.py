"""
To install:
    pip install click requests requests_cache

To run:
    python guess_gender.py list-of-names.txt

"""

import click
import requests
import requests_cache


requests_cache.install_cache('genderize-cache')


def genderize_url(name):
    url = 'https://api.genderize.io/?name={0}'.format(name)
    req = requests.get(url)
    return req.json()


@click.command()
@click.argument('filename')
@click.option('--misses/--show-misses', default=False)
@click.option('--debug/--no-debug', default=False)
def main(filename, misses, debug):
    missing_names = []

    with open(filename, 'r') as f:
        lines = f.read()

    names = [line for line in lines.split('\n') if len(line.strip())]
    stats = {
        'female': 0,
        'male': 0,
    }
    first_names = [name.split(' ')[0] for name in names]
    for first_name in first_names:
        info = genderize_url(first_name)
        gender = info['gender']
        if misses and gender not in ['female', 'male']:
            missing_names.append(first_name)

        if gender in stats:
            stats[gender] += 1
        else:
            stats[gender] = 1

    total_women = int(stats.get('female', 0))
    total_men = int(stats.get('male', 0))

    percent_women = float(total_women) / float(total_men + total_women) * 100
    percent_men = float(total_men) / float(total_men + total_women) * 100

    click.echo('Total women: {0} ({1:.3}%)'.format(total_women, percent_women))
    click.echo('Total men: {0} ({1:.3}%)'.format(total_men, percent_men))

    if misses:
        click.echo(', '.join(missing_names))

    if debug:
        click.echo(stats)


if __name__ == '__main__':
    main()
