#!/usr/bin/env python

import pdfkit


chapters = [
  'intro',
  'linear_algebra',
  'prob',
  'numerical',
  'ml',
  'mlp',
  'regularization',
  'optimization',
  'convnets',
  'rnn',
  'guidelines',
  'applications',
  'linear_factors',
  'autoencoders',
  'representation',
  'graphical_models',
  'monte_carlo',
  'partition',
  'inference',
  'generative_models',
]


def main():
  for idx, chapter in enumerate(chapters):
    print chapter
    url = 'http://www.deeplearningbook.org/contents/%s.html'%chapter
    fname = '%02d-%s.pdf'%(idx+1, chapter)
    pdfkit.from_url(url, fname)


if __name__ == '__main__':
  main()
