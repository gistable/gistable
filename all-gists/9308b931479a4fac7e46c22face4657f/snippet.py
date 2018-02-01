"""
Save a copy of all BBC recipes as JSON files.

Instructions:

Run this file with Python 3 in an environment with BeautifulSoup4 and requests:

virtualenv -p python3 env
source env/bin/activate
pip install requests beautifulsoup4
python recipes.py
"""

import codecs
import os
import json
import requests
import string

from bs4 import BeautifulSoup

save_directory = 'recipes'

parser = 'html.parser'
root_url = 'http://www.bbc.co.uk'

if not os.path.exists(save_directory):
  os.makedirs(save_directory)

def tryget(el):
  try:
    return el.text.strip()
  except:
    return "None"

for letter in list(string.ascii_lowercase):
  letter_page = requests.get(root_url + '/food/dishes/by/letter/' + letter)
  letter_soup = BeautifulSoup(letter_page.text, parser)
  dishes = letter_soup.find_all('li', class_='resource food')
  for dish in dishes:
    dish_link = dish.find('a').get('href')
    dish_page = requests.get(root_url + dish_link)
    dish_soup = BeautifulSoup(dish_page.text, parser)
    recipes = dish_soup.find_all('li', class_='with-image')
    for recipe in recipes:
      recipe_link = recipe.find('a').get('href')
      recipe_page = requests.get(root_url + recipe_link)
      recipe_soup = BeautifulSoup(recipe_page.text, parser)
      name = recipe_soup.find('h1', class_='content-title__text').text.strip()
      recipe_data = {
        'name': name,
        'prep_time': tryget(recipe_soup.find('p', class_='recipe-metadata__prep-time')),
        'cook_time': tryget(recipe_soup.find('p', class_='recipe-metadata__cook-time')),
        'serves': tryget(recipe_soup.find('p', class_='recipe-metadata__serving')),
        'author': {
          'name': tryget(recipe_soup.find('div', class_='chef__name')),
          'programme': tryget(recipe_soup.find('div', class_='chef__programme-name')),
        },
        'ingredients': [],
        'method': []
      }
      ingredients = recipe_soup.find_all('li', class_='recipe-ingredients__list-item')
      for ingredient in ingredients:
        recipe_data['ingredients'].append(ingredient.text.strip())
      steps = recipe_soup.find_all('li', class_='recipe-method__list-item')
      for step in steps:
        recipe_data['method'].append(step.text.strip())
      recipe_file = codecs.open(os.path.join(save_directory, name + ".json"), 'w', 'utf-8')
      recipe_file.write(json.dumps(recipe_data, ensure_ascii=False, indent=2, separators=(',', ': ')))
      recipe_file.close()
      print('Wrote recipe file for {}'.format(name))
