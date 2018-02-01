from pelican import signals

"""
Neighbor Articles Plugin for Pelican
====================================

Adds ``next_article`` (newer) and ``prev_article`` (older) variables
to the articles context

Usage:
------

    <ul>
    {% if article.prev_article %}
        <li>
            <a href="{{ SITEURL }}/{{ article.prev_article.url}}">
                {{ article.prev_article.title }}
            </a>
        </li>
    {% endif %}
    {% if article.next_article %}
        <li>
            <a href="{{ SITEURL }}/{{ article.next_article.url}}">
                {{ article.next_article.title }}
            </a>
        </li>
    {% endif %}
    </ul>
"""

def iter3(seq):
    it = iter(seq)
    nxt = None
    cur = next(it)
    for prv in it:
        yield nxt, cur, prv
        nxt, cur = cur, prv
    yield nxt, cur, None

def neighbors(generator):
    for nxt, cur, prv in iter3(generator.articles):
        cur.next_article = nxt
        cur.prev_article = prv

def register():
    signals.article_generator_finalized.connect(neighbors)